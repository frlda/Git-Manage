import sys
import json
import os
import asyncio
import signal
from . import sv, MODULES_ON, MODULES_PATH, BOTNAME, log, SAMPLE
from .libraries.git_tool import GitTool
from hoshino.typing import CQEvent
from hoshino import priv
from nonebot import get_bot, on_websocket_connect

#关闭进程
async def graceful_shutdown():
    log.info("开始关闭进程...")
    loop = asyncio.get_event_loop()

    # 获取所有任务
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    log.info(f"正在取消 {len(tasks)} 个任务...")

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    log.info("所有任务已完成或取消。")

    loop.stop()

@on_websocket_connect
async def start_up(ev: CQEvent):
    bot = get_bot()
    try:
        with open(SAMPLE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    try:
        if data.get("message_id", 0) != 0:
            await bot.delete_msg(message_id=data["message_id"])
            data["message_id"] = 0
            with open(SAMPLE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        log.error("撤回失败")

    try:
        if data and data.get("reboot") == "True":
            group_id = data["group_id"]
            await bot.send_group_msg(group_id=group_id, message=(f"[{BOTNAME} 启动成功]"))
            data["reboot"] = "False"
            with open(SAMPLE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        log.error(f"发送失败：{e}")

@sv.on_fullmatch('更新全部仓库', '#更新全部仓库')
async def update_all_repos(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, "抱歉，没有权限执行此操作。")
        return
    await bot.send(ev, "开始更新所有仓库...")
    success_messages = []
    error_messages = []
    updated_repos = 0
    total_repos = len(MODULES_ON)

    for module in MODULES_ON:
        repo_path = MODULES_PATH / module
        try:
            git_tool = GitTool(str(repo_path))
            update_status = await git_tool.update_repo_async()

            if update_status["status"] == "up-to-date":
                success_messages.append(f"仓库 {module} 已是最新状态，无需更新。")
            elif update_status["status"] == "updated":
                updated_repos += 1
                commits_updated = update_status["commits_updated"]
                update_logs = await git_tool.get_update_logs_async(commits_updated)

                log_messages = "\n".join(
                    [f"{log['date']} {log['author']}: {log['message']}" for log in update_logs]
                )
                success_messages.append(
                    f"仓库 {module} 更新成功，共更新了 {commits_updated} 个提交。\n更新日志:\n{log_messages}"
                )
        except Exception as e:
            error_messages.append(f"更新仓库 {module} 时出错：{e}")

    if success_messages:
        await bot.send(ev, "\n".join(success_messages))
    if error_messages:
        await bot.send(ev, "\n".join(error_messages))

    if updated_repos > 0:
        await bot.send(ev, f"所有仓库更新完成，共更新了 {updated_repos}/{total_repos} 个仓库。")
        print(f"所有仓库更新完成，共更新了 {updated_repos}/{total_repos} 个仓库。")
        await exit_after_update(bot, ev)
    else:
        print("无已更新仓库")

@sv.on_prefix('克隆仓库', '#克隆仓库')
async def clone_repo(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return

    args = ev.message.extract_plain_text().strip().split()
    if len(args) != 1:
        await bot.send(ev, "请提供一个有效的仓库 URL。")
        return

    repo_url = args[0]
    try:
        repo_name = await GitTool.clone_repo_async(repo_url)
        await bot.send(ev, f"成功克隆仓库：{repo_url}\n仓库名：{repo_name}")
        await exit_after_update(bot, ev)
    except Exception as e:
        await bot.send(ev, str(e))

async def exit_after_update(bot, ev):
    """
    用于在更新完成后退出当前进程
    """
    try:
        with open(SAMPLE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    msg_id = await bot.send(ev, f"[{BOTNAME} 重启中...]")
    data["message_id"] = msg_id.get('message_id', None)
    data["reboot"] = "True"
    data["group_id"] = int(ev.group_id)

    os.makedirs(os.path.dirname(SAMPLE), exist_ok=True)

    try:
        with open(SAMPLE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    finally:
        await graceful_shutdown()

@sv.on_fullmatch('一键重启', 'reloading')
async def restart_bot(bot, ev: CQEvent):
    """
    手动重启机器人
    """
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, "抱歉，只有超级管理员才能执行此操作。")
        return

    await bot.send(ev, "收到重启命令，正在准备重启...")
    await exit_after_update(bot, ev)
