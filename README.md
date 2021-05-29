# StudentHealth-SignIn-JNU
一个能够自动健康打卡的脚本
首先你需要一个pyhton并且装好pip
然后安装cryto包用来加密密码
·pip install pycryptodome·
之后在
···
account = {
    '学号': '密码'
}
···
 中填入你的学号和密码就能打卡了
 如果有linux服务器的话，配合crontab可以实现每天自动打卡
 理论上使用windows的定时任务也有类似的作用，不过我没试过就是了
