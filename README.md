# tgyaoqing
tg邀请积分统计机器人
用户邀请一个好友可以获取1积分.
15积分可以兑换奖励
可以在配置文件修改
按钮文本可以在mail.py文件修改，第331行

兑换奖励路径在第360行修改，默认读取文本第一行作为奖励，兑换后会删除该奖励

# 兑换积分的值，用户需要达到多少积分才能兑换奖励
EXCHANGE_SCORE = 15
运行前确保可以正常访问网络


pip3 install python-telegram-bot==13.7
pip install aiogram==2.14

纯python, 可以代码直接复制,运行main.py
确保有python3.8以上的坏境
确保已经正确修改config.py文件

不懂怎么改可以问我
接机器人定制 联系 @im_shiyi
