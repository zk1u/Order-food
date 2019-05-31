#!/usr/bin/evn python3

import requests
import re
import random
import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup


def format_string(string):

    string = string.replace("Min.", "")
    string = string.replace("€ ", "")
    string = string.replace(",", ".")
    string = string.replace(" ", "")
    string = string.replace("\n", "")
    return string

postal_code =  "2925BC"
base_url = "http://www.thuisbezorgd.nl/"
order_url = "http://www.thuisbezorgd.nl/eten-bestellen-krimpen-aan-den-ijssel-2925"
cash = 20.0

soup = BeautifulSoup(requests.get(order_url).text, 'html.parser')
restaurants = []
order = []
orders = []
dishes = []
final_order = []
for div in soup.findAll("div", {"class": "shim"}):  # filter non relevant classes
    div.decompose()

for div in soup.findAll("div", {"class": "detailswrapper"}):  # filter empty classes
    if re.match("^[ \t\n]*$", div.text):
        div.decompose()
        continue
    restaurants.append(div)

restaurants.pop()  # we don't need the last one

for restaurant in restaurants[:]:  # filter everything that's too expensive for us
    restaurant_status = restaurant.find("div", class_="avgdeliverytime").text
    if restaurant_status.upper() == "GESLOTEN":
        restaurants.remove(restaurant)
        continue
    delivery_costs = restaurant.find("div", class_="delivery-cost").text
    delivery_costs = format_string(delivery_costs)
    if delivery_costs == "GRATIS":
        delivery_costs = 0
    minimum_order_price = restaurant.find("div", class_="min-order").text
    minimum_order_price = format_string(minimum_order_price)

    if cash < float(delivery_costs) + float(minimum_order_price):
        restaurants.remove(restaurant)

if len(restaurants) == 0:
    print("No restaurant could be found for the amount of cash supplied")
    sys.exit()

restaurant_to_order_from = restaurants[random.randint(0, len(restaurants) - 1)]
restaurant_url = base_url + restaurant_to_order_from.a['href']

restaurant_web_page = BeautifulSoup(requests.get(restaurant_url).text, 'html.parser')

for div in restaurant_web_page.findAll("div", {"class":"meal"}):
    dishes.append(div)

for dish in dishes:
    order.append(dish.get("id"))
    order.append(format_string(dish.find("div", itemprop="price").text))
    orders.append(order.copy())
    order.clear()

random.shuffle(orders)

for order in orders[:]:
    if cash - float(order[1]) < 0:
        orders.remove(order)
        continue
    cash -= float(order[1])

print("Random order created.. Sending it to browser")

driver = webdriver.Chrome(os.getcwd() + "/chromedriver")
driver.get(order_url)
driver.get(restaurant_url)
driver.find_element_by_id("privacybanner").click()
time.sleep(1)
driver.find_element_by_id(orders[0][0]).click()
element = driver.find_element_by_name('mysearchstring_popupmode')
element.send_keys(postal_code)
element.submit()




