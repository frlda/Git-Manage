import sys
from . import sv, MODULES_ON, MODULES_PATH, BOTNAME
from .libraries.git_tool import GitTool
from hoshino.typing import CQEvent
from hoshino import priv


@sv.on_fullmatch('更新全部仓库')
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
        await exit_after_update(updated_repos, total_repos, bot, ev)
    else:
        print("无已更新仓库")


async def exit_after_update(updated_repos, total_repos, bot, ev):
    """
    用于在更新完成后退出当前进程
    """
    await bot.send(ev, f"所有仓库更新完成，共更新了 {updated_repos}/{total_repos} 个仓库。")
    print(f"所有仓库更新完成，共更新了 {updated_repos}/{total_repos} 个仓库。")
    await bot.send(ev, f"即将重启{BOTNAME}...")
    print("即将关闭进程...")
    sys.exit(0)