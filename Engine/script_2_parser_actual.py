import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import openpyxl as xl
import time
import os 
import xlsxwriter
import PySimpleGUI as sg
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

start_time = time.time()  # время начала выполнения
URL = "https://www.san.team"

current_date = date.today()
# создаем df для итоговых результатов
san_team_vendors_dict = {"Vendor":[],
                       "Nomination":[],
                       "Price":[],
                       "Reference":[],
                       "Category_Name":[],
                       "Sub_category_1":[]}
df_san_team_vendors = pd.DataFrame(san_team_vendors_dict)

# данные запроса браузера
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# исходный сайт, который будем парсить( продумать запуск inputom)
url = "https://www.san.team/catalog/"
req = requests.get(url, timeout= 5).text
src = req

#sg.Window(title=f"Parsing {url}", layout=[[]], margins=(400, 200)).read()

# запись данных для минимизации запросов на сайт
with open("Data/index.html", "w", encoding = "utf-8") as file:
    file.write(src)

# чтение из файла
with open("Data/index.html", encoding = "utf_8_sig") as file:
    src = file.read()

soup = BeautifulSoup(src, "lxml")
catalog_block = soup.find("div", class_ = "content content--catalog1")

# сбор ссылок с прочитанного файла(страницы сайта) по определенному тегу и классу тега
all_categories_hrefs = catalog_block.find_all("a", class_ = "clearfix")

# создаем словарь категория: ссылка
all_categories_dict = {}
for item in all_categories_hrefs:
    item_text =item.text.strip()
    item_href = URL + item.get("href")
    all_categories_dict[item_text] = item_href


# заеносим данные в файл json
with open("Data/all_categories_dict.json", "w", encoding = "utf-8") as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii= False)
    
# создаем переменную из файла json
with open("Data/all_categories_dict.json", encoding = "utf-8") as file:
    all_categories = json.load(file)
    
##### БЛОК ФУНКЦИЙ #####   
def href_not_has_defenite_class(tag):
    return tag.has_attr("href") and not tag.has_attr('class')# = \"catalog-lvl-2__title \"')
    
def div_has_definite_class():
    if soup.find("div", class_ = "catalog-lvl-2") == None:
        return soup.find("div", class_ = "catalog-lvl-3").find_all("a")
    else:
        return soup.find("div", class_ = "catalog-lvl-2").find_all("a")

def check_and_create_folder(name_dir):
    if os.path.isdir(f'C:/Users/vorotintsev/Desktop/PYTHON_parser/Data/Sub_categories/{name_dir}') == False:
        dir_and_file_name = 'Data/Sub_categories/' + name_dir
        path = os.path.join(cur_dir, dir_and_file_name)
        os.mkdir(path)
        
def create_page_dict(list):
    page_dict = {}
    for item in count_pages:
        page_ref = item.find("a").get("href")
        if page_ref == "#":
            page_ref = sub_category_href
        else:
            page_ref = URL + item.find("a").get("href")
        page_text = item.text.strip()
        if page_text != '': 
            page_dict[page_text] = page_ref
    return page_dict 

def create_dict_to_write(url, list, list_name):
    count=1
    for item in list:
        key = f"{count}_{item.text.strip()}"
        ref = item.find("a").get("href")
        href = url + ref
        list_name[key] = href
        count += 1
    return list
##### БЛОК ФУНКЦИЙ #####

count = 0

# прогрессбар
""" progressbar = [
    [sg.ProgressBar(len(all_categories_dict), orientation = 'h', size=(51, 10), key = 'progressbar')]
]
output_win = [
    [sg.Output(size=(80, 20))]
]
layout = [
    [sg.Frame('Progress', layout = progressbar)],
    [sg.Frame('Output', layout = output_win)],
    [sg.Submit('Start'), sg.Cancel()]
]
window = sg.Window('Custom Progress Meter', layout)
progress_bar = window['progressbar']
while True:
    event, values = window.read(timeout=10)
    if event == 'Cancel'  or event is None:
        break
    elif event == 'Start':
        for i,item in enumerate(all_categories_dict):
            print(item)
            time.sleep(1)
            progress_bar.UpdateBar(i + 1)

window.close() """

