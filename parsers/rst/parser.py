import requests
import random
import json
import string
from time import sleep

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

    def __init__(self, pages):
        self.pages = pages
        self.data_record()

    # получает содерждимое страницы
    def get_page(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup

    # получает список урлов объявлений на одной страничке
    def get_ads_on_page(self, url):
        soup = self.get_page(url)

        ad_url_list = []

        # TODO : возможно можно одниой строкой их найти, не нашел как
        try:
            ads_1 = soup.find('div', class_='rst-page-wrap').find_all('div', class_='rst-ocb-i rst-ocb-i-premium rst-uix-radius')
            for ad in ads_1:
                href = 'http://rst.ua' + ad.find('a', class_='rst-ocb-i-a')['href']
                ad_url_list.append(href)
        except: pass

        try:
            ads_2 = soup.find('div', class_='rst-page-wrap').find_all('div', class_='rst-ocb-i rst-ocb-i-premium rst-uix-radius rst-ocb-i-crash')
            for ad in ads_2:
                href = 'http://rst.ua' + ad.find('a', class_='rst-ocb-i-a')['href']
                ad_url_list.append(href)
        except: pass

        try:
            ads_3 = soup.find('div', class_='rst-page-wrap').find_all('div', class_='rst-ocb-i rst-ocb-i-premium rst-uix-radius rst-ocb-i-blue')
            for ad in ads_3:
                href = 'http://rst.ua' + ad.find('a', class_='rst-ocb-i-a')['href']
                ad_url_list.append(href)
        except: pass

        return ad_url_list

    # получает данные объявления
    def get_ad_data(self, url):
        soup = self.get_page(url)

        # страницы объявлений есть друх типов: с tr-td и с li-span
        tds = soup.find('div', class_='rst-page-oldcars-item-option-block rst-uix-clear').find_all('td')
        spans = soup.find('div', class_='rst-page-oldcars-item-option-block rst-uix-clear').find_all('span')

        for td in tds:
            if td.text == 'Цена':
                try:
                    price_hrn = td.find_next_sibling('td').find('span').find('strong').text.translate(OD)
                    price = td.find_next_sibling('td').find('span').find('span').text.translate(OD)
                except:
                    price_hrn = 0
                    price = 0

            elif td.text == 'Год выпуска':
                year = td.find_next_sibling('td').find('a').text.translate(OD)
                mileage = td.find_next_sibling('td').find('span').text.translate(OD)
            
            elif td.text == 'Двигатель':
                engine = float(td.find_next_sibling('td').find('strong').text[:3]) if td.find_next_sibling('td').find('strong').text else ''
                try:
                    fuel = td.find_next_sibling('td').find('span').text.replace('(','').replace(')','').lower()
                except: fuel = ''

            elif td.text == 'КПП':
                gearbox = td.find_next_sibling('td').find('strong').text.split()[0]
                try:
                    drive = td.find_next_sibling('td').find('span').text.replace('(','').split()[0]
                except: drive = ''

            elif td.text == 'Тип кузова':
                body = td.find_next_sibling('td').find('strong').text.split()[0]
                try:
                    color = td.find_next_sibling('td').find('span').text.replace(')','').split()[-1].lower()
                except: color = ''

            elif td.text == 'Область':
                location = td.find_next_sibling('td').find('a').text
                try:
                    location_city = td.find_next_sibling('td').find('span').find('a').text.replace(')','').split()[-1]
                except: location_city = ''

            elif td.text == 'Дата добавления':
                created = td.find_next_sibling('td').find('span').text
                last_site_updatedAt = tz.localize(datetime.strptime(created, '%d.%m.%Y'))

        for span in spans:
            if span.text == 'Цена':
                try:
                    price_hrn = span.find_next_sibling('span').find('span').find('strong').text.translate(OD)
                    price = span.find_next_sibling('span').find('span').find('span').text.translate(OD)
                except:
                    price_hrn = 0
                    price = 0

            elif span.text == 'Год выпуска':
                year = span.find_next_sibling('span').find('a').text.translate(OD)
                mileage = span.find_next_sibling('span').find('span').text.translate(OD)
            
            elif span.text == 'Двигатель':
                engine = float(span.find_next_sibling('span').find('strong').text[:3]) if span.find_next_sibling('span').find('strong').text else ''
                try:
                    fuel = span.find_next_sibling('span').find('span').text.replace('(','').replace(')','').lower()
                except: fuel = ''

            elif span.text == 'КПП':
                gearbox = span.find_next_sibling('span').find('strong').text.split()[0]
                try:
                    drive = span.find_next_sibling('span').find('span').text.replace('(','').split()[0]
                except: drive = ''

            elif span.text == 'Тип кузова':
                body = span.find_next_sibling('span').find('strong').text.split()[0]
                try:
                    color = span.find_next_sibling('span').find('span').text.replace(')','').split()[-1].lower()
                except: color = ''

            elif span.text == 'Область':
                location = span.find_next_sibling('span').find('a').text
                try:
                    location_city = span.find_next_sibling('span').find('span').find('a').text.replace(')','').split()[-1]
                except: location_city = ''

            elif span.text == 'Дата добавления':
                created = span.find_next_sibling('span').find('span').text
                last_site_updatedAt = tz.localize(datetime.strptime(created, '%d.%m.%Y'))

        mark_model = soup.find('div', class_='rst-uix-page-tree rst-uix-radius').find('a').find_next_sibling('a').find_next_sibling('a').find_next_sibling('a').text

        mark = mark_model.split()[0].lower()
        model = mark_model.split()[1].lower()

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
            'price_hrn': price_hrn,
            'drive': drive,
            'dtp': dtp,
            'created': created,
            'last_site_updatedAt': last_site_updatedAt,
            'image': image,
            'images': images,
            'rst_link': url,
            'mark': mark,
            'model': model,
            'gearbox': gearbox.split()[0],
            'location': location,
            'location_city': location_city,
            'fuel': fuel,
            'color': color,
            'body': body,
            'name': name,
        }
        return data

    # запись в базу
    def data_record(self):

        for page in range(1, self.pages+1):
            print('get {} page'.format(page))
            sleep(random.randint(3, 5))
            for url in self.get_ads_on_page(self.url.format(page)):

                print('Start parsing {}'.format(url))
                sleep(random.randint(5, 10))

                data = self.get_ad_data(url)

                try:
                    mark = Mark.objects.get(name=data['mark'])
                except:
                    Mark.objects.create(name=data['mark'])
                    mark = Mark.objects.get(name=data['mark'])

                try:
                    model = Model.objects.get(name=data['model'])
                except:
                    Model.objects.create(name=data['model'], mark=mark)
                    model = Model.objects.get(name=data['model'])

                try:
                    gearbox = Gearbox.objects.get(name=data['gearbox'])
                except:
                    Gearbox.objects.create(name=data['gearbox'])
                    gearbox = Gearbox.objects.get(name=data['gearbox'])

                try:
                    location = Location.objects.get(name=data['location'])
                except:
                    Location.objects.create(name=data['location'])
                    location = Location.objects.get(name=data['location'])

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
                    body = Body.objects.get(name=data['body'])
                except:
                    Body.objects.create(name=data['body'])
                    body = Body.objects.get(name=data['body'])

                try:
                    try:
                        car = Car.objects.get(rst_link=data['rst_link'])
                        car.price = data['price']
                        car.updatedAt = tz.localize(datetime.now())
                        car.last_site_updatedAt = data['last_site_updatedAt']
                        car.save()
                        print('Price updated')
                    except:
                        car = Car.objects.get(model=model,
                                        gearbox=gearbox,
                                        location=location,
                                        fuel=fuel,
                                        color=color,
                                        year=data['year'],
                                        mileage=data['mileage'],
                                        engine=data['engine'],
                                        body=body,
                                        dtp=data['dtp']
                                        )
                        car.price = data['price']
                        car.rst_link = data['rst_link']
                        car.updatedAt = tz.localize(datetime.now())
                        car.last_site_updatedAt = data['last_site_updatedAt']
                        car.save()
                        print('Updated')
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
                                        phone=None,
                                        body=body,
                                        image=data['image'],
                                        dtp=data['dtp'],
                                        createdAt=tz.localize(datetime.now()),
                                        last_site_updatedAt=data['last_site_updatedAt'],
                                        rst_link=data['rst_link']
                                        )
                    car.save()
                    print('Object created')

        return print('FINISHED')