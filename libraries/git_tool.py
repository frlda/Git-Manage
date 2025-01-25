import re
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

    def clone_repo(repo_url: str):
        """
        克隆远程仓库到固定路径，并将仓库名添加到MODULES_ON集合中。

        :param repo_url: 远程仓库地址
        """
        try:
            # 获取仓库名
            repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            MODULES_PATH = Path(__file__).parent.parent.parent / repo_name

            # 克隆远程仓库到固定路径
            Repo.clone_from(repo_url, MODULES_PATH)
            print(f"成功克隆仓库到 {MODULES_PATH}")

            # 更新__bot__.py文件中的MODULES_ON集合
            config_file = Path(__file__).parent.parent.parent.parent / 'config' / '__bot__.py'
            if not config_file.exists():
                raise FileNotFoundError(f"配置文件 {config_file} 不存在！")

            with open(config_file, 'r', encoding='utf-8') as f:
                config_content = f.read()

            # 使用正则表达式找到MODULES_ON集合并添加新的仓库名
            modules_on_pattern = re.compile(r'MODULES_ON\s*=\s*{([^}]*)}')
            match = modules_on_pattern.search(config_content)
            if match:
                # 提取集合内容
                modules_on_content = match.group(1)
                current_modules = set(
                    item.strip().strip("'").strip('"') for item in modules_on_content.split(',') if item.strip())
                current_modules.add(repo_name)  # 添加新的仓库名

                # 格式化集合内容
                new_modules_on_content = ', '.join(f"'{module}'" for module in sorted(current_modules))
                new_config_content = config_content[:match.start(1)] + new_modules_on_content + config_content[
                                                                                                match.end(1):]

                # 写回配置文件
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(new_config_content)
                print(f"成功将仓库 {repo_name} 添加到 MODULES_ON 集合中")
            else:
                print("未找到 MODULES_ON 集合")
            return repo_name

        except Exception as e:
            raise Exception(f"克隆仓库时出错：{e}")
