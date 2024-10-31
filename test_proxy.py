import requests


# PROXY_ADDR = 'socks5://username:password@localhost:3000'
PROXY_ADDR = 'socks5://username:password@43.153.3.156:3000'


def test_httpbin():
    url = 'http://httpbin.org/get'

    resp = requests.get(url, proxies=dict(http=PROXY_ADDR, https=PROXY_ADDR))
    print(resp.text)
    assert resp.status_code == 200


def test_httpsbin():
    url = 'https://httpbin.org/get'

    resp = requests.get(url, proxies=dict(http=PROXY_ADDR, https=PROXY_ADDR))
    assert resp.status_code == 200
    print(resp.text)


def test_httpsgist():
    url = 'https://gist.githubusercontent.com/csrgxtu/9c3d4303e262bf5333cc57ff11ea9105/raw/d57dcf1b58d76b5e543618e203f8bffb3fa141d9/gistfile1.txt'

    resp = requests.get(url, proxies=dict(http=PROXY_ADDR, https=PROXY_ADDR))
    assert resp.status_code == 200
    print(resp.text)


def test_httpsgoogle():
    url = 'https://google.com'

    resp = requests.get(url, proxies=dict(http=PROXY_ADDR, https=PROXY_ADDR))
    assert resp.status_code == 200
    print(resp.text)


def test_httpsbaidu():
    url = 'https://baidu.com'

    resp = requests.get(url, proxies=dict(http=PROXY_ADDR, https=PROXY_ADDR))
    assert resp.status_code == 200
    print(resp.text)


def test_httpsyoutube():
    url = 'https://youtube.com'

    resp = requests.get(url, proxies=dict(http=PROXY_ADDR, https=PROXY_ADDR))
    assert resp.status_code == 200
    print(resp.text)


def test_httpstwitter():
    url = 'https://twitter.com'

    resp = requests.get(url, proxies=dict(http=PROXY_ADDR, https=PROXY_ADDR))
    assert resp.status_code == 200
    print(resp.text)
