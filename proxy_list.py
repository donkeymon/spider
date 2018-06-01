import base
import requests
import random
import threading
import re
import time
from fake_useragent import UserAgent
from threading import Thread
from requests.exceptions import HTTPError, ConnectTimeout, ProxyError


PROXY_SITES = [
    {
        'method': 'GET',
        'base_url': 'http://www.xicidaili.com/nn/{0}',
        'pattern': '<td>(\\d+.\\d+.\\d+.\\d+)</td>\\s*<td>(\\d+)</td>\\s*<td>\\s*<a href="[\\w\\-\\/]+">\\w+</a>\\s*</td>\\s*<td class="\\w+">\\w+</td>\\s*<td>(http|https|HTTP|HTTPS)</td>',
        'reg_sort': [2, 0, 1],
        'max_page': 4,
        'thread_number': 4,
        'proxy_to_file': False,
        'work_proxy_to_file': False,
        'good_proxy_to_file': True,
        'file_content_spliter': ','
    },
    {
        'method': 'POST',
        'base_url': 'https://www.proxydocker.com/zh/proxylist/country/China',
        'pattern': '<td>\\s*<a href="[\\/:\\.\\w]+">(\\d+.\\d+.\\d+.\\d+)</a>\\s*:(\\d+)\\s*</td>\\s*<td class="[\\w\-]+">\\s*(http|https|HTTP|HTTPS)\\s*</td>',
        'reg_sort': [2, 0, 1],
        'max_page': 40,
        'thread_number': 4,
        'proxy_to_file': False,
        'work_proxy_to_file': False,
        'good_proxy_to_file': True,
        'file_content_spliter': ',',
        'cookie': '__tawkuuid=e::proxydocker.com::r04oTuigKvBUDZ2kO7ls/J8Yh9CDrVMsm26SQxS+xp+wvWyWCGnELlpFdFs1lT9/::2; REMEMBERME=TWFpbkJ1bmRsZVxFbnRpdHlcVXNlcjpaRzl1YTJWNWJXOXU6MTUyNzkxMjU3Mjo2ZWE4YTQ2ODU3ODYwNGYzZThlY2E2M2EzODJjYjQxZDgyNDJkNWU0MDJiMTc3OWEyMGU1NmZhNGUyODkxMTYw; PHPSESSID=837e3dda37a5e311405969fc7f101a24; TawkConnectionTime=0'
    },
    {
        'method': 'GET',
        'base_url': 'http://www.data5u.com/free/gngn/index.shtml',
        'pattern': '<span>\\s*<li>(\\d+.\\d+.\\d+.\\d+)</li>\\s*</span>\\s*<span style="[:;\\w ]+">\\s*<li class="[\\w ]+">(\\d+)</li>\\s*</span>\\s*<span style="[:;\\w ]+">\\s*<li>\\s*<a class="\\w+" href="[\\.:\/\\w]+">\\w+</a>\\s*</li>\\s*</span>\\s*<span style="[:;\\w ]+">\\s*<li>\\s*<a class="\\w+" href="[\\.:\/\\w]+">(http|https|HTTP|HTTPS)</a>\\s*</li>\\s*</span>',
        'reg_sort': [2, 0, 1],
        'max_page': 1,
        'thread_number': 4,
        'proxy_to_file': False,
        'work_proxy_to_file': False,
        'good_proxy_to_file': True,
        'file_content_spliter': ','
    },
    {
        'method': 'GET',
        'base_url': 'http://www.data5u.com/free/gnpt/index.shtml',
        'pattern': '<span>\\s*<li>(\\d+.\\d+.\\d+.\\d+)</li>\\s*</span>\\s*<span style="[:;\\w ]+">\\s*<li class="[\\w ]+">(\\d+)</li>\\s*</span>\\s*<span style="[:;\\w ]+">\\s*<li>\\s*<a class="\\w+" href="[\\.:\/\\w]+">\\w+</a>\\s*</li>\\s*</span>\\s*<span style="[:;\\w ]+">\\s*<li>\\s*<a class="\\w+" href="[\\.:\/\\w]+">(http|https|HTTP|HTTPS)</a>\\s*</li>\\s*</span>',
        'reg_sort': [2, 0, 1],
        'max_page': 1,
        'thread_number': 4,
        'proxy_to_file': False,
        'work_proxy_to_file': False,
        'good_proxy_to_file': True,
        'file_content_spliter': ','
    },
    {
        'method': 'GET',
        'base_url': 'https://www.kuaidaili.com/free/inha/{0}/',
        'pattern': '<tr>\\s*<td data-title="IP">(\\d+.\\d+.\\d+.\\d+)</td>\\s*<td data-title="PORT">(\\d+)</td>\\s*<td data-title="\\w+">\\w+</td>\\s*<td data-title="\\w+">(http|https|HTTP|HTTPS)</td>',
        'reg_sort': [2, 0, 1],
        'max_page': 4,
        'thread_number': 1,
        'req_interval': 1.5,
        'proxy_to_file': False,
        'work_proxy_to_file': False,
        'good_proxy_to_file': True,
        'file_content_spliter': ',',
        'cookie': 'channelid=0; sid=1527810745853105'
    }
]


