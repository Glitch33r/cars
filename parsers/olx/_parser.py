from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from fake_useragent import UserAgent


class OLXInner:
    proxy = {
        'address1': '45.67.120.4:30032',
        'address2': '45.67.120.6:30032',
        'address3': '45.67.123.107:30032',
        'address4': '45.67.123.13:30032',
        'address5': '45.67.120.171:30032',
        'username': 'jorjclub0420_gmail_c',
        'password': '2c752798d6'}
    driver = None
    links_of_post = []
    base_way = 'https://www.olx.ua/transport/legkovye-avtomobili/?page={}'

    def __init__(self, start, finish, numb):
        self.set_driver(numb)
        self.run(start, finish)

    def run(self, start, finish):
        for page in range(start, finish):
            self.driver.get(self.base_way.format(page))
            self.stack_links()


    def stack_links(self):
        self.links_of_post = []
        for row in range(1, 40):
            try:
                self.links_of_post.append(self.driver.find_element_by_xpath(
                    f'//*[@id="offers_table"]/tbody/tr[{row}]/td/div/table/tbody/tr[1]/td[2]/div/h3/a').get_attribute(
                    'href'))
            except NoSuchElementException:
                pass

    def set_driver(self, numb):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--proxy={self.proxy[f"address{numb}"]}')
        chrome_options.add_argument(f'--proxy-auth={self.proxy["username"]}:{self.proxy["password"]}')
        chrome_options.headless = True
        ua = UserAgent()
        chrome_options.add_argument(f'user-agent={ua.random}')
        self.driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options)
