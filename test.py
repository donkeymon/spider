import requests
import re
import base
import time
from fake_useragent import UserAgent

# start = time.clock()
# print(base.get_ip_info({'http': '61.135.217.7:80'}))
# end = time.clock()
# print(end - start)

file_handler = open('good_proxy.txt', 'r')
proxies_line = file_handler.read()
proxies = proxies_line.split(',')
proxies.pop()
file_handler.close()
for proxy in proxies:
    print(base.get_ip_info(eval(proxy)) + ' ' + proxy)