class ProxySite(object):

    def __init__(self, proxy_site = {}, work_proxy_timeout = 5, good_proxy_timeout = 3, proxy_to_file = False, work_proxy_to_file = False, good_proxy_to_file = True, file_content_spliter = ',', thread_number = 4, req_interval = 0):
        self.proxy_site = proxy_site
        self.method = proxy_site.get('method') and proxy_site.get('method').upper()
        self.base_url = proxy_site.get('base_url')
        self.pattern = proxy_site.get('pattern')
        self.reg_sort = proxy_site.get('reg_sort')
        self.max_page = proxy_site.get('max_page')
        self.cookie = proxy_site.get('cookie') or ''
        self.work_proxy_timeout = proxy_site.get('work_proxy_timeout') or work_proxy_timeout
        self.good_proxy_timeout = proxy_site.get('good_proxy_timeout') or good_proxy_timeout
        self.proxy_to_file = proxy_site.get('proxy_to_file') or proxy_to_file
        self.work_proxy_to_file = proxy_site.get('work_proxy_to_file') or work_proxy_to_file
        self.good_proxy_to_file = proxy_site.get('good_proxy_to_file') or good_proxy_to_file
        self.file_content_spliter = proxy_site.get('file_content_spliter') or file_content_spliter
        self.thread_number = proxy_site.get('thread_number') or thread_number
        self.req_interval = proxy_site.get('req_interval') or req_interval
        self.proxies = []
        self.work_proxies = []
        self.good_proxies = []
        self.user_agent_generator = UserAgent()
        self.thread_lock = threading.Lock()
        self.request_page_done = 0
        self.filter_proxy_done = 0
        self.filter_work_proxy_done = 0
        self.proxy_file = 'proxy.txt'
        self.work_proxy_file = 'work_proxy.txt'
        self.good_proxy_file = 'good_proxy.txt'

    def get_headers(self):
        return {
            'User-Agent': self.user_agent_generator.random,
            'Cookie': self.cookie,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'DNT': '1',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7'
        }

    def request(self, page):
        url = self.base_url.format(page)
        try:
            if self.method == 'GET':
                return requests.get(url, headers = self.get_headers(), verify = False).text
            elif self.method == 'POST':
                data = {
                    'page': page
                }
                return requests.post(url, headers = self.get_headers(), data = data).text
        except Exception:
            return ''

    def format_match_proxy(self, proxy):
        return {proxy[self.reg_sort[0]].lower(): "{0}:{1}".format(proxy[self.reg_sort[1]], proxy[self.reg_sort[2]])}

    def match(self, html):
        match_list = (re.findall(self.pattern, html))
        for proxy in match_list:
            self.proxies.append(self.format_match_proxy(proxy))
            print(self.format_match_proxy(proxy))
        self.request_page_done += 1

    def request_proxy_by_page(self, page):
        html = self.request(page)
        self.match(html)

    def request_proxy(self):
        for page in range(1, self.max_page + 1, self.thread_number):
            threads = []
            for i in range(self.thread_number):
                if page + i < self.max_page + 1:
                    threads.append(Thread(target = self.request_proxy_by_page, args = (page + i,)))
            for i in range(len(threads)):
                threads[i].start()
                time.sleep(self.req_interval)

    def filter_work_proxy(self):
        while True:
            if self.request_page_done < self.max_page:
                time.sleep(1)
                continue
            else:
                for i in range(0, len(self.proxies), self.thread_number):
                    threads = []
                    for j in range(self.thread_number):
                        if i + j < len(self.proxies):
                            threads.append(Thread(target = self.detect_work_proxy, args = (self.proxies[i + j],)))
                    for j in range(len(threads)):
                        threads[j].start()
                break

    def detect_work_proxy(self, proxy):
        is_work, msg = self.is_work_proxy(proxy)
        if is_work:
            self.work_proxies.append(proxy)
        print('{0} {1}'.format(str(proxy), msg))
        self.filter_proxy_done += 1

    def is_work_proxy(self, proxy):
        try:
            res = requests.get(base.GET_IP_URL_MAP.get(0), headers = self.get_headers(), proxies = proxy, timeout = self.work_proxy_timeout)
            res.raise_for_status()
        except HTTPError:
            return False, 'http_error'
        except ConnectTimeout:
            return False, 'connect_timeout'
        except ProxyError:
            return False, 'proxy_error'
        except Exception:
            return False, 'unknown_error'
        else:
            return True, 'work_proxy'

    def filter_good_proxy(self):
        while True:
            if self.filter_proxy_done < len(self.proxies):
                time.sleep(1)
                continue
            else:
                for i in range(0, len(self.work_proxies), self.thread_number):
                    threads = []
                    for j in range(self.thread_number):
                        if i + j < len(self.work_proxies):
                            threads.append(Thread(target = self.detect_good_proxy, args = (self.work_proxies[i + j],)))
                    for j in range(len(threads)):
                        threads[j].start()
                break

    def detect_good_proxy(self, proxy):
        is_good, msg = self.is_good_proxy(proxy)
        if is_good:
            self.good_proxies.append(proxy)
        print('{0} {1}'.format(str(proxy), msg))
        self.filter_work_proxy_done += 1

    def is_good_proxy(self, proxy):
        error_msg = ''
        # 重试4次
        for i in range(4):
            try:
                res = requests.get(base.GET_IP_URL_MAP.get(i), self.get_headers(), proxies = proxy, timeout = self.good_proxy_timeout)
                res.raise_for_status()
            except ConnectTimeout:
                error_msg = 'connect_timeout'
                continue
            except Exception:
                error_msg = 'unknown_error'
                continue
            else:
                find_detect_ip = re.findall('\\d+.\\d+.\\d+.\\d+', res.text)
                if not find_detect_ip:
                    error_msg = 'detect_ip_error'
                    detect_ip = ''
                else:
                    detect_ip = find_detect_ip[0]

                proxy_ip = (proxy.get('http') or proxy.get('https')).split(':')[0]
                if proxy_ip == detect_ip:
                    return True, 'good_proxy'
                else:
                    error_msg = 'not_through_proxy'

        return False, error_msg

    def write_proxy_to_file(self, proxies, file):
        file_handler = open(file, 'a')
        for proxy in proxies:
            file_handler.write(str(proxy) + self.file_content_spliter)
        file_handler.close()

    def read_good_proxy(self):
        file_handler = open(self.good_proxy_file, 'r')
        file_content = file_handler.read()
        good_proxies = file_content.split(self.file_content_spliter)
        good_proxies.pop()
        for i in range(len(good_proxies)):
            good_proxies[i] = eval(good_proxies[i])
        self.good_proxies = good_proxies
        return good_proxies

    def done_it(self):
        while True:
            if self.filter_work_proxy_done < len(self.work_proxies):
                time.sleep(1)
                continue
            else:
                if self.proxy_to_file:
                    self.write_proxy_to_file(self.proxies, self.proxy_file)
                if self.work_proxy_to_file:
                    self.write_proxy_to_file(self.work_proxies, self.work_proxy_file)
                if self.good_proxy_to_file:
                    self.write_proxy_to_file(self.good_proxies, self.good_proxy_file)
                print('proxies: {0}, work_proxies: {1}, good_proxies: {2}'.format(len(self.proxies), len(self.work_proxies), len(self.good_proxies)))
                break

    def start_fuck(self):
        self.request_proxy()
        self.filter_work_proxy()
        self.filter_good_proxy()
        self.done_it()


for site in PROXY_SITES:
    proxy_site = ProxySite(site)
    proxy_site.start_fuck()