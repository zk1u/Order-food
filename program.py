#!/usr/bin/evn python3

# Script to order food from thuisbezorgd.nl
# Todo: Recursion doesn't update variables

import requests
import re
import random
import sys

from bs4 import BeautifulSoup

# url = "http://www.thuisbezorgd.nl/findRestaurants.php"
# data = {"searchstring": "3011XR", "type": "postcode"}
# print(requests.post(url, data={"searchstring": "3011XR", "type": "postcode"}).text)

class Main:
    def start(self):
        self.ask_for_user_information()
        Scraper.scrape(Scraper(self._postal_code, self._user_cash))

    def ask_for_user_information(self):
        postal_code = self.get_postal_code_input()
        user_cash = self.get_cash_amount_input()
        print("You've entered the following data:\nPostal adress: " + str(postal_code) + "\nAmount of money: " + str(user_cash))
        correct_information = input("Is this correct? Please enter 'y'. If not, please enter 'n'")
        if correct_information == 'y':
            self._postal_code=postal_code
            self._user_cash=user_cash
        else:
            self.ask_for_user_information()


    def get_postal_code_input(self):
        postal_code = input("Please enter your postal address without any spaces. For example: 3011XR\n")
        if len(postal_code) < 6 :
            print("Postal code too short")
            self.get_postal_code_input()
        elif len(postal_code) > 6 :
            print("Postal code too long")
            self.get_postal_code_input()
        self.check_postal_code_regex(postal_code)
        return postal_code

    def check_postal_code_regex(self, postal_code):
        regex = "\d{4}?[A-Z]{2}"
        if not re.search(regex, postal_code):
            print("Postal code invalid")
            self.get_postal_code_input()
        return True

    def get_cash_amount_input(self):
        amount = input("Please enter the maximum amount of cash you are willing to spend. Enter a number with the following format: 20.00\n")
        try:
            return float(amount)
        except ValueError:
            print("Try again")
            self.get_cash_amount_input()

class Scraper:
    url = "http://www.thuisbezorgd.nl"

    def __init__(self, postal_code, user_cash):
        self._user_cash=user_cash
        self._postal_code=postal_code

    def scrape(self):
        scraped_restaurant_details = self.get_restaurant_details()
        restaurants = self.map_scraped_restaurant_details(scraped_restaurant_details)
        restaurant_to_order_from = self.pick_random_restaurant(restaurants)

    def get_restaurant_details(self):
        search_url = "http://www.thuisbezorgd.nl/eten-bestellen-krimpen-aan-den-ijssel-2925"
        soup = BeautifulSoup(requests.get(search_url).text, 'html.parser')
        return soup.findAll("div", {"class": "detailswrapper"})

    def map_scraped_restaurant_details(self, scraped_restaurant_details):
        restaurants = []
        scraped_restaurant_details.pop()  # last entry is of no use
        for scraped_restaurant_detail in scraped_restaurant_details:
            restaurant = Restaurant()
            restaurant.name = self.map_restaurant_name(scraped_restaurant_detail)
            restaurant.url = self.map_restaurant_url(scraped_restaurant_detail)
            restaurant.minimum_order_amount = self.map_minimum_order_amount(scraped_restaurant_detail)
            restaurant.delivery_costs = self.map_delivery_costs(scraped_restaurant_detail)
            restaurants.append(restaurant)
        return restaurants

    def map_restaurant_name(self, scraped_restaurant_detail):
        return " ".join(scraped_restaurant_detail.a.text.split())  # remove whitespaces from name

    def map_restaurant_url(self, scraped_restaurant_detail):
        return self.url + scraped_restaurant_detail.a['href']

    def map_minimum_order_amount(self, scraped_restaurant_detail):
        amount = scraped_restaurant_detail.find("div", class_="min-order").text
        amount = amount.replace("Min.", "")
        return self.amount_in_euros_to_float(amount)

    def map_delivery_costs(self, scraped_restaurant_detail):
        amount = scraped_restaurant_detail.find("div", class_="delivery-cost").text
        if amount == "GRATIS":
            return 0
        else:
            amount = amount.replace("€ ", "")
            amount = amount.replace(",", ".")
            return self.amount_in_euros_to_float(amount)

    def amount_in_euros_to_float(self, amount_in_euros):
        amount_in_euros = amount_in_euros.replace("€ ", "")
        amount_in_euros = amount_in_euros.replace(",", ".")
        amount_in_euros = " ".join(amount_in_euros.split())
        return float(amount_in_euros)

    def pick_random_restaurant(self, restaurants):
        user_cash = self._user_cash
        if len(restaurants) == 0:
            print("Couldn't find any restaurants where " + str(user_cash) + " euro would be enough money. See ya!")
            sys.exit()
        else:
            random_number = random.randint(0, len(restaurants) - 1)
            picked_restaurant = restaurants[random_number]
            if (picked_restaurant.delivery_costs + picked_restaurant.minimum_order_amount) > user_cash:
                restaurants.remove(picked_restaurant)
                self.pick_random_restaurant(restaurants)
            else:
                print(picked_restaurant.name)
                return picked_restaurant




class Restaurant:
    def __init__(self):
        self._name = None
        self._url = None
        self._delivery_costs = None
        self._minimum_order_amount = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def delivery_costs(self):
        return self._delivery_costs

    @delivery_costs.setter
    def delivery_costs(self, delivery_costs):
        self._delivery_costs = delivery_costs

    @property
    def minimum_order_amount(self):
        return self._minimum_order_amount

    @minimum_order_amount.setter
    def minimum_order_amount(self, minimum_order_amount):
        self._minimum_order_amount = minimum_order_amount


main = Main()
main.start()
