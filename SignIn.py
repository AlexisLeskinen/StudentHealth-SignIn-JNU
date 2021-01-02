import json
import time
import pip._vendor.requests
from base64 import b64encode
# 由于密码加密要用到crytop，需要pip3安装下面这个
# https://pycryptodome.readthedocs.io/en/latest/src/api.html
# Crypto使用文档
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

Host = "https://stuhealth.jnu.edu.cn"
UrlLogin = Host + "/api/user/login"
UrlSignIn = Host + "/api/write/main"
UrlStuInfo = Host + "/api/user/stuinfo"
UTF8 = "utf-8"
# 加密密钥
Key = 'xAt9Ye&SouxCJziN'.encode(UTF8)
#Key2 = "Netc705%Netc705%".encode(UTF8)

# 打卡参数
# signInJson = {
#     "mainTable": None, "jnuid": None}
# 请求头
headers = {
    "Host": "stuhealth.jnu.edu.cn",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Content-Type": "application/json",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5"
}

# 封装了下Request请求


def Request(url, params, method='post'):
    return pip._vendor.requests.request(method=method, url=url, json=params, headers=headers)

# 打卡


def SignIn(signInJson, repeat=0):
    # 发送打卡请求
    res = Request(UrlSignIn, signInJson)
    if(res.json()['meta']['code'] == 6666):
        print(signInJson['mainTable']['personName'] + "打卡成功！", end='\t')
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    else:
        repeat = repeat+1
        # 重试超过五次，停止打卡
        if(repeat == 5):
            print(res.json(), end='\n\n')
            print(signInJson)
            return
        else:
            SignIn(signInJson, repeat)

# 登陆，获取jnuid
# 需要学号和密码（webvpn那个）


def GetJNUID(username, password):
    password = encrypt(password, Key)
    logInParam = {
        "username": username, "password": password
    }

    res = Request(UrlLogin, logInParam)
    res = res.json()
    return res["data"]["jnuid"]


# 加密密码


def encrypt(password, key):
    # 最右边的是CBC加密的偏移量vi，16位
    # 这里直接取key作为偏移
    cipher = AES.new(key, AES.MODE_CBC, key)
    # 将密码填充到符合CBC加密的格式
    # 默认pkcs7方式
    passwaord = pad(password.encode(UTF8), AES.block_size)
    # 加密
    result = cipher.encrypt(passwaord)
    result = b64encode(result).decode(UTF8)
    # 将加密后的密码混淆
    # 和js前端里面的一样
    result = result.replace(r"/\//g", "_").replace(r"/\+/g", "-")
    result = result.replace(r"+", "-", 1).replace(r"/",
                                                  "_", 1).replace(r"=", "*", 1)
    return result

# 获取信息
# 返回打卡Json


def GetInfo(jnuid):
    StuInfoParam = {
        "jnuid": jnuid, "idType": 1
    }
    res = Request(UrlStuInfo, StuInfoParam)
    data = res.json()['data']
    mainTable = data['mainTable']

    # 给打卡json的空白处赋值
    # 打卡时间
    mainTable['declareTime'] = time.strftime("%Y-%m-%d", time.localtime())
    # 姓名
    mainTable['personName'] = data['xm']
    # 性别
    mainTable['sex'] = data['xbm']
    # 学院
    mainTable['collegeName'] = data['yxsmc']
    # 专业
    mainTable['professionName'] = data['zy']

    # 删除空白的key
    for k in list(mainTable.keys()):
        if not mainTable.get(k):
            del mainTable[k]

    mainTable['way2Start'] = ''
    mainTable['schoolC1'] = ''
    # 删除这3个，不然不打卡失败
    del mainTable['del']
    del mainTable['id']
    del mainTable['personType']
    signInJson = {
        "mainTable": mainTable, "jnuid": jnuid
    }

    return signInJson

# 主程序


def main(username, password):
    junid = GetJNUID(username, password)
    signInJson = GetInfo(junid)
    SignIn(signInJson)


if __name__ == '__main__':
    main(学号, 密码)
