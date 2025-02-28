import sys
import json
import os
from . import sv, MODULES_ON, MODULES_PATH, BOTNAME, log, SAMPLE
from .libraries.git_tool import GitTool
from hoshino.typing import CQEvent
from hoshino import priv
from nonebot import get_bot
from nonebot import on_websocket_connect

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
        if data["reboot"] == "True":
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

    success_messages = []
    error_messages = []
    updated_repos = 0  # 记录有更新的仓库数量
    total_repos = len(MODULES_ON)  # 总仓库数量

    for module in MODULES_ON:
        repo_path = MODULES_PATH / module
        try:
            git_tool = GitTool(str(repo_path))
            update_status = git_tool.update_repo()

            if update_status["status"] == "up-to-date":
                success_messages.append(f"仓库 {module} 已是最新状态，无需更新。")
            elif update_status["status"] == "updated":
                updated_repos += 1  # 记录有更新的仓库
                commits_updated = update_status["commits_updated"]
                update_logs = git_tool.get_update_logs(commits_updated)

                log_messages = "\n".join([f"{log['date']} {log['author']}: {log['message']}" for log in update_logs])
                success_messages.append(
                    f"仓库 {module} 更新成功，共更新了 {commits_updated} 个提交。\n更新日志:\n{log_messages}"
                )
        except Exception as e:
            error_messages.append(f"更新仓库 {module} 时出错：{e}")

    if success_messages:
        await bot.send(ev, "\n".join(success_messages))
    if error_messages:
        await bot.send(ev, "\n".join(error_messages))

    # 判断是否需要触发重启
    if updated_repos > 0:
        await bot.send(ev, f"所有仓库更新完成，共更新了 {updated_repos}/{total_repos} 个仓库。")
        print(f"所有仓库更新完成，共更新了 {updated_repos}/{total_repos} 个仓库。")
        await exit_after_update(bot, ev)
    else:
        print("无已更新仓库")


@sv.on_prefix('克隆仓库', '#克隆仓库')
async def clone_repo(bot, ev: CQEvent):
    """
    克隆新的 Git 仓库
    """
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, "抱歉，没有权限执行此操作。")
        return

    args = ev.message.extract_plain_text().strip().split()
    if len(args) != 1:
        await bot.send(ev, "请提供一个有效的仓库 URL。")
        return

    repo_url = args[0]
    try:
        repo_name = GitTool.clone_repo(repo_url)
        await bot.send(ev, f"成功克隆仓库：{repo_url}\n仓库名：{repo_name}")
        await exit_after_update(bot, ev)
    except Exception as e:
        await bot.send(ev, e)


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

    with open(SAMPLE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("即将关闭进程...")
    sys.exit(0)