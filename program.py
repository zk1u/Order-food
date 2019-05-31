#!/usr/bin/evn python3

import requests
import re
import random
import sys

from bs4 import BeautifulSoup


def format_string(string):
    string = string.replace("Min.", "")
    string = string.replace("€ ", "")
    string = string.replace(",", ".")
    return string


base_url = "http://www.thuisbezorgd.nl/"
order_url = "http://www.thuisbezorgd.nl/eten-bestellen-krimpen-aan-den-ijssel-2925"
cash = 20.0

soup = BeautifulSoup(requests.get(order_url).text, 'html.parser')
restaurants = []
food = []
for div in soup.findAll("div", {"class": "shim"}):  # filter non relevant classes
    div.decompose()

for div in soup.findAll("div", {"class": "detailswrapper"}):  # filter empty classes
    if re.match("^[ \t\n]*$", div.text):
        div.decompose()
        continue
    restaurants.append(div)

restaurants.pop()  # we don't need the last one

for restaurant in restaurants[:]:  # filter everything that's too expensive for us
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

restaurant_web_page = BeautifulSoup(requests.get(base_url + restaurant_to_order_from.a['href']).text, 'html.parser')

for div in restaurant_web_page.findAll("div", {"class":"meal"}):
    food.append(div)

for foods in food:
    print(foods)
