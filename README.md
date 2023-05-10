# HTTP Simple Implementation Over TCP

## Test

```sh
python3 ./http_client.py http://www.baidu.com
python3 ./http_client.py http://127.0.0.1:8888

python3 ./http_server.py

python3 -m pytest .\test_parse_http_header.py -v -s
python3 -m pytest .\test_read_http_from_stream.py -v -s
```

Test connection keep alive by using socket

```sh
>>> import socket
>>> s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
>>> s.connect(("127.0.0.1", 8888))
>>> request_data = b"GET / HTTP/1.0\r\n" +b"Host: 127.0.0.1\r\n\r\n"
>>> s.sendall(request_data)
>>> s.recv(1024)
b'HTTP/1.0 200 OK\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: application/json\r\nServer: Apache\r\nClient: (\'127.0.0.1\', 61840)\r\nContent-Length: 47\r\n\r\n{"name": "sample", "time": 11111.0, "day": 111}'
>>> s.sendall(request_data)
>>> s.recv(1024)
b'HTTP/1.0 200 OK\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: application/json\r\nServer: Apache\r\nClient: (\'127.0.0.1\', 61840)\r\nContent-Length: 47\r\n\r\n{"name": "sample", "time": 11111.0, "day": 111}'
```

## TODOs

- [] read http body
  - [x] via `content-length`
  - [ ] via `chunk`
- [] support `connection:keep-alive`

## HTTP Message Definition

[RFC7230](https://www.rfc-editor.org/rfc/rfc7230#section-3) states HTTP message:

>     generic-message = start-line
>                       *(message-header CRLF)
>                       CRLF
>                       [ message-body ]

So there's:

1. The start-line, which is either a `Request-Line` or a `Status-Line`, both of which end in **CRLF**.
2. Zero or more message-headers, each ending in **CRLF**.
3. A **CRLF** to denote the end of the start-line and headers.
4. Optionally, a message body if `content-length` or other header(`chunk`) exists.

> **CRLF**: `\r\n`

That being said, you don't want to parse HTTP yourself. Use a library for that.

## HTTP Message Example

[![enter image description here][1]][1]
*(picture [source](https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages))*

  [1]: https://i.stack.imgur.com/j63Ua.png

## HTTP Message Data Example

In Python, the raw data with escaping character

```py
request_data = (
    b"GET / HTTP/1.0\r\n"
    b"Host: 127.0.0.1\r\n"
    b"Connection: close\r\n"
    b"\r\n"
)
```

```py
response_data = (
    b"HTTP/1.0 200 OK\r\n"
    b"Server: SimpleHTTP/0.6\r\n"
    b"Date: Mon, 13 Oct 2014 17:55:55 GMT\r\n"
    b"Content-type: text/html; charset=UTF-8\r\n"
    b"Content-Length: 10\r\n"
    b"\r\n"
    b"0123456789"
)
```


[http - Raw POST request with json in body - Stack Overflow](https://stackoverflow.com/questions/32436864/raw-post-request-with-json-in-body)

[What, at the bare minimum, is required for an HTTP request? - Stack Overflow](https://stackoverflow.com/questions/6686261/what-at-the-bare-minimum-is-required-for-an-http-request)

[StringIO Module in Python - GeeksforGeeks](https://www.geeksforgeeks.org/stringio-module-in-python/)

## HTTP Protocol Parsing Libraries

[GitHub - python-hyper/h11: A pure-Python, bring-your-own-I/O implementation of HTTP/1.1](https://github.com/python-hyper/h11)
[GitHub - MagicStack/httptools: Fast HTTP parser](https://github.com/MagicStack/httptools)
[GitHub - kbandla/dpkt: fast, simple packet creation / parsing, with definitions for the basic TCP/IP protocols](https://github.com/kbandla/dpkt)
[GitHub - benoitc/http-parser: HTTP request/response parser for python in C](https://github.com/benoitc/http-parser/)
[GitHub - silentsignal/netlib-offline: Raw HTTP parser for Python, based on mitmproxy's netlib](https://github.com/silentsignal/netlib-offline)

## TODOs

- HTTPs practices:

  [How does HTTPS work?](https://blog.bytebytego.com/p/how-does-https-work-episode-6)
