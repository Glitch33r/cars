import requests
from django.http import JsonResponse
from lxml import html
from time import sleep
from threading import Thread
from .parser import OLX


def run(request):
    url = 'https://www.olx.ua/transport/legkovye-avtomobili/'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.109'
    url_paging = '?page={}'
    page_numbers = range(2, 500)
    list_pages = [url + url_paging.format(i) for i in page_numbers]
    list_pages.append(url)

    def process(urls):
        for url_ in urls:
            page = requests.get(url_, headers={'User-Agent': user_agent})
            web_page = html.fromstring(page.content)
            posts_list = web_page.xpath('//a[contains(@class, "marginright5 link linkWithHash detailsLink")]/@href')
            sleep(1)
            for idx, post_url in enumerate(posts_list):
                print(f'link #{idx}')
                olx = OLX(post_url)
                olx.start()
                del olx

    thr_1 = Thread(target=process, args=(list_pages[0:50],))
    # thr_2 = Thread(target=process, args=(list_pages[151:350], ))
    # thr_3 = Thread(target=process, args=(list_pages[351:500], ))
    thr_1.start()
    # thr_2.start()
    # thr_3.start()

    thr_1.join()
    # thr_2.join()
    # thr_3.join()
    return JsonResponse(dict(status='success'))