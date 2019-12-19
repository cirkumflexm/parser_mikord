import requests
import json
from bs4 import BeautifulSoup as bs
import re
import math
import csv

headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
           }

start_url = "https://www.ural-mart.ru/retail/shkafy_dlya_sumok/"


def parse_page(html_page, session):
    items_list = html_page.find_all('div', class_="item")
    product_all = []
    for item in items_list:
        item_name = item.find('h2').find('a').text
        item_link = item.find('h2').find('a')['href']
        item_features = item.find('div', class_="all-features")
        item_price = item.find('strong', class_="product-sum-value").text
        item_kod = item_features.find('h3').text
        request_in = session.get('https://www.ural-mart.ru' + item_link, headers=headers)
        if request_in.status_code == 200:
            html_page_in = bs(request_in.content, 'html.parser')
            html_page_product = html_page_in.find('div', class_="product")
            product_gallery = html_page_product.find('div', class_="gallery-slider").find_all('a')
            item_images = []
            for image in product_gallery:
                item_images.append(image['href'])
            product_feature = html_page_product.find_all('div', class_="feature")
            item_features = []
            for feature in product_feature:
                item_feature = {'product_feature_label': feature.find('div', class_="label").text,
                                'product_feature_value': feature.find('div', class_="value").text}
                item_features.append(item_feature)
            item_description = html_page_product.find_all('div', class_="cont")
        product_one = {
            'item_name': item_name,
            'item_price': item_price,
            'item_kod': item_kod,
            'item_images': item_images,
            'item_features': item_features,
            'item_description': item_description
        }
        product_all.append(product_one)
    return product_all


def parse_json(html_page, session):
    page_script = html_page.find('script', attrs={'src': re.compile("jsonlist")})['src']
    request_script = session.get('https://www.ural-mart.ru' + page_script, headers=headers)
    text_js_pos = request_script.text.find('[')
    text_js = request_script.text[text_js_pos:].replace("]';", "]")
    json_text_js = json.loads(text_js)
    return json_text_js


def parse_img_save(filename, url):
    file_stream = requests.get(url, stream=True)
    with open(filename + '.jpg', 'wb') as fd:
        for chunk in file_stream.iter_content(chunk_size=256):
            fd.write(chunk)


def save_csv(array_product):
    with open('parsed_mikort.csv', 'a') as file:
        a_pen = csv.writer(file)
        a_pen.writerow(('Название', 'Цена', 'Код', 'Ссылки на изображения', 'Поля характеристик', 'Описание'))
        for product in array_product:
            a_pen.writerow((product['item_name'], product['item_price'], product['item_kod'], product['item_images'],
                            product['item_features'], product['item_description']))


def parse_img(array_products):
    for prod in array_products:
        kod = prod['item_kod'].split(' ')
        art = 0
        if kod[2].isdigit():
            art = kod[2]
        nom = 0
        for img in prod['item_images']:
            nom = nom + 1
            parse_img_save(str(art) + '_' + str(nom), 'https://www.ural-mart.ru' + img)

def micort_parse(start_url, headers):
    session = requests.Session()
    request = session.get(start_url, headers=headers)
    ready_page = []
    if request.status_code == 200:
        html_page = bs(request.content, 'html.parser')
        ready_page.extend(parse_page(html_page, session))
        arr_product = parse_json(html_page, session)    # масив товара в текущей категории
        count_entrys = len(arr_product)  # количество записей
        entry_on_page = 20  # количество записей на странице
        current_page = 1    # текущая страница
        sort_price = 0
        kolvo_page_list = math.ceil(count_entrys / 20)  # кол-во списков страниц
        '''
        for akt_page in range(1, kolvo_page_list):
            start_entrys = akt_page*entry_on_page
            list_tovar_show = ''
            for akt_entrys in arr_product[start_entrys:start_entrys+20]:
                list_tovar_show = list_tovar_show + str(akt_entrys['id']) + ','
            request_page = session.post(start_url, data={"list_tovar_show": list_tovar_show, "sort_price": sort_price},
                                        headers=headers)
            html_page_list = bs(request_page.content, 'html.parser')
            ready_page.extend(parse_page(html_page_list, session))
        '''
        print(ready_page)

    else:
        print('Error')

    return ready_page


def main():
    array = micort_parse(start_url, headers)
    save_csv(array)
    parse_img(array)


if __name__ == "__main__":
    main()




