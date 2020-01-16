import requests
import json
from bs4 import BeautifulSoup as bs
import re
import math
import csv
import time
import os

headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
           }
site_url = "https://www.ural-mart.ru"

array_url = []

temp_url = ["/retail/shkafy_dlya_sumok/"]

gut_url = ["/retail/vitrina/", "/retail/prilavki/", "/retail/kassovoe-oborudovanie/", "/retail/shkafy_dlya_sumok/",
           "/retail/telezhki-pokupatelskie/", "/retail/korziny-pokupatelskie/", "/retail/prohodnye-sistemy/",
           "/retail/rasprodazhnye-korziny/", "/retail/aksessuary-dlya-magazinov/", "/shelving/torgovye_stellazhi/",
           "/shelving/arhivnye_stellazhi/", "/shelving/gruzovye_stellazhi/", "/shelving/promyshlennye_stellazhi/",
           "/shelving/konsolnye_stellazhi/", "/shelving/glubinnye_stellazhi/", "/technologic/prigotovlenie-pishi/",
           "/technologic/linii-razdachi/", "/technologic/holodilnie-stoli/",
           "/technologic/baktericidnoe-oborudovanie/", "/technologic/posudomoechnoe-oborudovanie/",
           "/technologic/prachechnoe-oborudovanie/", "/production/dlya-holodilnogo-oborudovaniya/",
           "/production/dlya-teplovogo-oborudovaniya/", "/production/dlya-nejtralnogo-oborudovaniya/",
           "/production/dlya-linij-razdach/", "/constructions/sendvich-paneli-iz-minvaty/",
             "/constructions/sendvich-paneli-iz-pur/", "/constructions/sendvich-paneli-iz-pir/",
             "/constructions/nesemnaya-opalubka/", "/avtomatizaciya-torgovli/"]

fail_url = ["/technologic/teplovoe-oborudovanie/", "/technologic/nejtralnoe/", "/production/dlya-elektromehanicheskogo-oborudovaniya/",]

def parse_page(html_page, session):
    items_list = html_page.find_all('div', class_="item")
    product_all = []
    for item in items_list:
        item_name = item.find('h2').find('a').text
        item_link = item.find('h2').find('a')['href']
        item_features = item.find('div', class_="all-features")
        item_price = item.find('strong', class_="product-sum-value").text
        item_price = item_price.replace(' ', '')
        item_kod = item_features.find('h3').text
        item_kod = item_kod[12:]
        request_in = session.get('https://www.ural-mart.ru' + item_link, headers=headers)
        if request_in.status_code == 200:
            print('Парсинг карточки товара' + item_link)
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
        else:
            print('Неудача подключения к карточке')
            item_images = ''
            item_features = ''
            item_description = ''
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
    with open('images/' + filename + '.jpg', 'wb') as fd:
        for chunk in file_stream.iter_content(chunk_size=256):
            fd.write(chunk)


def save_csv(array_product, name_razdel):
    with open('parsed_mikort_' + name_razdel + '.csv', 'a', encoding="utf-8") as file:
        a_pen = csv.writer(file)
        a_pen.writerow(('product_name', 'product_price', 'product_sku', 'product_images', 'product_s_desc',
                        'product_desc', 'product_length', 'product_height',	'product_width', 'product_weight',
                        'features'))
        for product in array_product:
            features_html = '<div class="features">'
            for feature in product['item_features']:
                dlinna = 0
                shirina = 0
                visota = 0
                ves = 0
                if feature['product_feature_label'] == 'Длина, мм:':
                    dlinna = feature['product_feature_value']
                if feature['product_feature_label'] == 'Ширина, мм:':
                    shirina = feature['product_feature_value']
                if feature['product_feature_label'] == 'Высота, мм:':
                    visota = feature['product_feature_value']
                if feature['product_feature_label'] == 'Вес:':
                    ves = feature['product_feature_value']
                features_item = '<div class ="feature"><div class="label">{}</div><div class="value">{}</div>' \
                                '</div>'.format(feature['product_feature_label'], feature['product_feature_value'])
                features_html = features_html + features_item
            features_html = features_html + '</div>'
            images_list_product = []
            for nom in range(0, len(product['item_images'])):
                images_list_product.append(name_razdel + '/' + str(product['item_kod']) + '_' + str(nom) + '.jpg')
            a_pen.writerow((product['item_name'], product['item_price'], product['item_kod'], images_list_product,
                            product['item_features'], product['item_description'], dlinna, shirina, visota, ves,
                            features_html))


def parse_img(array_products, name_razdel):
    nom_prod = 0
    for prod in array_products:
        nom = 0
        nom_prod = nom_prod + 1
        for img in prod['item_images']:
            time.sleep(1)
            parse_img_save(name_razdel + '/' + str(prod['item_kod']) + '_' + str(nom), 'https://www.ural-mart.ru' + img)
            nom = nom + 1
            print('Из ' + len(array_products) + ' Выполнено ' + nom_prod + '. Из ' + len(prod['item_images']) + ' готово' + nom)


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

        for akt_page in range(1, kolvo_page_list):
            print('Парсинг внутренней списка раздела. Пагинация: ' + str(akt_page))
            time.sleep(3)
            start_entrys = akt_page*entry_on_page
            list_tovar_show = ''
            for akt_entrys in arr_product[start_entrys:start_entrys+20]:
                list_tovar_show = list_tovar_show + str(akt_entrys['id']) + ','
            request_page = session.post(start_url, data={"list_tovar_show": list_tovar_show, "sort_price": sort_price},
                                        headers=headers)
            html_page_list = bs(request_page.content, 'html.parser')
            ready_page.extend(parse_page(html_page_list, session))

    else:
        print('Error')

    return ready_page


def main():
    for url_one in array_url:
        print('Парсинг нового раздела. Название: ' + url_one)
        name_razdel = url_one.replace('/', '__')
        os.mkdir('images/' + name_razdel)
        full_addr = site_url + url_one
        array = micort_parse(full_addr, headers)
        print('Сохраниение CSV')
        save_csv(array, name_razdel)
        # print('Парсинг изображений раздела.')
        # parse_img(array, name_razdel)
        print('Парсинг раздела завершен.')
        time.sleep(40)

if __name__ == "__main__":
    main()




