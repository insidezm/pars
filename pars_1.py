import random
import re
from time import sleep
import requests
from bs4 import BeautifulSoup
import json
import csv
import fake_useragent


user = fake_useragent.UserAgent().random
headers = {
    'User-Agent': user
}

url = "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"

req = requests.get(url, headers=headers)
src = req.text

# Сохраним страницу в файл, чтобы не делать каждый раз новый запрос на сайте.
with open("index.html", "w", encoding='utf-8') as file:
    file.write(src)

with open("index.html", encoding="utf8") as file:
    src = file.read()

soup = BeautifulSoup(src, "lxml")
all_products_href = soup.find_all(class_="mzr-tc-group-item-href")

all_categories_dict = {}
for item in all_products_href:
    item_text = item.text
    item_href = f'https://health-diet.ru{item.get("href")}'

    all_categories_dict[item_text] = item_href

# Сохраним все категории в json файл.
with open("all_categories_dict.json", "w", encoding="utf-8") as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

with open("all_categories_dict.json", encoding="utf-8") as file:
    all_categories = json.load(file)

iteration_count = int(len(all_categories)) - 1
count = 0
print(f"Всего итераций: {iteration_count}")


for category_name, category_href in all_categories.items():
    category_name = re.sub(r'[\s,\'()-]', r'_', category_name)

    req = requests.get(url=category_href, headers=headers)
    src = req.text

    # сохраняем каждую страницу, чтобы работать с локальным компьютером, а не сайтом.
    with open(f"data/{count}_{category_name}.html", "w", encoding='utf-8') as file:
        file.write(src)

    with open(f"data/{count}_{category_name}.html", encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    # проверка страницы на наличие таблицы с продуктами
    alert_block = soup.find(class_="uk-alert-danger")
    if alert_block is not None:
        continue

    # собираем заголовки таблицы
    table_head = soup.find(class_="mzr-tc-group-table").find("tr").find_all("th")
    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text

    with open(f"data/{count}_{category_name}.csv", "w", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            (
                product,
                calories,
                proteins,
                fats,
                carbohydrates
            )
        )

    # собираем данные продуктов
    products_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

    product_info = []
    for item in products_data:
        product_tds = item.find_all("td")

        title = product_tds[0].find("a").text
        calories = product_tds[1].text
        proteins = product_tds[2].text
        fats = product_tds[3].text
        carbohydrates = product_tds[4].text

        product_info.append(
            {
                "Title": title,
                "Calories": calories,
                "Proteins": proteins,
                "Fats": fats,
                "Carbohydrates": carbohydrates
            }
        )
        with open(f"data/{count}_{category_name}.csv", "a", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                (
                    title,
                    calories,
                    proteins,
                    fats,
                    carbohydrates
                )
            )
    with open(f"data/{count}_{category_name}.json", "a", encoding="utf-8") as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    count += 1
    iteration_count = iteration_count - 1

    if iteration_count == 0:
        print("Работа завершена")
        break

    sleep(random.randrange(2, 4))
