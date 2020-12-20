from bs4 import BeautifulSoup
import lxml

def main():

    #url = 'https://www.avito.ru/moskva/tovary_dlya_kompyutera/komplektuyuschie/videokarty'
    #fake_header =  { 'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36' }

    for page_counter in range(1, 6):
        filename = 'test' + str(page_counter) + '.html'
        with open(filename, 'r', encoding='utf8') as input_file:
            text = input_file.read()
        soup = BeautifulSoup(text, 'lxml')
        mydivs = soup.findAll("span", {"class": "title-root-395AQ iva-item-title-1Rmmj title-list-1IIB_ title-root_maxHeight-3obWc text-text-1PdBw text-size-s-1PUdo text-bold-3R9dt"})
        for i in mydivs:
            print(i.find('a').text)
            print(i.text)
        #container = soup.select('iva-item-content-m2FiN')
        #for item in container:
        #    print(item)

if __name__ == "__main__":
    main()
