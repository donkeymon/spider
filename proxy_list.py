import base
import requests
import random
import threading
import multiprocessing
import re
import os
from fake_useragent import UserAgent
from multiprocessing import Process, Pool
from threading import Thread
from urllib.request import ProxyHandler, build_opener
from urllib.error import URLError
from requests.exceptions import HTTPError, ConnectTimeout, ProxyError

THREAD_NUMBER = 40
PROCESS_NUMBER = 4
BASE_URL = 'http://www.xicidaili.com/nn/{0}'
PATTERN = '''<td class=".*"><img src=".*" alt=".*" /></td>
      <td>(.*)</td>
      <td>(.*)</td>
      <td>
        <a href=".*">.*</a>
      </td>
      <td class=".*">.*</td>
      <td>(.*)</td>'''

PROXY_FILE = 'proxy.txt'
WORK_PROXY_FILE = 'work_proxy.txt'
GOOD_PROXY_FILE = 'good_proxy.txt'
WORK_PROXY_TIMEOUT = 5
GOOD_PROXY_TIMEOUT = 3
MAX_PAGE = 400

THREAD_LOCK = threading.Lock()

def get_headers():
    return {
        'User-Agent': UserAgent().random
    }


def get_proxies_by_page(page, proxies):
    headers = get_headers()
    url = BASE_URL.format(page)

    # urllib
    # request = base.get_request(url = url, headers = headers)
    # html = base.get_html(request)

    # requests
    html = requests.get(url, headers = headers).text
    match_result = re.findall(PATTERN, html)
    THREAD_LOCK.acquire()
    file_handler = open(PROXY_FILE, 'a')
    for proxy in match_result:
        file_handler.write("{{'{0}': '{1}:{2}'}},".format(proxy[2].lower(), proxy[0], proxy[1]))
        proxies.append({proxy[2].lower(): proxy[0] + ':' + proxy[1]})
    file_handler.close()
    THREAD_LOCK.release()


def is_work_proxy(proxy, work_proxies = []):
    try:
        res = requests.get(base.NET_CN_GET_IP_URL, get_headers(), proxies = proxy, timeout = WORK_PROXY_TIMEOUT)
        res.raise_for_status()
    except HTTPError:
        print('not work proxy ' + str(proxy) + ' http_error')
        return False
    except ConnectTimeout:
        print('not work proxy ' + str(proxy) + ' connect_timeout')
        return False
    except ProxyError:
        print('not work proxy ' + str(proxy) + ' proxy_error')
        return False
    except Exception:
        print('not work proxy ' + str(proxy) + ' unknown error')
        return False
    else:
        THREAD_LOCK.acquire()
        file_handler = open(WORK_PROXY_FILE, 'a')
        file_handler.write(str(proxy) + ',')
        file_handler.close()
        work_proxies.append(proxy)
        THREAD_LOCK.release()
        print('is work proxy  ' + str(proxy))
        return True


def is_good_proxy(proxy, good_proxies = []):
    if proxy not in good_proxies:
        get_ip_url = base.GET_IP_URL_MAP.get(0)
        error_msg = ''
        # 重试4次
        for i in range(4):
            try:
                res = requests.get(get_ip_url, get_headers(), proxies = proxy, timeout = GOOD_PROXY_TIMEOUT)
                res.raise_for_status()
            except ConnectTimeout:
                error_msg = 'connect_timeout'
                pass
            except Exception:
                error_msg = 'unknown_error'
                pass
            else:
                find_detect_ip = re.findall('\d+\.\d+\.\d+\.\d+', res.text)
                if not find_detect_ip:
                    error_msg = 'detect_ip_error'
                    get_ip_url = base.GET_IP_URL_MAP.get(i)
                    detect_ip = ''
                else:
                    detect_ip = find_detect_ip[0]

                proxy_ip = (proxy.get('http') or proxy.get('https')).split(':')[0]
                if proxy_ip == detect_ip:
                    THREAD_LOCK.acquire()
                    file_handler = open(GOOD_PROXY_FILE, 'a')
                    file_handler.write(str(proxy) + ',')
                    file_handler.close()
                    good_proxies.append(proxy)
                    THREAD_LOCK.release()
                    print('is good proxy  {0}'.format(str(proxy)))
                    return True
                else:
                    error_msg = 'not_through_proxy'

        print('not good proxy {0} {1}'.format(str(proxy), error_msg))
        return False


