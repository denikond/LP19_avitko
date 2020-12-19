import requests
import random
import time

def main():

    url = 'https://www.avito.ru/moskva/tovary_dlya_kompyutera/komplektuyuschie/videokarty'
    fake_header =  { 'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36' }

    for page_counter in range(1, 6):
        payload = {'p': str(page_counter)}
        r = requests.get(url, headers=fake_header,params=payload)
        print('URL=' + url + ' | status= ' + str(r.status_code))
        if r.status_code == 200:
            #print(r.content)
            #print(r.text)
            filename = 'test' + str(page_counter) + '.html'
            with open(filename, 'w', encoding='utf8') as output_file:
                output_file.write(r.text)
        wait_time = random.uniform(4, 7)
        time.sleep(wait_time)

if __name__ == "__main__":
    main()
