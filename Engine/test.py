import requests
from bs4 import BeautifulSoup, Comment
import json
import re
# данные запроса браузера
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# исходный сайт, который будем парсить( продумать запуск inputom)
url = "https://www.san.team/catalog/truboprovodnaja_armatura/krany_sharovye/68418/"
req = requests.get(url).text
src = req
soup = BeautifulSoup(src, "lxml")
price_soup = soup.find("div", class_ = "detail-product-buy__buttons").find("a", class_="buyoneclick").get("data-productprice")
print(price_soup)

""" comment = price_soup.find(string=lambda text: isinstance(text, Comment))

if comment:
    cs = BeautifulSoup(comment, 'lxml')
    ex = cs.get_text(" ")
    print(ex.strip('p> Самовывоз  руб.'))
else:
    print(None)
 """






""" price= '''<div class="detail-product-buy__declaration-data delivery">
<p><a data-toggle="modal" href="#callback-modal-delivery">Доставка</a></p>
<!--p><a href="#callback-modal-delivery" data-toggle="modal">Самовывоз</a><span>975 руб.</span></p-->
</div>'''
"""
""" bs = BeautifulSoup(price, 'html.parser')
div = bs.find('div', class_='detail-product-buy__declaration-data delivery')

c = div.find(string=lambda text: isinstance(text, Comment))

if c:
    cs = BeautifulSoup(c, 'html.parser')
    ex = cs.get_text()
    print(ex)
else:
    print("Not found")
     """
