# Git-Manage
基于 [HoshinoBotv2](https://github.com/Ice9Coffee/HoshinoBot) 的用于更新通过Git管理的插件

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

开启 Git-Manage      ：启用插件
更新全部仓库            ：更新全部通过Git管理的仓库
```
## 注意
建议运行时使用以下脚本
```
#!/bin/bash
# 循环运行并记录日志
while true
do
    python run.py >> run.log 2>&1
    echo "Restarting automatically in 3 seconds (press Ctrl + C to cancel)" >> run.log
    sleep 3
done
```
创建在Hoshino根目录后赋予可执行权限`chmod +x run_loop.sh`

## 致谢
| Nickname         | Contribution      |
| ---------------- | ----------------- |
| [HoshinoReboot](https://github.com/Norca0721/HoshinoReboot) | 提供的重启相关功能 |
