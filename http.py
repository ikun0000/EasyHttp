import os.path
import datetime
import hashlib

STATIC_PATH = 'html'
DATE_FORMAT = '%a, %d %b %Y %X GMT'


# 根据路径获取文件的MD5校验值，如果文件不存在，则抛出FileNotFoundError
# 返回值为文件MD5检验的十六进制字符串
def get_file_md5(filename:str):
    if not os.path.exists(filename):
        raise FileNotFoundError("{} Nof Found".format(filename))

    file_data = b''
    with open(filename, 'rb') as fd:
        while True:
            data = fd.read(1024)
            if data is None or data == b'':
                break
            file_data += data

    return hashlib.md5(file_data).hexdigest()


# 这个类用来格式化HTTP请求数据
class HttpRequest:

    # 接收一个bytes序用来列格式化
    # @param raw_data: 一个bytes类型的http请求数据
    def __init__(self, raw_data: bytes):
        self.raw_data = raw_data
        self.header = dict()

        recv_data = raw_data.decode()
        self.request_method = recv_data.split('\r\n')[0].split(' ')[0]                  # 获取请求的方法
        self.request_page = recv_data.split('\r\n')[0].split(' ')[1]                    # 获取请求的路径，参数，锚点
        self.http_version = recv_data.split('\r\n')[0].split(' ')[2].split('/')[1]      # 获取HTTP版本号

        for item in recv_data.split('\r\n')[1:recv_data.split('\r\n').index('')]:       # 把http请求头用\r\n分割成列表并迭代
            if item != '':                                                              # 排除header和body中间的空行
                self.header[item.split(': ')[0]] = item.split(': ')[1]                  # 把客户端请求的信息放到列表里面

        self.request_path = self.request_page.split('?')[0]                             # 去除请求路径的参数
        request_path_anchor = self.request_path
        self.request_path = self.request_path.split('#')[0]                             # 去除请求路径的锚点
        self.request_args = dict()                                                      # 获取请求路径的参数
        try:
            arguments = self.request_page.split('?')[1]                                 # 如果没有带参数那么就会抛出数组越界异常
            for argument in arguments.split('&'):
                self.request_args[argument.split('=')[0]] = argument.split('=')[1]

        except:                                                                         # 没有参数则设置为None
            self.request_args = None

        self.request_anchor = ''
        try:
            self.request_anchor = request_path_anchor.split('#')[1]                               # 获得锚点
        except:
            self.request_anchor = None

        self.post_data = dict()
        if self.method == 'POST':                   # 如果是POST请求则对body进行解析
            post_data = recv_data.split('\r\n')[recv_data.split('\r\n').index('') + 1].split('&')
            for item in post_data:
                self.post_data[item.split('=')[0]] = item.split('=')[1]
        else:
            self.post_data = None


    # 获取原始的数据，即构造器传入的数据
    @property
    def raw(self):
        return self.raw_data

    # 获取HTTP请求的方法
    @property
    def method(self):
        return self.request_method

    # 获取请求的文件路径
    @property
    def path(self):
        return self.request_path

    # 获取HTTP版本
    @property
    def version(self):
        return self.http_version

    # 获取浏览器携带的COOKIE
    # 如果有cookie返回一个cookie字典，没有cookie返回None
    @property
    def cookie(self):
        cookie = self.header.get('Cookie', None)
        if cookie is None:                  # 如果没有携带Cookie返回None
            return None

        cookie = cookie.replace(' ', '')
        cookie_list = cookie.split(';')     # 如果没有被分割则尝试;
        if cookie_list is None:
            if ';' not in cookie:           # 如果还是不行就是携带了一个cookie
                cookie_list[cookie.split('=')[0]] = cookie.split('=')[1]
                return cookie_list

        cookie_dict = dict()
        for item in cookie_list:
            if item != '':
                cookie_dict[item.split('=')[0]] = item.split('=')[1]

        return cookie_dict

    # 获取路径携带的参数
    # 如果携带了参数返回一个参数字典，否则返回None
    @property
    def pathargs(self):
        return self.request_args

    # 获得POST请求的数据
    # 如果有返回一个字典，没有返回None
    @property
    def postdata(self):
        return self.post_data

    # 获取路径的锚点
    # 如果有返回锚点值，没有返回None
    @property
    def anchor(self):
        return self.request_anchor






