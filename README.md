# Git-Manage
基于 [HoshinoBotv2](https://github.com/Ice9Coffee/HoshinoBot) 的用于更新通过Git管理的插件（新增手动重启）
本项目适用于linux环境下
## 使用前置
```bash
pip install -r requirements.txt
```

## 环境需求
```
python 3.8+
```

## 使用说明
```
在 hoshino/config/__bot__.py 中添加本项目文件名
在群里或私信向 bot 发送 [开启 Git-Manage] 启用插件

开启 Git-Manage         ：启用插件
#更新全部仓库            ：更新全部通过Git管理的仓库
#克隆版仓库 [仓库链接]    ：克隆指定仓库到Hoshino插件目录下，需保证链接最后路径为插件名
#reloading or 一键重启      ：手动重启hoshino
```
## 注意
建议运行时使用文件夹中以下脚本
run_loop.sh

移动到Hoshino根目录后（即run.py所在目录）赋予可执行权限`chmod +x run_loop.sh`

之后启动hoshinobot，请使用指令
```
./run_loop.sh
```

## 致谢
| Nickname         | Contribution      |
| ---------------- | ----------------- |
| [HoshinoReboot](https://github.com/Norca0721/HoshinoReboot) | 提供的重启相关功能 |
