import re
import pycurl
from io import BytesIO
from bs4 import BeautifulSoup
import json

url = "https://www.olx.ua/obyavlenie/turan-2010-IDDHRat.html"
b = BytesIO()
c = pycurl.Curl()
cookie_path = 'cookie.dat'
ID = re.findall("-ID(.*?)\.html", url)[0]
print(ID)
c.setopt(pycurl.URL, url)
c.setopt(pycurl.SSL_VERIFYPEER, False)
c.setopt(pycurl.WRITEFUNCTION, b.write)
c.setopt(pycurl.HEADER, 1)
c.setopt(pycurl.COOKIEFILE, cookie_path)
c.setopt(pycurl.COOKIEJAR, cookie_path)
c.perform()
c.close()
data = b.getvalue()
soup = BeautifulSoup(data, "html.parser")
phoneToken = re.findall("var phoneToken = '(.*?)'", soup.text)[0]
phone_url = 'https://www.olx.ua/ajax/misc/contact/phone/{0}/?pt={1}'.format(ID, phoneToken)
print(phoneToken)
bb = BytesIO()
c = pycurl.Curl()
c.setopt(pycurl.URL, phone_url)
c.setopt(pycurl.HTTPHEADER, [
    'Host: www.olx.ua',
    'Accept: */*',
    'Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding: gzip, deflate, br',
    'Connection: keep-alive',
    'X-Requested-With: XMLHttpRequest'
])
c.setopt(pycurl.WRITEFUNCTION, bb.write)
c.setopt(pycurl.REFERER, url)
c.setopt(pycurl.COOKIEFILE, cookie_path)
c.setopt(pycurl.SSL_VERIFYPEER, False)
c.setopt(pycurl.USERAGENT,
         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.170')
c.perform()
c.close()
data = bb.getvalue()
# try:
# json_data = json.loads(data)
# phoneNumber = json_data['value']
# except:
#     phoneNumber = 'Перевірте номер за посиланням оголошення'
print(data)
