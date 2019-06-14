import requests
import json
import string

from bs4 import BeautifulSoup

from main.models import *

from django.utils.timezone import get_current_timezone
from datetime import datetime
tz = get_current_timezone()

# Оставляет в строке только цифры
class DigitsMixin:
    def __init__(self, keep=string.digits):
        self.comp = dict((ord(c),c) for c in keep)
    def __getitem__(self, k):
        return self.comp.get(k)

OD = DigitsMixin()


class Rst:
    url = 'http://rst.ua/oldcars/?task=newresults&make%5B%5D=0&year%5B%5D=0&year%5B%5D=0&price%5B%5D=0&price%5B%5D=0\
    &engine%5B%5D=0&engine%5B%5D=0&gear=0&fuel=0&drive=0&condition=0&from=sform&start={}'
    pages = 10
    all_data = []

    def __init__(self):
        self.data_record()

    # получает содерждимое страницы
    def get_page(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(url, headers=headers)
        return r.text

    # получает список урлов объявлений на одной страничке
    def get_ads_on_page(self, html):
        soup = BeautifulSoup(html, 'lxml')

        # TODO : возможно можно одниой строкой их найти, не нашел как
        ads_1 = soup.find('div', class_='rst-page-wrap').find_all('div', class_='rst-ocb-i rst-ocb-i-premium rst-uix-radius')
        ads_2 = soup.find('div', class_='rst-page-wrap').find_all('div', class_='rst-ocb-i rst-ocb-i-premium rst-uix-radius rst-ocb-i-crash')
        ads_3 = soup.find('div', class_='rst-page-wrap').find_all('div', class_='rst-ocb-i rst-ocb-i-premium rst-uix-radius rst-ocb-i-blue')

        ad_url_list = []

        for ad in ads_1:
            href = 'http://rst.ua' + ad.find('a', class_='rst-ocb-i-a')['href']
            ad_url_list.append(href)

        for ad in ads_2:
            href = 'http://rst.ua' + ad.find('a', class_='rst-ocb-i-a')['href']
            ad_url_list.append(href)

        for ad in ads_3:
            href = 'http://rst.ua' + ad.find('a', class_='rst-ocb-i-a')['href']
            ad_url_list.append(href)
        
        return ad_url_list

    # получает список урлов объявлений со всех страниц
    def get_url_list(self):
        print('Start geting all ads')
        url_list = []
        for page in range(1, self.pages+1):
            print('get {} page'.format(page))
            url_list += self.get_ads_on_page(self.get_page(self.url.format(page)))
        return url_list

    # получает данные объявления
    def get_ad_data(self, url):
        soup = BeautifulSoup(self.get_page(url), 'lxml')

        # страницы объявлений есть друх типов: с tr-td и с li-span
        tds = soup.find('div', class_='rst-page-oldcars-item-option-block rst-uix-clear').find_all('td')
        spans = soup.find('div', class_='rst-page-oldcars-item-option-block rst-uix-clear').find_all('span')

        for td in tds:
            if td.text == 'Цена':
                try:
                    price = td.find_next_sibling('td').find('span').find('strong').text.translate(OD)
                    price_dol = td.find_next_sibling('td').find('span').find('span').text.translate(OD)
                except:
                    price = 'torg'
                    price_dol = 'torg'

            elif td.text == 'Год выпуска':
                year = td.find_next_sibling('td').find('a').text.translate(OD)
                mileage = td.find_next_sibling('td').find('span').text.translate(OD)
            
            elif td.text == 'Двигатель':
                engine = td.find_next_sibling('td').find('strong').text
                try:
                    fuel = td.find_next_sibling('td').find('span').text.replace('(','').replace(')','')
                except: fuel = ''

            elif td.text == 'КПП':
                gearbox = td.find_next_sibling('td').find('strong').text
                try:
                    drive = td.find_next_sibling('td').find('span').text.replace('(','').split()[0]
                except: drive = ''

            elif td.text == 'Тип кузова':
                body = td.find_next_sibling('td').find('strong').text
                try:
                    color = td.find_next_sibling('td').find('span').text.replace(')','').split()[-1]
                except: color = ''

            elif td.text == 'Область':
                location = td.find_next_sibling('td').find('a').text
                try:
                    location_city = td.find_next_sibling('td').find('span').find('a').text.replace(')','').split()[-1]
                except: location_city = ''

            elif td.text == 'Дата добавления':
                created = td.find_next_sibling('td').find('span').text
                createAt = tz.localize(datetime.strptime(created, '%d.%m.%Y'))

        for span in spans:
            if span.text == 'Цена':
                try:
                    price = span.find_next_sibling('span').find('span').find('strong').text.translate(OD)
                    price_dol = span.find_next_sibling('span').find('span').find('span').text.translate(OD)
                except:
                    price = 'torg'
                    price_dol = 'torg'

            elif span.text == 'Год выпуска':
                year = span.find_next_sibling('span').find('a').text.translate(OD)
                mileage = span.find_next_sibling('span').find('span').text.translate(OD)
            
            elif span.text == 'Двигатель':
                engine = span.find_next_sibling('span').find('strong').text
                try:
                    fuel = span.find_next_sibling('span').find('span').text.replace('(','').replace(')','')
                except: fuel = ''

            elif span.text == 'КПП':
                gearbox = span.find_next_sibling('span').find('strong').text
                try:
                    drive = span.find_next_sibling('span').find('span').text.replace('(','').split()[0]
                except: drive = ''

            elif span.text == 'Тип кузова':
                body = span.find_next_sibling('span').find('strong').text
                try:
                    color = span.find_next_sibling('span').find('span').text.replace(')','').split()[-1]
                except: color = ''

            elif span.text == 'Область':
                location = span.find_next_sibling('span').find('a').text
                try:
                    location_city = span.find_next_sibling('span').find('span').find('a').text.replace(')','').split()[-1]
                except: location_city = ''

            elif span.text == 'Дата добавления':
                created = span.find_next_sibling('span').find('span').text
                createAt = tz.localize(datetime.strptime(created, '%d.%m.%Y'))

        mark_model = soup.find('div', class_='rst-uix-page-tree rst-uix-radius').find('a').find_next_sibling('a').find_next_sibling('a').find_next_sibling('a').text

        mark = mark_model.split()[0]
        model = mark_model.split()[1]

        try:
            description = soup.find('div', class_='rst-page-oldcars-item-option-block-container rst-page-oldcars-item-option-block-container-desc rst-uix-block-more').text.strip()
        except: description = ''

        images = []
        images_soup = soup.find_all('a', class_='rst-uix-float-left rst-uix-radius')
        for image in images_soup:
            images.append(image['href'])
        try:
            image = images_soup[0]['href']
        except:
            image = 'no such image'

        try:
            soup.find('em', text="После ДТП").text
            dtp = True
        except: dtp = False

        name = soup.find('div', class_='rst-page-oldcars-item-option-block-container rst-uix-progress').find('stong').text.split()[0]

        data = {
            'year': year,
            'mileage': mileage,
            'engine': engine,
            'description': description,
            'price': price,
            'price_dol': price_dol,
            'drive': drive,
            'dtp': dtp,
            'created': created,
            'createAt': createAt,
            'image': image,
            'images': images,
            'rst_link': url,
            'mark': mark,
            'model': model,
            'gearbox': gearbox,
            'location': location,
            'location_city': location_city,
            'fuel': fuel,
            'color': color,
            'body': body,
            'phone': 'phone',
            'name': name,
        }
        return data

    # запись в базу
    def data_record(self):
        url_list = self.get_url_list()
        count = len(url_list) - 1
        for url in url_list:
            print('Start parsing {}'.format(url))
            # self.all_data.append(self.get_ad_data(url))
            data = self.get_ad_data(url)

            try:
                model = Model.objects.get(name=data['model'])
            except:
                Model.objects.create(name=data['model'])
                model = Model.objects.get(name=data['model'])

            try:
                mark = Mark.objects.get(name=data['mark'])
            except:
                Mark.objects.create(name=data['mark'], model=model)
                mark = Mark.objects.get(name=data['mark'])

            try:
                gearbox = Gearbox.objects.get(name=data['gearbox'])
            except:
                Gearbox.objects.create(name=data['gearbox'])
                gearbox = Gearbox.objects.get(name=data['gearbox'])

            try:
                location = Location.objects.get(region=data['location'])
            except:
                Location.objects.create(region=data['location'])
                location = Location.objects.get(region=data['location'])

            try:
                fuel = Fuel.objects.get(name=data['fuel'])
            except:
                Fuel.objects.create(name=data['fuel'])
                fuel = Fuel.objects.get(name=data['fuel'])

            try:
                color = Color.objects.get(name=data['color'])
            except:
                Color.objects.create(name=data['color'])
                color = Color.objects.get(name=data['color'])

            try:
                seller_phone = SellerPhone.objects.get(phone=data['phone'])
            except:
                SellerPhone.objects.create(phone=data['phone'])
                seller_phone = SellerPhone.objects.get(phone=data['phone'])

            try:
                body = Body.objects.get(name=data['body'])
            except:
                Body.objects.create(name=data['body'])
                body = Body.objects.get(name=data['body'])

            try:
                Car.objects.get(rst_link=data['rst_link'])
            except:
                car = Car.objects.create(model=model,
                                    gearbox=gearbox,
                                    location=location,
                                    fuel=fuel,
                                    color=color,
                                    year=data['year'],
                                    mileage=data['mileage'],
                                    engine=data['engine'],
                                    description=data['description'],
                                    price=data['price'],
                                    phone=seller_phone,
                                    body=body,
                                    image=data['image'],
                                    dtp=data['dtp'],
                                    createdAt=data['createAt'],
                                    rst_link=data['rst_link']
                                    )
                car.save()
                print('Object created, id = {}'.format(car.id))

            print('{} left'.format(count))
            count -= 1
        print('FINISHED')
        return self.all_data
