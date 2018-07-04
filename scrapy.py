import multiprocessing
import socket
import time
import re
import signal
import requests
import bs4

# 构造socket连接，和斗鱼api服务器相连接
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname("openbarrage.douyutv.com")
port = 8601
client.connect((host, port))

# 弹幕查询正则表达式
danmu_re = re.compile(b'txt@=(.+?)/cid@')
username_re = re.compile(b'nn@=(.+?)/txt@')
uid_re = re.compile(b'uid@(.+?)/nn@')
level_re = re.compile(b'level@=([1-9][0-9]?)/sahf')


# 根据房间号获取房间名
def get_room_name(roomid):
    res = requests.get('http://www.douyu.com/' + roomid)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    return soup.find('a', {'class', 'zb-name'}).string


def send_req_msg(msgstr):
    '''构造并发送符合斗鱼api的请求'''

    msg = msgstr.encode('utf-8')
    data_length = len(msg) + 8
    code = 689
    # 构造协议头
    msgHead = int.to_bytes(data_length, 4, 'little') \
              + int.to_bytes(data_length, 4, 'little') + \
              int.to_bytes(code, 4, 'little')
    client.send(msgHead)
    sent = 0
    while sent < len(msg):
        tn = client.send(msg[sent:])
        sent = sent + tn


def get_msg_start(roomid,num):
    # 构造登录授权请求
    msg = 'type@=loginreq/roomid@={}/\0'.format(roomid)
    send_req_msg(msg)
    room_name = get_room_name(roomid)
    print('已连接至{}的直播间'.format(room_name))
    # 构造获取弹幕消息请求
    msg_more = 'type@=joingroup/rid@={}/gid@=-9999/\0'.format(roomid)
    send_req_msg(msg_more)
    # barrage_list = []
    # barrage_list.append(['用户id', '昵称', '等级', '内容'])
    flag = True
    while flag:
        # 服务端返回的数据
        data = client.recv(1024)
        # 通过re模块找发送弹幕的用户名和内容
        danmu_username = username_re.findall(data)
        danmu_content = danmu_re.findall(data)
        uid_content = uid_re.findall(data)
        level_content = level_re.findall(data)
        if not data:
            break
        else:
            for i in range(0, len(danmu_content)):
                try:
                    # barrage_list.append(uid_content,danmu_username,level_content,danmu_content)
                    # 输出信息

                    result = '[id{}][{}][{}]:{}'.format(uid_content[0].decode('utf-8'), level_content[0].decode('utf-8'),
                                                      danmu_username[0].decode(
                                                          'utf8'), danmu_content[0].decode(encoding='utf8'))

                    result1 = '{}'.format(danmu_content[0].decode(encoding='utf8'))

                    print(result)

                    save_txt(result1)
                    if len(result) > num:
                        print('已成功获得%d条弹幕' % len(result))
                        flag = False
                        break
                except:
                    continue


def save_txt(content):
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(''.join(content) + '\n')


def keeplive():
    '''
    保持心跳，15秒心跳请求一次
     '''
    while True:
        msg = 'type@=keeplive/tick@=' + str(int(time.time())) + '/\0'
        send_req_msg(msg)
        print('发送心跳包')
        time.sleep(15)


def logout():
    '''
    与斗鱼服务器断开连接
    关闭线程
    '''
    msg = 'type@=logout/'
    send_req_msg(msg)
    print('已经退出服务器')


def signal_handler(signal, frame):
    '''
    捕捉 ctrl+c的信号 即 signal.SIGINT
    触发hander：
    登出斗鱼服务器
    关闭进程
    '''
    p1.terminate()
    p2.terminate()
    logout()
    print('Bye')


if __name__ == '__main__':
    room_id = input('请输入房间ID： ')
    need_num = input('请输入需要的弹幕数量：')
    num = int(need_num)
    # 房间号
    # room_id = 748396
    # 开启signal捕捉
    signal.signal(signal.SIGINT, signal_handler)

    # 开启弹幕和心跳进程
    p1 = multiprocessing.Process(target=get_msg_start, args=(room_id, num))
    p2 = multiprocessing.Process(target=keeplive)
    p1.start()
    p2.start()

