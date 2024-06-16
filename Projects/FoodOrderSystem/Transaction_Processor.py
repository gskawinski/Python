import json

from kafka import KafkaConsumer
from kafka import KafkaProducer

from uuid import UUID

# FUNCTIONS


def is_unique_order_number(order_number):
    """
    Check if uuid_to_test is a valid UUID.

    Parameters: uuid_to_test : str
        The UUID string to check.

    Returns: bool

    """
    try:
        uuid_obj = UUID(order_number, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == order_number


from datetime import datetime


def is_valid_datetime(date_time):
    """
    Check if the given date and time string is within the last 2 hours.

    Parameters : date_time : str
        A date and time string in the format "%Y-%m-%d %H:%M:%S".
    Returns : bool
        True if the date and time is within the last 2 hours, otherwise False.
    """
    now = datetime.now()
    order_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    time_difference = now - order_time
    if time_difference.total_seconds() > 7200:  # 2 hours in seconds
        return False
    return True


import re


def is_valid_email(email):
    """
    Perform email validity check logic
    Return True if email is valid, False otherwise
    """

    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    return bool(re.fullmatch(regex, email))


def is_valid_age(age):
    if 18 <= age <= 100:
        return True
    return False


def validate_credit_card(card_number: str) -> bool:
    """
    Validates a credit card number using the Luhn algorithm.

    Parameters: card_number : str
        The credit card number to validate (as a string).

    Returns: bool
        True if the credit card number is valid, otherwise False.

    """
    card_number = [int(num) for num in card_number]  # Convert to list of integers
    check_digit = card_number.pop(-1)  # Remove the last digit (check digit)
    card_number.reverse()  # Reverse the remaining digits
    card_number = [
        num * 2 if idx % 2 == 0 else num for idx, num in enumerate(card_number)
    ]  # Double digits at even indices
    card_number = [
        num - 9 if idx % 2 == 0 and num > 9 else num
        for idx, num in enumerate(card_number)
    ]  # Subtract 9 if over 9
    card_number.append(check_digit)  # Add the check digit back to the list
    check_sum = sum(card_number)  # Sum all digits
    return check_sum % 10 == 0  # If check sum is divisible by 10, it's valid


# from sklearn.ensemble import IsolationForest


def is_valid_total_cost(total_cost):
    # Use Isolation Forest algorithm to detect fraudulent transactions or for anomaly detection
    # The predictions will be either -1 (anomaly) or 1 (normal).
    # https://medium.com/@waleedmousa975/building-a-real-time-fraud-detection-system-for-financial-transactions-with-kafka-and-machine-8bf2ad869ac
    # https://github.com/amancodeblast/Credit-Card-Fraud-Detection

    # define model
    # model = IsolationForest(
    #     n_estimators=100, max_samples="auto", contamination="auto", random_state=42
    # )
    # # model.fit(X_train)  # X_train contains your feature matrix
    # # y_pred = model.predict(X_test)  # X_test contains your test feature matrix
    # X_pred = [[total_cost]]
    # y_pred = model.predict(X_pred)
    # if y_pred[0] == -1:
    #     print(f"Fraudulent transaction detected: {total_cost}")
    #     return False
    return True


def process_food_order(data):
    """
    Perform order validity check
    """
    # order = json.loads(data)
    order = data
    order_number = order["_order_number"]
    restaurant_name = order["restaurant_name"]
    date_time = order["date_time"]
    user_name = order["user_name"]
    user_phone = order["user_phone"]
    user_email = order["user_email"]
    delivery_address = order["delivery_address"]
    age = order["age"]
    card_number = order["card_number"]
    customer_order = order["customer_order"]
    total_cost = order["total_cost"]

    # Initialize status and failure_reason
    status = "valid"
    failure_reason = None

    # Perform food order validity checks
    if not is_unique_order_number(order_number):
        status = "invalid"
        failure_reason = "Order number is not unique"
    elif not is_valid_datetime(date_time):
        status = "invalid"
        failure_reason = "Date and time is not valid"
    elif not is_valid_email(user_email):
        status = "invalid"
        failure_reason = "Address email not valid"
    elif not is_valid_age(age):
        status = "invalid"
        failure_reason = "Age not valid"
    elif not validate_credit_card(card_number):
        status = "invalid"
        failure_reason = "Credit Card not valid"
    elif not is_valid_total_cost(total_cost):
        status = "invalid"
        failure_reason = "Total Cost not valid"

    if status == "invalid":
        order = None

    return {"status": status, "failure_reason": failure_reason, "data": order}


## ================== MAIN

from pymongo import MongoClient

# Initialize MongoDB client
MONGO_URI = "mongodb://your_mongodb_uri"
client = MongoClient(MONGO_URI)
db = client["food_ordr_database"]
collection = db["food_order_logs"]

ORDER_KAFKA_TOPIC = "food_order_details"
ORDER_CONFIRMED_KAFKA_TOPIC = "food_order_confirmed"
KAFKA_BROKER = "localhost:9092"

consumer = KafkaConsumer(ORDER_KAFKA_TOPIC, bootstrap_servers=KAFKA_BROKER)
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

print("Start Processing Orders")
while True:
    for message in consumer:
        print("Ongoing transaction..")
        consumed_message = json.loads(message.value.decode())
        print(consumed_message)
        data = consumed_message
        order_valid = process_food_order(data)

        if order_valid["status"] == "valid":
            # Send order data to Kafka confirmed topic for further order processing
            producer.send(ORDER_CONFIRMED_KAFKA_TOPIC, json.dumps(data).encode("utf-8"))

            # Save raw order data to MongoDB
            # collection.insert_one(data)

            # Print log
            print(f"Successful transaction for order ID : {data['_order_number']} ")
