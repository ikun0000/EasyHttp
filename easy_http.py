import socket
import select
import logging
import datetime
import optparse
import signal
import sys
from http import HttpRequest, HttpResponse


def handler(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

# 设置日志格式和帮助信息
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] - %(message)s", filename="access.log") 
HELP_TEXT = """
python easy_http.py [-l host] [-p port] 
"""

if __name__ == '__main__':
    optionparse = optparse.OptionParser(HELP_TEXT)          # 初始化参数
    optionparse.add_option('-l', '--listen', 
                           dest='listen_addr', help='listen address, default 127.0.0.1', type='str', default='127.0.0.1')
    optionparse.add_option('-p', '--port', 
                           dest='port', help='the listen port, default 80', type='int', default=80)
    option, args = optionparse.parse_args()


    listen_addr = option.listen_addr        # 获得监听地址
    port = option.port                      # 获得监听端口
    print("Starting Easy HTTP, listen at {}:{}".format(listen_addr, port))
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setblocking(False)             # 设置套接字非阻塞，使用异步IO读取请求
    listener.bind((listen_addr, port))      # 绑定监听地址和端口
    listener.listen(500)                    # 最大连接数

    readlist = [listener, ]                 # select的第一个参数

    while True:
        rdlist, _, _ = select.select(readlist, [], [])

        for sfd in rdlist:
            if sfd is listener:
                client, addr = listener.accept()
                client.setblocking(False)
                readlist.append(client)
            else:
                buf = sfd.recv(4096)
                if buf == b'':
                    readlist.remove(sfd)
                    sfd.close()
                else:
                    try:
                        request = HttpRequest(buf)
                        logging.info('{0} {1}'.format(request.method, request.request_page))
                        print('[{0}] - {1} {2}'.format(datetime.datetime.now().strftime('%c'), request.method, request.request_page))
                        resp = HttpResponse(200, request.path, request.header.get('If-None-Match', ''))
                    except:
                        resp = HttpResponse(400, '/400.html', '')

                    sfd.send(resp.get_socket_data())

                    if request.header.get('Connection', '') == 'close':
                        readlist.remove(sfd)
                        sfd.close()
