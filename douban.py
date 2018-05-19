import random
import time
import base

KEY_WORDS = ['钱江', '和谐', '九堡']

USE_PROXY = True
PROXY = {
    'http': 'http://127.0.0.1:1080'
}

BASE_URL = 'https://www.douban.com'
SUB_URL = '/group/HZhome/discussion?'
BASE_URL_M = 'https://m.douban.com'
SUB_URL_M = '/group/HZhome/?'


SPLITTER = '|'
BASE_PATTERN_M = '''<a href="(.*)" title="(.*)">
                        <h3 class=".*">
                            .*({0}).*'''
BASE_PATTERN = '''<a href="(.*)" title="(.*)" class="">
                       .*({0}).*
                    </a>'''

START = 0
MAX_START = 10000
FILE_NAME = '租房.txt'


def get_headers():
    return {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': 1,
        'User-Agent': random.choice(base.USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'DNT': 1,
        'Referer': 'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&tn=baidu&wd=%E8%B1%86%E7%93%A3%20%E6%9D%AD%E5%B7%9E%E7%A7%9F%E6%88%BF%E5%B0%8F%E7%BB%84&rsv_pq=dc4ab5760000d649&rsv_t=0dc0TLK5%2FGWiLLaM7UX284evhE8e8ZKlCz8k80aVXAZPo1TP4cG06X1wVgg&rqlang=cn&rsv_enter=1&rsv_sug3=31&rsv_sug1=27&rsv_sug7=100&rsv_sug2=0&inputT=3576&rsv_sug4=3577',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7',
        'Cookie': 'bid=J17yE_0QLd8; ap=1'
    }


def get_pattern():
    return BASE_PATTERN.format(SPLITTER.join(KEY_WORDS))


def main():
    pattern = get_pattern()
    start = START
    file_handler = open(FILE_NAME, 'a', encoding='utf-8')

    while start < MAX_START:
        headers = get_headers()
        url = BASE_URL + SUB_URL + 'start=' + str(start)
        request = base.get_request(url, headers)
        html = base.get_html(request)
        match_result = base.get_match_result(pattern, html)
        for info in match_result:
            print(str(start) + ' ' + info[0] + ' ' + info[1])
            file_handler.writelines(info[0] + ' ' + info[1] + "\n")
        start = start + 25
        time.sleep(round(random.choice(range(2, 4))))
        
    print('done')