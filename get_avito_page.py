import requests

def main():

    r = requests.get('https://www.avito.ru/moskva/tovary_dlya_kompyutera/komplektuyuschie/videokarty')
    print(r.status_code)
    print(r)

if __name__ == "__main__":
    main()