def read_proxies(file_name):
    try:
        file_handler = open(file_name, 'r')
        proxies_line = file_handler.read()
        proxies = proxies_line.split(',')
        proxies.pop()
        file_handler.close()

        for i in range(len(proxies)):
            proxies[i] = base.proxy_format(proxies[i])
        return proxies
    except Exception:
        return []


def random_proxy():
    proxies = read_proxies(GOOD_PROXY_FILE)
    return random.choice(proxies)


def test_good_proxy():
    good_proxies = read_proxies(GOOD_PROXY_FILE)
    for proxy in good_proxies:
        print('detect_ip: {0}   proxy: {1}'.format(base.get_ip_info(base.proxy_format(proxy)), proxy))


# def main():
    # 单线程
    # for page in range(1, MAX_PAGE):
    #     get_good_proxies_by_page(page)

    # 多线程
    # proxies = []
    # for page in range(1, MAX_PAGE, THREAD_NUMBER):
    #     threads = []
    #     for i in range(THREAD_NUMBER):
    #         threads.append(Thread(target = get_proxies_by_page, args = (page + i, proxies)))
    #     for i in range(THREAD_NUMBER):
    #         threads[i].start()
    #     for i in range(THREAD_NUMBER):
    #         threads[i].join()

    # proxies = read_proxies(PROXY_FILE)
    # for i in range(0, len(proxies), THREAD_NUMBER):
    #     threads = []
    #     for j in range(THREAD_NUMBER):
    #         threads.append(Thread(target = is_good_proxy, args = (base.proxy_format(proxies[i + j]),)))
    #     for j in range(THREAD_NUMBER):
    #         threads[j].start()
    #     for j in range(THREAD_NUMBER):
    #         threads[j].join()

    # 多进程
    # if __name__ == '__main__':
    #     for page in range(1, MAX_PAGE, PROCESS_NUMBER):
    #             processes = []
    #             for i in range(PROCESS_NUMBER):
    #                 processes.append(Process(target = get_good_proxies_by_page, args = (page + i,)))
    #             for i in range(PROCESS_NUMBER):
    #                 processes[i].start()

    # 多进程 进程池
    # if __name__ == '__main__':
    #     pool = Pool(4)
    #     for page in range(1, MAX_PAGE, PROCESS_NUMBER):
    #         for i in range(PROCESS_NUMBER):
    #             pool.apply_async(get_good_proxies_by_page, args = (page + i,))
    #     pool.close()
    #     pool.join()

def get_proxies_to_file(restart = False):
    if os.path.exists(PROXY_FILE):
        if restart:
            os.unlink(PROXY_FILE)
        else:
            return read_proxies(PROXY_FILE)

    proxies = []
    for page in range(1, MAX_PAGE, THREAD_NUMBER):
        threads = []
        for i in range(THREAD_NUMBER):
            if page + i <= MAX_PAGE:
                threads.append(Thread(target = get_proxies_by_page, args = (page + i, proxies)))
        for i in range(len(threads)):
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()
    return proxies


def get_work_proxies_to_file(restart = False):
    if os.path.exists(WORK_PROXY_FILE):
        if restart:
            os.unlink(WORK_PROXY_FILE)
        else:
            return read_proxies(WORK_PROXY_FILE)

    proxies = read_proxies(PROXY_FILE)
    work_proxies = []
    for i in range(0, len(proxies), THREAD_NUMBER):
        threads = []
        for j in range(THREAD_NUMBER):
            if i + j < len(proxies):
                threads.append(Thread(target = is_work_proxy, args = (base.proxy_format(proxies[i + j]), work_proxies)))
        for j in range(len(threads)):
            threads[j].start()
        for j in range(len(threads)):
            threads[j].join()
    return work_proxies


def get_good_proxies_to_file(restart = False):
    if os.path.exists(GOOD_PROXY_FILE):
        if restart:
            good_proxies = read_proxies(GOOD_PROXY_FILE)
        else:
            return read_proxies(GOOD_PROXY_FILE)
    else:
        good_proxies = []

    work_proxies = read_proxies(WORK_PROXY_FILE)
    for i in range(0, len(work_proxies), THREAD_NUMBER):
        threads = []
        for j in range(THREAD_NUMBER):
            if i + j < len(work_proxies):
                threads.append(Thread(target = is_good_proxy, args = (base.proxy_format(work_proxies[i + j]), good_proxies)))
        for j in range(len(threads)):
            threads[j].start()
        for j in range(len(threads)):
            threads[j].join()
    return good_proxies

get_proxies_to_file()
get_work_proxies_to_file()
get_good_proxies_to_file()