# цикл перебора категорий и сохранение ссылок в файл
for category_name, category_href in all_categories.items():
    print(f"Обработка категории {category_name} {count +1} из {len(all_categories_dict)}")
     
    # ограничение итераций по количеству ссылок в словаре
    if count <= len(all_categories_dict): #category_name == "Аксессуары для ванных и туалетных комнат":
        req = requests.get(url=category_href, headers=headers, timeout = 5)
        src = req.text
        soup = BeautifulSoup(src, "lxml")
        # поиск всех ссылок в div-контейнере, определенного класса
        sub_categories = div_has_definite_class() #soup.find("div", class_ = "catalog-lvl-2").find_all(not_has_defenite_class)
        # создаем словари подкатегорий, к которым будем обращаться в дальнейшем
        sub_categories_dict = {}
        
        for item in sub_categories:
            # перебираем все категории в массиве ссылок
            # получаем имя подкатегории, обрезая лишние пробелы
            item_sub_cat_text = item.text.strip().replace('"','') # Категория_1 - 5
            # получаем ссылку подкатегории, записываем в переменную с исходным доменном сайта
            item_sub_cat_href =URL + item.get("href")
            
            # проверяем на пустые имена и очищаем не нужные ссылки
            if item_sub_cat_text != "" and item_sub_cat_text != "Перейти в раздел":
                sub_categories_dict[item_sub_cat_text] = item_sub_cat_href
                
            cur_dir = r'C:/Users/vorotintsev/Desktop/PYTHON_parser'
            check_and_create_folder(f'{count}_{category_name}')
            
        # запись файла в json-файл    
        with open(f"Data/Sub_categories/{count}_{category_name}/{category_name}_sub_categories.json", "w", encoding = "utf-8") as file:
                        json.dump(sub_categories_dict, file, indent=4, ensure_ascii= False) 
                # чтение из файла
        with open(f"Data/Sub_categories/{count}_{category_name}/{category_name}_sub_categories.json", encoding = "utf-8") as file:
                        all_sub_cat_dict = json.load(file)               
        count_sub_cat = 0
        vendor_count = 0
        vend_count = 0
                # функция проверяет ссылки на артикула по набору атрибутов
        def href_not_has_defenite_class(tag):
            return tag.has_attr("href") and not tag.has_attr('class')# = \"catalog-lvl-2__title \"')
                
                # перебор суб_категорий
        for sub_category_name, sub_category_href in all_sub_cat_dict.items():
            req = requests.get(url=sub_category_href, headers=headers, timeout=5)
            src = req.text
            soup = BeautifulSoup(src, "lxml")
            count_pages = soup.find("div", class_="pagination").find_all("div", class_="pagination__item")
            vendor_list = []
            if len(count_pages) > 0:
                page_dict = create_page_dict(count_pages)      
                for pg_in, pg_ref  in page_dict.items():
                    req = requests.get(url = pg_ref, headers=headers, timeout=5)
                    src = req.text
                    soup = BeautifulSoup(src, "lxml")                
                    if soup.find_all("div", class_ = "catalog-lvl-4__titlte") != None:
                        art_List = soup.find_all("div", class_ = "catalog-lvl-4__title")
                        vendor_list = vendor_list + art_List
                vendor_dict = {}
                create_dict_to_write(URL, vendor_list, vendor_dict)
                # запись в файл .json
                with open(f"Data/Sub_categories/{count}_{category_name}/{sub_category_name}_vendor_list.json", "w", encoding = "utf-8") as file:
                    json.dump(vendor_dict, file, indent=4, ensure_ascii= False) 
                # чтение из файла .json
                with open(f"Data/Sub_categories/{count}_{category_name}/{sub_category_name}_vendor_list.json", encoding = "utf-8") as file:
                    all_vendor_sub_cat_dict = json.load(file)
                vend_count =len(all_vendor_sub_cat_dict)
                print(f"Собрано {vend_count} позиций в категории {sub_category_name}")
                        
                for item_name, item_href in all_vendor_sub_cat_dict.items():
                            art_text = item_name[item_name.index('_')+1:] # наименование y[y.index('_')+1:]
                            art_href = item_href # ссылка - 4
                            art_src = requests.get(art_href, headers=headers, timeout=5).text
                            art_bs = BeautifulSoup(art_src, "lxml")
                            art_txt = art_bs.find("div", class_ = "detail-product-buy__article").text.strip()
                            art_name = art_txt[art_txt.find(" ")+1:]
                            price = float(art_bs.find("div", class_ = "detail-product-buy__buttons").find("a", class_="buyoneclick").get("data-productprice").replace(',', '.').replace(' ', ''))
                            vendor_count +=1
                            df_san_team_vendors.loc[len(df_san_team_vendors.index)]=[art_name, art_text, price, art_href, category_name, sub_category_name]
                            print(df_san_team_vendors)
            else:
                if soup.find_all("div", class_ = "catalog-lvl-4__titlte") != None:
                    art_List = soup.find_all("div", class_ = "catalog-lvl-4__title")
                    vendor_dict = {}
                    create_dict_to_write(URL, art_List, vendor_dict)
                    # запись в файл .json
                    with open(f"Data/Sub_categories/{count}_{category_name}/{sub_category_name}_vendor_list.json", "w", encoding = "utf-8") as file:
                        json.dump(vendor_dict, file, indent=4, ensure_ascii= False) 
                    # чтение из файла .json
                    with open(f"Data/Sub_categories/{count}_{category_name}/{sub_category_name}_vendor_list.json", encoding = "utf-8") as file:
                        all_vendor_sub_cat_dict = json.load(file)
                    vend_count =len(all_vendor_sub_cat_dict)
                    print(f"Собрано {vend_count} позиций в категории {sub_category_name}")
                    for item_name, item_href in all_vendor_sub_cat_dict.items():
                                art_text = item_name[item_name.index('_')+1:] # наименование y[y.index('_')+1:]
                                art_href = item_href # ссылка - 4
                                art_src = requests.get(art_href, headers=headers, timeout=5).text
                                art_bs = BeautifulSoup(art_src, "lxml")
                                art_txt = art_bs.find("div", class_ = "detail-product-buy__article").text.strip()
                                art_name = art_txt[art_txt.find(" ")+1:]
                                price = float(art_bs.find("div", class_ = "detail-product-buy__buttons").find("a", class_="buyoneclick").get("data-productprice").replace(',', '.').replace(' ', ''))
                                vendor_count +=1
                                df_san_team_vendors.loc[len(df_san_team_vendors.index)]=[art_name, art_text, price, art_href, category_name, sub_category_name]
                                            #print(art_name)
                                            #print(art_text)
                                            #print(price)
                                            #print(art_href)
                                            #print(category_name)
                                print(df_san_team_vendors)
    count +=1

json_san_team_vendor = df_san_team_vendors.to_json(orient="table")

with open("Data/СанТим.json", "w", encoding = "utf-8") as file:
    file.write(json_san_team_vendor)
    
sheet_name = 'Sheet_1'

with pd.ExcelWriter(
        f"Data/Output/Сантим_{current_date}.xlsx",
        engine="xlsxwriter",
        mode='w') as writer:

    df_san_team_vendors.to_excel(writer, sheet_name=sheet_name, index=False)
    workbook = writer.book
    link_format = workbook.add_format({  # type: ignore
                            'font_color': 'blue',
                            'underline': 1,
                            'valign': 'top',
                            'text_wrap': True,
                        })
    writer.sheets[sheet_name].set_column('D:D', None, link_format)


end_time = time.time()  # время окончания выполнения
execution_time = end_time - start_time  # вычисляем время выполнения
print("Сбор данных завершен")
print(f"Время выполнения программы: {execution_time} секунд")
time.sleep(3)