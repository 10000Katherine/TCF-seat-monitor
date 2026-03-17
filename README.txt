TCF Seat Monitor (GUI Version)

这个版本已经是完整的可分享项目包：
- 图形界面
- 保存邮箱配置
- Start / Stop 监控
- 邮件提醒
- 日志文件
- 预设 Vancouver / Victoria / Ashton 三个考点

使用步骤：
1. 先安装 Python 3
2. 双击 install_and_run.bat
3. 在界面里填写：
   - Gmail
   - Gmail 的 16 位 App Password
   - 接收提醒邮箱
4. 勾选要监控的考点
5. 点击 Start Monitoring

文件说明：
- gui_monitor.py       图形界面
- monitor_core.py      后台监控逻辑
- targets.json         考点配置
- config.env.example   配置模板
- requirements.txt     依赖
- tcf_monitor.log      运行后自动生成日志

重要说明：
1. Victoria 的检测相对直接：页面里如果不再出现 SOLD OUT，就会发提醒。
2. Vancouver / Ashton 目前采用“页面关键内容变化提醒”模式：
   这类提醒很有价值，但仍建议你点开网页人工确认一次。
3. Gmail 必须先开启两步验证，再生成 App Password。
4. 如果以后你想打包成 exe：
   pip install pyinstaller
   pyinstaller --noconsole --onefile gui_monitor.py

建议分享给别人时配一句：
“下载后双击 install_and_run.bat，填邮箱就能用。”
