import requests
import re
import base
import time
import proxy_list
from fake_useragent import UserAgent

# start = time.clock()
# print(base.get_ip_info({'http': '119.28.194.66:8888'}))
# end = time.clock()
# print(end - start)

# file_handler = open('good_proxy.txt', 'r')
# proxies_line = file_handler.read()
# proxies = proxies_line.split(',')
# proxies.pop()
# file_handler.close()
# for proxy in proxies:
#     print(base.get_ip_info(eval(proxy)) + ' ' + proxy)

proxy_list.test_good_proxy()