#模拟登录获得cookie

import requests
from bs4 import BeautifulSoup
import yaml

# 获得post_key以便在登录时使用
def get_post_key():
    url = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    return soup.find('input')['value']


def login_pixiv():
    with open("config.yml") as f:
        account_info = yaml.load(f, Loader=yaml.SafeLoader)['Account']
    pixiv_id = account_info['ID']
    password = account_info['password']
    headers = {}
    url = "https://accounts.pixiv.net/ajax/login?lang=zh"
    data = {"pixiv_id": pixiv_id,
            "password": password}
    data['post_key'] = get_post_key()
    r = requests.post(url=url,data=data)
    # 通过登录返回的headers中的Set-Cookie设置Cookie
    cookie = r.headers['Set-Cookie']
    headers["Referer"] = "https://www.pixiv.net"
    headers["Cookie"] = cookie
    headers["user-agent"]="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    # 返回 hraders在以后的爬虫中使用
    return headers
