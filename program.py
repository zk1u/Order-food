#!/usr/bin/evn python3

# Script to order food from thuisbezorgd.nl
# Todo: Recursion doesn't update variables
import re


class Main:

    def start(self):
        self.ask_for_user_information()
        print("Yay!")

    def ask_for_user_information(self):
        correct_information = False
        while not correct_information:
            postal_address = self.get_postal_code_input()
            cash_amount = self.get_cash_amount_input()
            print("You've entered the following data:\nPostal adress: " + str(postal_address) + "\nAmount of money: " + str(cash_amount))
            correct_information = (input("Is this correct? Please enter 'y'. If not, please enter 'n'") == 'y')
        return

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
        amount = input("Please enter the maximum amount of cash you are willing to spend. Please enter a whole number\n")
        try:
            return int(amount)
        except ValueError:
            print("Try again")
            self.get_cash_amount_input()


main = Main()
main.start()
