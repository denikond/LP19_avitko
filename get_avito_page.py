import logging
import requests
import random
import time
from bs4 import BeautifulSoup
import lxml
from app import db
from app.models import Item, Image
from datetime import datetime, timedelta
import os
import urllib.request
import config
from PIL import Image as PImage

fake_header =  { 'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36' }

def images_store_dir_n_db(img_urls, num_of_ad_i):
    """ Функция сохраняющая картинки объявления на диск и в базу
    входной параметр - массив ссылок на картинки и номер объявления"""

    for ind, img in enumerate(img_urls):
        fo_name = num_of_ad_i + "_" + (f"{str(ind):>3}").replace(" ","0") + ".jpg"
        fo_norm = os.path.join(config.img_normal_dir, fo_name)
        fo_thumb = os.path.join(config.img_thumb_dir, fo_name)

        try:
            urllib.request.urlretrieve(img, fo_norm)
        except Exception as err:
            print(err)

        try:
            with PImage.open(fo_norm) as im:
                im.thumbnail(config.thumb_size)
                im.save(fo_thumb, "JPEG")
        except OSError:
            print("cannot create thumbnail for", fo_norm)

        grabed_Image = Image(num_of_ad=num_of_ad_i,image_path=fo_name)
        db.session.add(grabed_Image)
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            print(err)


