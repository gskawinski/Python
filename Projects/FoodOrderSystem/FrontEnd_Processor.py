import json
import os
import random
from datetime import datetime
import uuid
from pprint import pprint
import time

from faker import Faker

fake = Faker("en_US")  # with PL locales to create PL data

# Load restaurant data/offer from restaurant_menus.json
with open("restaurant_menus.json", "r") as f:
    restaurants_data = json.load(f)


# Function to generate a unique order number
def generate_order_number():
    # return str(uuid.uuid4().int & (1 << 63) - 1)  # Generates a UUID-based orde
    return str(uuid.uuid4())


# Function to display available cuisine choices
def display_cuisine_choices(data):
    cuisines = set()  # Use a set to store unique cuisine choices
    for restaurant in data:
        cuisines.add(restaurant["Category"])

    print("Available Cuisine Choices:")
    for index, cuisine in enumerate(cuisines, start=1):
        print(f"{index}. {cuisine}")


# Function to create a new automatic order
def create_order_automatic(restaurants_data):
    # print(f"\nAutomatic online food order system!\n")
    # choose cuisine / restaurant
    chosen_cuisine = random.choice(restaurants_data)
    # print(f"You have chosen the cuisine: {chosen_cuisine['Category']}")
    # choose the dishes and quantity
    dishes_chosen = random.sample(chosen_cuisine["Menu"], random.randint(1, 3))
    # print(f"You have chosen the dishes: {dishes_chosen}")

    # create main order
    # current time
    now = datetime.now()
    # generate uniqe order number using UUID technique
    order_number = generate_order_number()

    # Define a list of card types
    card_types = ["visa", "mastercard", "amex", "discover"]
    card_type = random.choice(card_types)

    order = {
        "_order_number": order_number,
        "restaurant_name": chosen_cuisine["Name"],
        "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_name": fake.name(),
        "user_phone": fake.phone_number(),
        "user_email": fake.email(),
        "delivery_address": fake.address(),
        "age": random.randint(15, 99),
        # "birthday": fake.date_of_birth().isoformat(),
        # "text_request": fake.text(),
        # "website": fake.url(),
        "card_type": card_type,
        "card_number": fake.credit_card_number(card_type=card_type),
    }

    # indywidual components order and total cost
    items = []
    total_cost = 0
    for elem in dishes_chosen:
        item_name = elem["dish"]
        item_price = elem["price"]
        quantity = random.randint(1, 2)
        total_item_cost = item_price * quantity
        total_cost += total_item_cost
        items.append(
            {
                "item": item_name,
                "quantity": quantity,
                "total_item_cost": total_item_cost,
            }
        )

    # print("\nYour Automatic Order:")
    # for item in items:
    #     print(f"{item['quantity']} x {item['item']} - ${item['total_item_cost']}")
    # print(f"Total Cost: ${total_cost}")
    # print("Thank you for your order!\n")

    # order items to main order
    order["customer_order"] = items
    order["total_cost"] = round(total_cost, 2)

    return order
