import csv
import os


def csv_parser(list_files, categoriya):
    for filecsvsrc in list_files:
        with open(filecsvsrc, encoding="utf-8") as csvfile:
            dstdirectory = 'dst_parser_result_plus'
            with open(dstdirectory + '/' + filecsvsrc, 'a', encoding="utf-8") as newcsvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                a_pen = csv.writer(newcsvfile)
                a_pen.writerow(('product_name', 'product_price', 'product_sku', 'file_url', 'product_s_desc',
                            'product_desc', 'product_length', 'product_height',	'product_width', 'product_weight',
                            'features', 'category_id'))
                for row in spamreader:
                    if len(row) > 0:
                        temp_images = row[3]
                        temp_images = temp_images.replace("['", '').replace("']", '').split("', '")
                        row[3] = temp_images[0]
                        row.append(categoriya)
                        a_pen.writerow(row)


def csv_parser_media_img(list_files):
    for filecsvsrc in list_files:
        with open(filecsvsrc, encoding="utf-8") as csvfile:
            dstdirectory = 'dst_parser_result_media'
            with open(dstdirectory + '/media.csv', 'a', encoding="utf-8") as newcsvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                a_pen = csv.writer(newcsvfile)
                for row in spamreader:
                    if len(row) > 0:
                        temp_images = row[3]
                        temp_images = temp_images.replace("['", '').replace("']", '').split("', '")
                        for media in temp_images:
                            media_row = [row[2], media]
                            a_pen.writerow(media_row)

def main():
    directory = 'parser_result'
    list_files = os.listdir(directory)

    #csv_parser(list_files, 60)

    csv_parser_media_img(list_files)

if __name__ == "__main__":
    main()

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
             "/constructions/nesemnaya-opalubka/", "/avtomatizaciya-torgovli/", ]