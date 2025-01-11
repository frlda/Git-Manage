from git import Repo
from pathlib import Path
from typing import List

class GitTool:
    def __init__(self, repo_path: str):
        """
        初始化 Git 工具类。

        :param repo_path: Git 仓库的本地路径
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists() or not (self.repo_path / '.git').exists():
            raise ValueError(f"插件 {self.repo_path.name} 不是有效的 Git 仓库")
        self.repo = Repo(self.repo_path)

    def update_repo(self):
        """
        更新 Git 仓库到当前所在分支的最新状态，并识别是否已经处于最新状态。
        返回更新的提交数量。
        """
        try:
            current_branch = self.repo.active_branch.name
            print(f"当前所在分支为 {current_branch}，正在检查更新...")

            if self.repo.is_dirty():
                raise Exception("仓库有未提交的更改，请先处理后再更新。")

            origin = self.repo.remote()
            origin.fetch()

            local_commit = self.repo.commit(current_branch)
            remote_commit = self.repo.commit(f"origin/{current_branch}")

            if local_commit == remote_commit:
                print(f"分支 {current_branch} 已经是最新状态，无需更新。")
                return {"status": "up-to-date", "branch": current_branch, "commits_updated": 0}

            commits_to_update = list(self.repo.iter_commits(f"{current_branch}..origin/{current_branch}"))
            commit_count = len(commits_to_update)

            print(f"从远程拉取分支 {current_branch} 的最新更改...")
            origin.pull(current_branch)
            print(f"分支 {current_branch} 已更新到最新状态，共更新 {commit_count} 个提交。")
            return {"status": "updated", "branch": current_branch, "commits_updated": commit_count}

        except Exception as e:
            raise Exception(f"更新仓库时出错：{e}")

    def get_update_logs(self, max_logs: int = 5) -> List[dict]:
        """
        获取当前分支的最新提交日志。

        :param max_logs: 要获取的提交日志数量，默认为 5。
        :return: 包含提交信息的字典列表，每个字典包含 'hash', 'author', 'date', 'message' 键。
        """
        try:
            logs = []
            current_branch = self.repo.active_branch.name

            for commit in self.repo.iter_commits(current_branch, max_count=max_logs):
                logs.append({
                    'hash': commit.hexsha,
                    'author': commit.author.name,
                    'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'message': commit.message.strip()
                })

            print(f"成功获取最新的 {max_logs} 条提交日志：{logs}")
            return logs

        except Exception as e:
            print(f"获取更新日志时出错：{e}")
            return []

    def clone_repo(repo_url: str, target_path: str):
        """
        克隆远程仓库到指定路径。

        :param repo_url: 远程仓库地址
        :param target_path: 本地目标路径
        """
        try:
            Repo.clone_from(repo_url, target_path)
            print(f"成功克隆仓库到 {target_path}")
        except Exception as e:
            print(f"克隆仓库时出错：{e}")
