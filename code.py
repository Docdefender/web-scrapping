import requests
from bs4 import BeautifulSoup
import sqlite3

baseurl = "https://www.gratis.com/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/119.0.0.0 Safari/537.36'}
links = []
for x in range(1, 5):
    url = f'https://www.gratis.com/parfum-deodorant-c-504?page={x}'
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    products = soup.find_all('div', class_='infos')
    for item in products:
        for link in item.find_all('a', href=True):
            links.append(baseurl + link['href'])

print(links)

item_list = []
for link in links:
    r = requests.get(link, headers=headers)
    try:
        soup = BeautifulSoup(r.content, 'html.parser')
        name = soup.find('h1', class_="product-title pdp-product-title ng-star-inserted").text.strip()
        price = soup.find('span', class_='discounted').text.strip()
        brand = soup.find('div', class_='product-details-rating ng-star-inserted').text.strip()
        rating = soup.find('div', class_='JetR-inline-ratingOrCount').text.strip()
        reviews_list = []

        try:
            reviews_divs = soup.find_all('div', class_='gratis-review-container')
            for review_div in reviews_divs:
                review_name = review_div.find('span', class_='cssVar-authorName').text.strip()
                review_date = review_div.find('span',
                                              class_='min-width: fit-content; align-self: center; ').text.strip()
                review_text = review_div.find('div', class_='item__inner').text

                reviews_list.append({'name': review_name, 'date': review_date, 'review': review_text})

        except Exception as e:
            print(f"Error fetching reviews: {e}")

    except Exception as e:
        print(f"Error fetching product details: {e}")
        continue

    items = {
        'name': name,
        'price': price,
        'brand': brand,
        'rating': rating,
        'reviews': reviews_list
    }

    item_list.append(items)


conn = sqlite3.connect('products.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price TEXT,
        brand TEXT,
        rating TEXT,
        reviews TEXT
    )
''')
conn.commit()


for item in item_list:
    cursor.execute('''
        INSERT INTO products (name, price, brand, rating, reviews) VALUES (?, ?, ?, ?, ?)
    ''', (item['name'], item['price'], item['brand'], item['rating'],
          str(item['reviews'])))
    conn.commit()

conn.close()
