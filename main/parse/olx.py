import requests
from time import sleep
from lxml import html
from pprint import pprint
from lxml.etree import tostring
from selenium.webdriver import Firefox
import threading
from selenium.webdriver.firefox.options import Options

URL = 'https://www.olx.ua/transport/legkovye-avtomobili/'
URL_PAGING = '?page={}'
adverting_urls = []
el = []
page_numbers = range(1, 500)
list_urls = [URL + URL_PAGING.format(i) for i in page_numbers]

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)

options = Options()
options.headless = True
pprint('Browser opens')
driver = Firefox(executable_path='./webdriver/geckodriver.exe', options=options)
sleep(10)


def get_adverting_links(url):
    expression = '//*[@id="offers_table"]/tbody/tr/td/div/table/tbody/tr/td/div/h3/a/@href'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    for i in url:
        req = requests.get(i, headers=headers)
        body = html.document_fromstring(req.text)

        for _url in body.xpath(expression):
            adverting_urls.append(_url)

    # return adverting_urls


def get_car_data(url):
    exspression = '//*[@id="offeractions"]/div[1]/strong/text()'
    for i in url:
        driver.get(i)
        els = driver.find_element_by_xpath(exspression)
        el.append(els)
    # driver.close()


threads = list()
threads.append(threading.Thread(target=get_adverting_links, args=(list_urls[len(list_urls) // 2:],)))
threads.append(threading.Thread(target=get_adverting_links, args=(list_urls[:len(list_urls) // 2],)))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

# threads = list()
# threads.append(threading.Thread(target=get_car_data, args=(adverting_urls[len(adverting_urls)//2:],)))
# threads.append(threading.Thread(target=get_car_data, args=(adverting_urls[:len(adverting_urls)//2],)))
#
# for thread in threads:
#     thread.start()
#
# for thread in threads:
#     thread.join()

pprint(adverting_urls)
pprint(el)

driver.close()
