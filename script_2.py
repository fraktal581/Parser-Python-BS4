import json
import requests
with open("all_categories_dict.json", encoding = "utf-8") as file:
    all_categories = json.load(file)

    for category_name, category_href in all_categories.items():
        req = requests.get
print()
