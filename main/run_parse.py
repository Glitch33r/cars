import time
import requests
from lxml import html
from main.parse.olx import OLX
from threading import Thread


URL = 'https://www.olx.ua/transport/legkovye-avtomobili/'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.109'
URL_PAGING = '?page={}'
page_numbers = range(2, 500)
list_pages = [URL + URL_PAGING.format(i) for i in page_numbers]
list_pages.append(URL)


def process(urls):
    for url in urls:
        page = requests.get(url, headers={'User-Agent': user_agent})
        web_page = html.fromstring(page.content)
        posts_list = web_page.xpath('//a[contains(@class, "marginright5 link linkWithHash detailsLink")]/@href')
        time.sleep(1)
        for idx, post_url in enumerate(posts_list):
            print(f'link #{idx}')
            olx = OLX(post_url)
            olx.start()
            del olx


thr_1 = Thread(target=process, args=(list_pages[0:50], ))
# thr_2 = Thread(target=process, args=(list_pages[151:350], ))
# thr_3 = Thread(target=process, args=(list_pages[351:500], ))
thr_1.start()
# thr_2.start()
# thr_3.start()


thr_1.join()
# thr_2.join()
# thr_3.join()