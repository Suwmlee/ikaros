# -*- coding: utf-8 -*-

import re
import requests
import json
import pathlib
import time
import os
import uuid
import mechanicalsoup
from urllib.parse import urljoin
from http.cookies import SimpleCookie
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import current_app
from ..service.configservice import scrapingConfService


G_USER_AGENT = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'


def get_html(url, cookies: dict = None, ua: str = None, return_type: str = None):
    """ 网页请求核心
    """
    configProxy = scrapingConfService.getProxySetting()
    errors = ""

    if ua is None:
        headers = {"User-Agent": G_USER_AGENT}  # noqa
    else:
        headers = {"User-Agent": ua}

    for i in range(configProxy.retry):
        try:
            if configProxy.enable:
                proxies = configProxy.proxies()
                result = requests.get(str(url), headers=headers, timeout=configProxy.timeout, proxies=proxies,
                                      cookies=cookies)
            else:
                result = requests.get(
                    str(url), headers=headers, timeout=configProxy.timeout, cookies=cookies)

            result.encoding = "utf-8"

            if return_type == "object":
                return result
            elif return_type == "content":
                return result.content
            else:
                return result.text
        except requests.exceptions.ProxyError:
            current_app.logger.error("[-]Proxy error! Please check your Proxy")
            raise requests.exceptions.ProxyError
        except Exception as e:
            current_app.logger.info("[-]Connect retry {}/{} : {}".format(i + 1, configProxy.retry, url))
            current_app.logger.error(e)
    current_app.logger.info('[-]Connect Failed! Please check your Proxy or Network!')
    raise Exception('Connect Failed')


def post_html(url: str, query: dict, headers: dict = None) -> requests.Response:
    configProxy = scrapingConfService.getProxySetting()
    errors = ""
    headers_ua = {"User-Agent": G_USER_AGENT}
    if headers is None:
        headers = headers_ua
    else:
        headers.update(headers_ua)

    for i in range(configProxy.retry):
        try:
            if configProxy.enable:
                proxies = configProxy.proxies()
                result = requests.post(
                    url, data=query, proxies=proxies, headers=headers, timeout=configProxy.timeout)
            else:
                result = requests.post(
                    url, data=query, headers=headers, timeout=configProxy.timeout)
            return result
        except Exception as e:
            current_app.logger.info("[-]Connect retry {}/{} : {}".format(i + 1, configProxy.retry, url))
            current_app.logger.error(e)
    current_app.logger.info("[-]Connect Failed! Please check your Proxy or Network!")

G_DEFAULT_TIMEOUT = 10 # seconds

class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = G_DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)
    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)

#  with keep-alive feature
def get_html_session(url:str = None, cookies: dict = None, ua: str = None, return_type: str = None, encoding: str = None):
    configProxy = configProxy = scrapingConfService.getProxySetting()
    session = requests.Session()
    if isinstance(cookies, dict) and len(cookies):
        requests.utils.add_dict_to_cookiejar(session.cookies, cookies)
    retries = Retry(total=configProxy.retry, connect=configProxy.retry, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", TimeoutHTTPAdapter(max_retries=retries, timeout=configProxy.timeout))
    session.mount("http://", TimeoutHTTPAdapter(max_retries=retries, timeout=configProxy.timeout))
    if configProxy.enable:
        session.proxies = configProxy.proxies()
    headers = {"User-Agent": ua or G_USER_AGENT}
    session.headers = headers
    try:
        if isinstance(url, str) and len(url):
            result = session.get(str(url))
        else: # 空url参数直接返回可重用session对象，无需设置return_type
            return session
        if not result.ok:
            return None
        if return_type == "object":
            return result
        elif return_type == "content":
            return result.content
        elif return_type == "session":
            return result, session
        else:
            result.encoding = encoding or "utf-8"
            return result.text
    except requests.exceptions.ProxyError:
        print("[-]get_html_session() Proxy error! Please check your Proxy")
    except Exception as e:
        print(f"[-]get_html_session() failed. {e}")
    return None


def get_html_by_browser(url, cookies: dict = None, ua: str = None, return_type: str = None):
    browser = mechanicalsoup.StatefulBrowser(user_agent=G_USER_AGENT if ua is None else ua)
    configProxy = scrapingConfService.getProxySetting()
    if configProxy.enable:
        browser.session.proxies = configProxy.proxies()
    result = browser.open(url)
    if not result.ok:
        return ''
    result.encoding = "utf-8"
    if return_type == "object":
        return result
    elif return_type == "content":
        return result.content
    elif return_type == "browser":
        return result, browser
    else:
        return result.text


def get_html_by_form(url, form_name: str = None, fields: dict = None, cookies: dict = None, ua: str = None, return_type: str = None):
    browser = mechanicalsoup.StatefulBrowser(user_agent=G_USER_AGENT if ua is None else ua)
    if isinstance(cookies, dict):
        requests.utils.add_dict_to_cookiejar(browser.session.cookies, cookies)
    configProxy = scrapingConfService.getProxySetting()
    if configProxy.enable:
        browser.session.proxies = configProxy.proxies()
    result = browser.open(url)
    if not result.ok:
        return ''
    form = browser.select_form() if form_name is None else browser.select_form(form_name)
    if isinstance(fields, dict):
        for k, v in fields.items():
            browser[k] = v
    response = browser.submit_selected()
    response.encoding = "utf-8"
    if return_type == "object":
        return response
    elif return_type == "content":
        return response.content
    elif return_type == "browser":
        return response, browser
    else:
        return response.text


def is_japanese(s) -> bool:
    """ 日语简单检测
    """
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\uFF66-\uFF9F]', s, re.UNICODE))


