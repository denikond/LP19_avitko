import requests

def main():

    url = 'https://www.avito.ru/moskva/tovary_dlya_kompyutera/komplektuyuschie/videokarty'
    fake_header =  { 'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36' }
    r = requests.get(url, headers=fake_header)
    print(r.status_code)
    print(r.content)
    #print(r.text)
    
    with open('test.html', 'w', encoding='utf8') as output_file:
        output_file.write(r.text)

if __name__ == "__main__":
    main()
