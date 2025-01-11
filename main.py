from . import sv, MODULES_ON, MODULES_PATH
from .libraries.git_tool import GitTool
from hoshino.typing import CQEvent

@sv.on_fullmatch('更新全部仓库')
async def update_all_repos(bot, ev: CQEvent):
    success_messages = []
    error_messages = []

    for module in MODULES_ON:
        repo_path = MODULES_PATH / module
        try:
            git_tool = GitTool(str(repo_path))
            update_status = git_tool.update_repo()

            if update_status["status"] == "up-to-date":
                print(f"仓库 {module} 已是最新状态，无需更新。")
                success_messages.append(f"仓库 {module} 已是最新状态，无需更新。")
            elif update_status["status"] == "updated":
                commits_updated = update_status["commits_updated"]
                update_logs = git_tool.get_update_logs(commits_updated)

                log_messages = "\n".join([f"{log['date']} {log['author']}: {log['message']}" for log in update_logs])
                print(f"仓库 {module} 更新成功。\n更新日志:\n{log_messages}")
                success_messages.append(
                    f"仓库 {module} 更新成功，共更新了 {commits_updated} 个提交。\n更新日志:\n{log_messages}"
                )
        except Exception as e:
            print(f"更新仓库 {module} 时出错：{e}")
            error_messages.append(f"更新仓库 {module} 时出错：{e}")

    if success_messages:
        await bot.send(ev, "\n".join(success_messages))
    if error_messages:
        await bot.send(ev, "\n".join(error_messages))