# HTTP状态码对应的说明文字
HTTP_STATUS_CODE = {
    200: 'OK',
    304: 'Not Modified',
    400: 'Bad Request',
    404: 'Not Found',
    500: 'Internal Server Error',
}

# 文件后缀对应的Content-type
FILE_TYPE = {
    'txt': 'text/plain; charset=UTF-8',
    'html': 'text/html; charset=iso-8859-1',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'js': 'application/javascript; charset=utf-8',
    'css': 'text/css'
}

# 根据传入的状态码，文件路径和文件的MD5校验值生成HTTP响应数据
class HttpResponse:

    # 接受HTTP状态码，文件路径和文件MD5校验值实例化一个HTTP返回对象
    # @param status_code: 要生成的返回对象的HTTP状态码，会受到path，file_mode改变
    # @param path 返回文件的路径，会受到自身，status_code，file_md5而改变
    # @param file_md5 请求文件的MD5校验值，由[If-None-Match]携带
    def __init__(self, status_code:int, path:str = '/', file_md5:str = ''):
        self.status_code = status_code
        self.file_md5 = file_md5
        if path == '/':                             # 如果时请求网站域名或者传入空，返回体时默认首页
            self.file_path = os.path.join(STATIC_PATH, 'index.html')
        else:
            self.file_path = os.path.join(STATIC_PATH, path[1:])

        if path == '':                              # 请求错误
            self.status_code = 400
            self.file_path = os.path.join(STATIC_PATH, '400.html')


        if not os.path.exists(self.file_path):          # 如果请求的页面不存在自动把返回状态码改为404，并返回404页面
            self.status_code = 404
            self.file_path = os.path.join(STATIC_PATH, '404.html')

        self.response_header = dict()                   # 构造必要的头部信息

        self.response_header['Date'] = datetime.datetime.now().strftime(DATE_FORMAT)
        self.response_header['Server'] = 'Easy HTTP0.1'
        try:                                            # 根据请求文件的后缀确定Content-type
            file_type = os.path.basename(self.file_path).split('.')[1]
            self.response_header['Content-Type'] = FILE_TYPE[file_type]
        except:                                         # 如果没有后缀则直接当客户端作请求错误处理
            self.status_code = 400
            self.file_path = os.path.join(STATIC_PATH, '400.html')
            self.response_header['Content-Type'] = FILE_TYPE['html']

        if self.status_code == 200:                     # 如果时成功返回页面就使用长连接，否则使用短连接
            self.response_header['Connection'] = 'keep-alive'
        else:
            self.response_header['Connection'] = 'close'


    # 获取可以直接通过套接字send发送的字节序
    def get_socket_data(self):
        resp_body = self.body       # 获取返回体，返回提函数会影响到返回头部信息，所以要先获取
        resp_data = 'HTTP/1.1 '.encode() + str(self.status_code).encode() + " ".encode() + HTTP_STATUS_CODE[self.status_code].encode() + '\r\n'.encode()        # 获取HTTP返回头第一行
        resp_header = b''

        for field, field_value in self.header.items():          # 根据头部的字典生成头部字节序
            resp_header += (field.encode() + ': '.encode() + field_value.encode() + '\r\n'.encode())

        resp_data += resp_header            # 拼接返回数据
        resp_data += '\r\n'.encode()
        resp_data += resp_body
        return resp_data


    # 当HTTP状态码为200时默认是长连接，可以通过这个方法设置为短连接
    def set_close(self):
        self.response_header['Connection'] = 'close'

    # 这个方法可以自己增加头部信息或修改已有的头部信息
    def put_header(self, key:str, value:str):
        self.response_header[key] = value

    # 获取头部字段的字典
    @property
    def header(self):
        return self.response_header

    # 获取返回状态码
    @property
    def code(self):
        return self.status_code

    # 获取返回的body
    @property
    def body(self):
        self.response_body = b''

        if self.status_code == 200:
            if get_file_md5(self.file_path) == self.file_md5:           # 如果是200的状态码并且请求的内容不变返回304
                self.status_code = 304
                self.response_header['ETag'] = self.file_md5
                return self.response_body

        with open(self.file_path, 'rb') as fd:                          # 读请求的文件内容
            while True:
                data = fd.read(1024)
                if data is None or data == b'':
                    break
                self.response_body += data
        if self.status_code == 200:                                     # 如果返回400，404，500的状态码则不设置ETag
            self.response_header['ETag'] = get_file_md5(self.file_path)
        self.response_header['Content-Length'] = str(len(self.response_body))
        return self.response_body