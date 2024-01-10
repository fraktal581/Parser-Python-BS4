import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import openpyxl as xl
import xlsxwriter
from datetime import date
current_date = date.today()
# создаем df для итоговых результатов
san_team_vendors_dict = {"Vendor":[],
                       "Nomination":[],
                       "Price":[],
                       "Reference":[],
                       "Category_Name":[]}
df_san_team_vendors = pd.DataFrame(san_team_vendors_dict)

# данные запроса браузера
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# исходный сайт, который будем парсить( продумать запуск inputom)
url = "https://www.san.team/catalog/"
req = requests.get(url).text
src = req

# запись данных для минимизации запросов на сайт
with open("index.html", "w", encoding = "utf-8") as file:
    file.write(src)

# чтение из файла
with open("index.html", encoding = "utf_8_sig") as file:
    src = file.read()

soup = BeautifulSoup(src, "lxml")
catalog_block = soup.find("div", class_ = "content content--catalog1")

# сбор ссылок с прочитанного файла(страницы сайта) по определенному тегу и классу тега
all_categories_hrefs = catalog_block.find_all("a", class_ = "clearfix")

# создаем словарь категория: ссылка
all_categories_dict = {}
for item in all_categories_hrefs:
    item_text =item.text.strip()
    item_href = "https://www.san.team" + item.get("href")
    all_categories_dict[item_text] = item_href


# заеносим данные в файл json
with open("all_categories_dict.json", "w", encoding = "utf-8") as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii= False)
    
# создаем переменную из файла json
with open("all_categories_dict.json", encoding = "utf-8") as file:
    all_categories = json.load(file)
    
def href_not_has_defenite_class(tag):
    return tag.has_attr("href") and not tag.has_attr('class')# = \"catalog-lvl-2__title \"')
    
def div_has_definite_class():
    if soup.find("div", class_ = "catalog-lvl-2") == None:
        return soup.find("div", class_ = "catalog-lvl-3").find_all("a")
    else:
        return soup.find("div", class_ = "catalog-lvl-2").find_all("a")

count = 0
# цикл перебора категорий и сохранение ссылок в файл
for category_name, category_href in all_categories.items():
    # ограничение итераций по количеству ссылок в словаре
    if count<=0: #len(all_categories_dict):
        req = requests.get(url=category_href, headers=headers)
        src = req.text
        soup = BeautifulSoup(src, "lxml")
        
        # поиск всех ссылок в div-контейнере, определенного класса
        sub_categories = div_has_definite_class() #soup.find("div", class_ = "catalog-lvl-2").find_all(not_has_defenite_class)
        # создаем словари подкатегорий, к которым будем обращаться в дальнейшем
        sub_categories_dict = {}
        
        for item in sub_categories:
            # перебираем все категории в массиве ссылок
            # получаем имя подкатегории, обрезая лишние пробелы
            item_sub_cat_text = item.text.strip() # Категория_1 - 5
            # получаем ссылку подкатегории, записываем в переменную с исходным доменном сайта
            item_sub_cat_href ="https://www.san.team" + item.get("href")
            
            # проверяем на пустые имена и очищаем не нужные ссылки
            if item_sub_cat_text != "" and item_sub_cat_text != "Перейти в раздел":
                sub_categories_dict[item_sub_cat_text] = item_sub_cat_href
            # запись файла в json-файл    
            with open(f"Data/Sub_categories/{count}_{category_name}_sub_categories.json", "w", encoding = "utf-8") as file:
                json.dump(sub_categories_dict, file, indent=4, ensure_ascii= False) 
            # чтение из файла
            with open(f"Data/Sub_categories/{count}_{category_name}_sub_categories.json", encoding = "utf-8") as file:
                all_sub_cat_dict = json.load(file)
        count_sub_cat = 0
        
        def href_not_has_defenite_class(tag):
            return tag.has_attr("href") and not tag.has_attr('class')# = \"catalog-lvl-2__title \"')
        
        for sub_category_name, sub_category_href in all_sub_cat_dict.items():
            if count_sub_cat <= len(all_sub_cat_dict):
                req = requests.get(url=sub_category_href, headers=headers)
                src = req.text
                soup = BeautifulSoup(src, "lxml")
                if soup.find_all("div", class_ = "catalog-lvl-4__title") != None:
                    art_List = soup.find_all("div", class_ = "catalog-lvl-4__title")
                    for item in art_List:
                        art_text = item.text.strip() # наименование - 2
                        art_href ="https://www.san.team" + item.find("a").get("href") # ссылка - 4
                        art_src = requests.get(art_href, headers=headers).text
                        art_bs = BeautifulSoup(art_src, "lxml")
                        art_txt = art_bs.find("div", class_ = "detail-product-buy__article").text.strip()
                        art_name = art_txt[art_txt.find(" ")+1:]
                        
                        price = float(art_bs.find("div", class_ = "detail-product-buy__buttons").find("a", class_="buyoneclick").get("data-productprice").replace(',', '.').replace(' ', ''))
                        df_san_team_vendors.loc[len(df_san_team_vendors.index)]=[art_name, art_text, price, art_href, category_name]
                        #print(art_name)
                        #print(art_text)
                        #print(price)
                        #print(art_href)
                        #print(category_name)
                        #print(df_san_team_vendors)

                
    count +=1



json_san_team_vendor = df_san_team_vendors.to_json(orient="table")

with open("Data/СанТим.json", "w", encoding = "utf-8") as file:
    file.write(json_san_team_vendor)
    
#xl_writer = pd.ExcelWriter("Data/Сантим.xlsx")
sheet_name = 'Sheet_1'
""" writer = pd.ExcelWriter(f"Data/Сантим_{current_date}.xlsx")
workbook = writer.book
link_format = workbook.add_format({  # type: ignore
    'font_color': 'blue',
    'underline': 1,
    'valign': 'top',
    'text_wrap': True,
}) """

with pd.ExcelWriter(
        f"Data/Сантим_{current_date}.xlsx",
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

print("ок")