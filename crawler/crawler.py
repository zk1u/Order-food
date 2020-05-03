#!/usr/bin/env python3

import requests
import re
import random
import sys
import os
import time
import yaml
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from bs4 import BeautifulSoup

def order():
    print("Reading config.yaml..")

    with open("config.yaml", 'r') as ymlfile:
        try:
            cfg = yaml.safe_load(ymlfile)
        except yaml.YAMLError as exception:
            print(exception)
            sys.exit()

    def format_string(string):

        string = string.replace("Min.", "")
        string = string.replace("€ ", "")
        string = string.replace(",", ".")
        string = string.replace(" ", "")
        string = string.replace("\n", "")
        return string

    print("Creating random order..")

    postal_code =  cfg['address']['postalcode']
    base_url = "http://www.thuisbezorgd.nl/"
    order_url = "http://www.thuisbezorgd.nl/eten-bestellen-krimpen-aan-den-ijssel-2925"
    cash = cfg['cash']

    soup = BeautifulSoup(requests.get(order_url).text, 'html.parser')
    restaurants = []
    order = []
    orders = []
    dishes = []
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

    if restaurant_to_order_from.find("div", class_="delivery-cost").text != 'GRATIS':
        cash -= float(format_string(restaurant_to_order_from.find("div", class_="delivery-cost").text))

    restaurant_url = base_url + restaurant_to_order_from.a['href']

    print(restaurant_url)
    time.sleep(10)

    restaurant_web_page = BeautifulSoup(requests.get(restaurant_url).text, 'html.parser')

    for div in restaurant_web_page.findAll("div", {"class":"meal-container"}):
        dishes.append(div)

    #print(dishes)

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

    chrome_options = Options()  
    #chrome_options.add_argument("--headless")  

    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=os.getcwd() + "/chromedriver")
    driver.get(order_url)
    driver.get(restaurant_url)
    cookiebanner_ok_button = driver.find_element_by_class_name("cc-banner__btn-ok")
    if cookiebanner_ok_button is not None:
        cookiebanner_ok_button.click()
    # driver.find_element_by_id("privacybanner").click()
    # time.sleep(1)
    print(orders)
    driver.find_element_by_id(orders[0][0]).click()
    time.sleep(1)
    element = driver.find_element_by_name("mysearchstring")
    element.send_keys(postal_code)
    element.send_keys(Keys.ENTER)
    time.sleep(5)

    for order in orders:
        driver.execute_script("window.scrollTo(0, document.documentElement.clientHeight - 20)")
        time.sleep(2)
        meal_div = driver.find_element_by_id(order[0])
        try: 
            meal_div.find_element_by_class_name("sidedish-content")
            print("This meal does not contain any sidedishes")
            time.sleep(5)
            meal_div.click()
        except:
            print("This meal contains side dishes")
            time.sleep(5)
            meal_div.click()
            time.sleep(1)
            meal_div.find_element_by_class_name("cartbutton-button").click()
        time.sleep(2)

    driver.find_element_by_class_name("cartbutton-button").click()
    driver.find_element_by_name("address").send_keys(cfg['address']['streetname'] + ' ' + str(cfg['address']['housenumber']))
    driver.find_element_by_name("postcode").clear()  # clear prefilled postalcode
    driver.find_element_by_name("postcode").send_keys(cfg['address']['postalcode'])
    driver.find_element_by_name("surname").send_keys(cfg['userdetails']['name'])
    driver.find_element_by_name("email").send_keys(cfg['userdetails']['mail'])
    driver.find_element_by_name("phonenumber").send_keys(cfg['userdetails']['phonenumber'])

    select = Select(driver.find_element_by_name('deliverytime'))
    select.select_by_index(1)

    driver.find_element_by_class_name("paymentmethod3").click()
    time.sleep(1)
    select = Select(driver.find_element_by_id('iidealbank'))
    select.select_by_visible_text('Rabobank')
    driver.find_element_by_class_name("checkout-orderbutton-btn").click()
    url = driver.current_url
    driver.quit()
    return url








