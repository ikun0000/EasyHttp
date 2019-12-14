from http import HttpRequest, get_file_md5, HttpResponse

if __name__ == '__main__':
    data = """GET /dir/test2.html HTTP/1.1
Host: detectportal.firefox.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0
Accept: */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Cache-Control: no-cache
Pragma: no-cache
Connection: close
Cookie: a=1; b=2


"""
    postdata = 'POST /a.html?a=2&p=bb HTTP/1.1\r\nHost: 127.0.0.1\r\nUser-Agent: python-requests/2.22.0\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nConnection: keep-alive\r\nContent-Length: 27\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\nname=kk&password=1122334455'

    data = data.replace('\n', '\r\n')
    # data = data.replace('\n', '\r\n')
    #
    #
    #
    # obj = HttpRequest(data.encode())
    # print(obj.version)
    # print(obj.method)
    # print(obj.request_args)
    # print(obj.path)
    # print(obj.post_data)
    # print(obj.anchor)
    # print(obj.cookie)
    # print(get_file_md5("C:\\Users\\kk\\Desktop\\a.exe"))

    try:
        requ = HttpRequest(data.encode())
        resp = HttpResponse(200, requ.path, 'c293bc4cf5fe9da8d94898e38d9b5726')
        print(resp.get_socket_data().decode())
    except:
        resp = HttpResponse(400, '/400.html')
        print(resp.get_socket_data().decode())
