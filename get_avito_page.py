import logging
import requests
import random
import time
from bs4 import BeautifulSoup
import lxml

fake_header =  { 'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36' }

def get_item_data(html_text):
    """ парсер индивидуальной страницы с товаром, без нормальзации полей """
    soup = BeautifulSoup(html_text, 'lxml')
    #наименование товара
    item_name = soup.findAll("span", {"class": "title-info-title-text"})[0].next
    #номер объявления - пока некрасивый, как буду писать в базу нужно номализовать
    num_sign = soup.findAll("span", {"data-marker": "item-view/item-id"})
    #они бывают пустыми как выяснилось
    if len(num_sign):
        num_sign = num_sign[0].next
    else:
        num_sign = ''
    #дата подачи объявления - они прколисты, придется писать парсер времени авито-времени
    date_sign = soup.findAll("div", {"class": "title-info-metadata-item-redesign"})
    #она тоже бывает пустой
    if len(date_sign):
        date_sign = date_sign[0].next
    else:
        date_sign = ''
    #варим в супе все ссылки на фотки с товаром
    img_path = soup.findAll("div", {"class": "gallery-img-frame js-gallery-img-frame"})
    #получаем список картинок
    img_urls = [img.attrs['data-url'] for img in img_path]
    #варим в супе адрес
    addr = soup.findAll("span", {"class": "item-address__string"})
    #были объявления без адреса
    if len(addr):
        addr = addr[0].next
    else:
        addr = ''
    #варим в супе цену
    price = soup.findAll("span", {"class": "js-item-price"})
    #обратить внимаение иногда вываривается несколько цен - возмножно для индикатора роста или падения
    if len(price):
        price = price[0].next
    else:
        price = ''
    #сообщения к объявлению
    message_text = soup.findAll("div", {"class": "item-description-text"})
    #формат полное безумие включая набор смайлов, в utf-8
    if len(message_text):
        message_text = message_text[0].find_all('p')[0].next
    else:
        message_text = ''
    #Ниже временная фигня для записи строки в файл и визуального контроля 
    str1 = item_name + ';' + num_sign + ';' + date_sign + ';' + img_urls[0] + ';' + addr + ';' + price + ';' + message_text
    str2 = ''
    for i in str1:
        if i != '\n':
            str2 += i
    str2 += '\n'
    print(str2)
    with open('out.csv', 'a+',encoding='utf-8') as of:
        of.write(str2)
    #конец временной фигни для записи в файл и визуального контроля


def get_item_page(postfix_url):
    """ парсер индивидуальной страницы товара """
    prefix = 'https://www.avito.ru'
    item_url = prefix + postfix_url
    req_response = requests.get(item_url, headers=fake_header)
    if req_response.status_code == 200:
        print(item_url)
        get_item_data(req_response.text)
    else:
        print('ВНИМАНИЕ ОШИБКА ЧТЕНИЯ response = ', req_response.status_code)
        print(item_url)
    #симулятор неравномерной задержки
    wait_time = random.uniform(4, 7)
    time.sleep(wait_time)    

def index_page_parser(html_text):
    """ парсер индексной страницы товаров """
    soup = BeautifulSoup(html_text, 'lxml')
    mydivs = soup.findAll("div", {"class": "iva-item-titleStep-2bjuh"})
    #выбрали массив ссылок на товары, начинаем перебирать их
    n = 1 
    for div in mydivs:
        print('    ' + str(n)+ ' ' + div.text + ' || ' + div.contents[0]['href'])
        get_item_page(div.contents[0]['href'])
        n += 1


def get_index_page(start_section_url='https://www.avito.ru/moskva/tovary_dlya_kompyutera/komplektuyuschie/videokarty', pagenum_start=1, pagenum_end=2):
    """ функция читает индексную страницу """
#    fake_header =  { 'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36' }
    req_response = requests.get(start_section_url, headers=fake_header)
    start_section_url = req_response.url
    #без этой ^ хрени не работает переход по подстраницам ?p=2 к стартовой странице приклеивается суффикс
    for page_counter in range(pagenum_start, pagenum_end):
        #перебираем страницы с индексами
        if page_counter > 1 :
            payload = {'p': str(page_counter)}
            req_response = requests.get(start_section_url, headers=fake_header, params=payload)
        else:
            req_response = requests.get(start_section_url, headers=fake_header)
        
        if req_response.status_code == 200:
            #вызываем парсер индексной страницы
            print('URL=' + req_response.url + ' | status= ' + str(req_response.status_code))
            index_page_parser(req_response.text)
        else:
            print('ВНИМАНИЕ ОШИБКА ЧТЕНИЯ')
            print('URL=' + req_response.url + ' | status= ' + str(req_response.status_code))
        #слабый симулякр неравносмерной задержки
        wait_time = random.uniform(4, 7)
        time.sleep(wait_time)


def main():
    #logging.basicConfig(level=logging.DEBUG)
    #logging.debug('This will get logged')

    get_index_page()


if __name__ == "__main__":
    main()