def translate(
        src: str,
        target_language: str = "zh_cn",
        engine: str = "google-free",
        app_id: str = "",
        key: str = "",
        delay: int = 0,
):
    trans_result = ""
    if engine == "google-free":
        url = (
                "https://translate.google.cn/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl=auto&tl="
                + target_language
                + "&q="
                + src
        )
        result = get_html(url=url, return_type="object")

        translate_list = [i["trans"] for i in result.json()["sentences"]]
        trans_result = trans_result.join(translate_list)
    # elif engine == "baidu":
    #     url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    #     salt = random.randint(1, 1435660288)
    #     sign = app_id + src + str(salt) + key
    #     sign = hashlib.md5(sign.encode()).hexdigest()
    #     url += (
    #         "?appid="
    #         + app_id
    #         + "&q="
    #         + src
    #         + "&from=auto&to="
    #         + target_language
    #         + "&salt="
    #         + str(salt)
    #         + "&sign="
    #         + sign
    #     )
    #     result = get_html(url=url, return_type="object")
    #
    #     translate_list = [i["dst"] for i in result.json()["trans_result"]]
    #     trans_result = trans_result.join(translate_list)
    elif engine == "azure":
        url = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=" + target_language
        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Ocp-Apim-Subscription-Region': "global",
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        body = json.dumps([{'text': src}])
        result = post_html(url=url, query=body, headers=headers)
        translate_list = [i["text"] for i in result.json()[0]["translations"]]
        trans_result = trans_result.join(translate_list)

    else:
        raise ValueError("Non-existent translation engine")

    time.sleep(delay)
    return trans_result


# 从浏览器中导出网站登录验证信息的cookies，能够以会员方式打开游客无法访问到的页面
# 示例: FC2-755670 url https://javdb9.com/v/vO8Mn
# json 文件格式
# 文件名: 站点名.json，示例 javdb9.json
# 内容(文件编码:UTF-8)：
'''
{
    "over18":"1",
    "redirect_to":"%2Fv%2FvO8Mn",
    "remember_me_token":"cbJdeaFpbHMiOnsibWVzc2FnZSI6IklrNVJjbTAzZFVSRVlVaEtPWEpUVFhOVU0yNXhJZz09IiwiZXhwIjoiMjAyMS0wNS0xNVQxMzoyODoxNy4wMDBaIiwicHVyIjoiY29va2llLnJlbWVtYmVyX21lX3Rva2VuIn19--a7131611e844cf75f9db4cd411b635889bff3fe3",
    "_jdb_session":"asddefqfwfwwrfdsdaAmqKj1%2FvOrDQP4b7h%2BvGp7brvIShi2Y%2FHBUr%2BklApk06TfhBOK3g5gRImZzoi49GINH%2FK49o3W%2FX64ugBiUAcudN9b27Mg6Ohu%2Bx9Z7A4bbqmqCt7XR%2Bao8PRuOjMcdDG5czoYHJCPIPZQFU28Gd7Awc2jc5FM5CoIgSRyaYDy9ulTO7DlavxoNL%2F6OFEL%2FyaA6XUYTB2Gs1kpPiUDqwi854mo5%2FrNxMhTeBK%2BjXciazMtN5KlE5JIOfiWAjNrnx7SV3Hj%2FqPNxRxXFQyEwHr5TZa0Vk1%2FjbwWQ0wcIFfh%2FMLwwqKydAh%2FLndc%2Bmdv3e%2FJ%2BiL2--xhqYnMyVRlxJajdN--u7nl0M7Oe7tZtPd4kIaEbg%3D%3D",
    "locale":"zh",
    "__cfduid":"dee27116d98c432a5cabc1fe0e7c2f3c91620479752",
    "theme":"auto"
}
'''
# 从网站登录后，通过浏览器插件(CookieBro或EdittThisCookie)或者直接在地址栏网站链接信息处都可以复制或者导出cookie内容，
# 并填写到以上json文件的相应字段中
def load_javdb_cookies():
    try:
        javdb = scrapingConfService.getSetting().cookies_javdb
        cookies = load_cookies(javdb)
        return cookies
    except:
        return None


def load_javlib_cookies():
    try:
        javlib = scrapingConfService.getSetting().cookies_javlib
        cookies = load_cookies(javlib)
        return cookies
    except:
        return None


def load_cookies(rawcookie):
    cookie = SimpleCookie()
    cookie.load(rawcookie)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


# 文件修改时间距此时的天数
def file_modification_days(filename) -> int:
    mfile = pathlib.Path(filename)
    if not mfile.exists():
        return 9999
    mtime = int(mfile.stat().st_mtime)
    now = int(time.time())
    days = int((now - mtime) / (24 * 60 * 60))
    if days < 0:
        return 9999
    return days


def is_link(filename: str):
    """ 检查文件是否是链接
    """
    if os.path.islink(filename):
        return True # symlink
    elif os.stat(filename).st_nlink > 1:
        return True # hard link Linux MAC OSX Windows NTFS
    return False


def abs_url(base_url: str, href: str) -> str:
    """ URL相对路径转绝对路径
    """
    if href.startswith('http'):
        return href
    return urljoin(base_url, href)