def parse_date(str_i):

    months = [" ", "января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]

    """ функция преобразующая текстовую дату с Авито в объект datetime 
    входные данные строка, начинается символ \n, пробелы, потом "сегодня| число месяц" 
    далее опционально время ЧЧ:ММ (может быть, может не быть) """
    date_split = str_i[1:].split()
    if date_split[0] == 'сегодня':
        ad_date = datetime.today()
        ad_time = datetime.strptime(date_split[2], "%H:%M").time()
        ad_datetime = datetime.combine(ad_date, ad_time)
    elif date_split[0] == 'вчера':
        ad_date = datetime.today() - timedelta(days=1)
        ad_time = datetime.strptime(date_split[2], "%H:%M").time()
        ad_datetime = datetime.combine(ad_date, ad_time)
    else:
        ad_day = int(date_split[0])
        ad_mon = months.index(date_split[1])
        if date_split[2] == 'в':
            ad_year = datetime.now().year
            ad_time = datetime.strptime(date_split[3], "%H:%M").time()
        elif len(date_split)>3:
            ad_year = int(date_split[3])
            ad_time = datetime.strptime(date_split[4], "%H:%M").time()
        else:
            ad_year = int(date_split[2])
            ad_time = datetime.strptime('0:0', "%H:%M").time()
        ad_datetime = datetime.combine(datetime(year=ad_year, month=ad_mon, day=ad_day), ad_time)
    return ad_datetime

def get_item_data(html_text):
    """ парсер индивидуальной страницы с товаром, без нормальзации полей """
    soup = BeautifulSoup(html_text, 'lxml')
    #наименование товара
    item_name = soup.findAll("span", {"class": "title-info-title-text"})[0].next
    #номер объявления - пока некрасивый, как буду писать в базу нужно номализовать
    num_sign = soup.findAll("span", {"data-marker": "item-view/item-id"})
    #они бывают пустыми как выяснилось
    if len(num_sign):
        num_sign = "".join(x for x in num_sign[0].next if x.isdigit()) 
    else:
        num_sign = ''
    #дата подачи объявления - они прколисты, придется писать парсер времени авито-времени
    date_sign = soup.findAll("div", {"class": "title-info-metadata-item-redesign"})
    #она тоже бывает пустой
    if len(date_sign):
        date_sign = parse_date(date_sign[0].next)
    else:
        date_sign = None
    #варим в супе все ссылки на фотки с товаром
    #это были thumb's 640x480
    #img_path = soup.findAll("div", {"class": "gallery-img-frame js-gallery-img-frame"})
    #это полноразмерные фото  gallery-extended-img-frame gallery-extended-img-frame_state-selected js-gallery-extended-img-frame
    #img_path = soup.findAll("div", {"class": "gallery-extended-img-frame js-gallery-extended-img-frame"})
    img_path = soup.findAll("div", {"class": "gallery-extended-img-frame"})
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
        price = int(price[0].next.replace(' ', ''))
    else:
        price = 0
    #сообщения к объявлению
    message_text = soup.findAll("div", {"class": "item-description-text"})
    #формат полное безумие включая набор смайлов, в utf-8
    if len(message_text):
        message_text = message_text[0].find_all('p')[0].next
    else:
        message_text = ''
    #Ниже временная фигня для записи строки в файл и визуального контроля
    """
    str1 = item_name + ';' + num_sign + ';' + date_sign + ';' + img_urls[0] + ';' + addr + ';' + price + ';' + message_text
    str2 = ''
    for i in str1:
        if i != '\n':
            str2 += i
    str2 += '\n'
    print(str2)
    with open('out.csv', 'a+',encoding='utf-8') as of:
        of.write(str2)"""
    #конец временной фигни для записи в файл и визуального контроля
    if num_sign != '':
        grabed_Item = Item(description=item_name,num_of_ad=num_sign,creation_date=date_sign,address=addr,price=price,extended_text=message_text)
        db.session.add(grabed_Item)
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            print(err)
            #print("Такое объявление уже есть, импорт не производится")
        else:
            images_store_dir_n_db(img_urls,num_sign)
    else:
        print("!!! Обнаружена реклама, а не объявление, исключено из импорта в базу")
        


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
    wait_time = random.uniform(3, 5)
    time.sleep(wait_time)    

def index_page_parser(html_text, index_num):
    """ парсер индексной страницы товаров """
    soup = BeautifulSoup(html_text, 'lxml')
    mydivs = soup.findAll("div", {"class": "iva-item-titleStep-2bjuh"})
    #выбрали массив ссылок на товары, начинаем перебирать их
    n = 1 
    for div in mydivs:
        print('    ' + str(index_num) + ' : ' + str(n)+ ' ' + div.text + ' || ' + div.contents[0]['href'])
        get_item_page(div.contents[0]['href'])
        n += 1


def get_index_page(start_section_url='https://www.avito.ru/moskva/tovary_dlya_kompyutera/komplektuyuschie/videokarty', pagenum_start=1, pagenum_end=20):
    """ функция читает индексную страницу """
#    fake_header =  { 'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36' }
    req_response = requests.get(start_section_url, headers=fake_header)
    start_section_url = req_response.url
    #без этой ^ хрени не работает переход по подстраницам ?p=2 к стартовой странице приклеивается суффикс
    for page_counter in range(pagenum_start, pagenum_end+1):
        #перебираем страницы с индексами
        if page_counter > 1 :
            payload = {'p': str(page_counter)}
            req_response = requests.get(start_section_url, headers=fake_header, params=payload)
        else:
            req_response = requests.get(start_section_url, headers=fake_header)
        
        if req_response.status_code == 200:
            #вызываем парсер индексной страницы
            print('URL=' + req_response.url + ' | status= ' + str(req_response.status_code))
            index_page_parser(req_response.text, page_counter)
        else:
            print('ВНИМАНИЕ ОШИБКА ЧТЕНИЯ')
            print('URL=' + req_response.url + ' | status= ' + str(req_response.status_code))
        #слабый симулякр неравносмерной задержки
        wait_time = random.uniform(4, 7)
        time.sleep(wait_time)


def main():
    #logging.basicConfig(level=logging.DEBUG)
    #logging.debug('This will get logged')

    #get_index_page()
    get_index_page(start_section_url='https://www.avito.ru/moskva/tovary_dlya_kompyutera/komplektuyuschie/videokarty', pagenum_start=1, pagenum_end=2)

    #get_item_page("/moskva/tovary_dlya_kompyutera/radeon_hd_5570_1gb_2051605184")

if __name__ == "__main__":
    main()
