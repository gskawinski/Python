import json
import pandas as pd

from kafka import KafkaConsumer

# ======= FUNCTIONS


def is_valid_order(order):
    """
    Validates an order to ensure all required fields are present and not null.

    Parameters:
        order (dict): The order to validate.

    Returns:
        bool: True if the order is valid, False otherwise.
    """

    required_keys = [
        "_order_number",
        "restaurant_name",
        "date_time",
        "user_name",
        "user_phone",
        "user_email",
        "delivery_address",
        "age",
        "card_type",
        "card_number",
        "customer_order",
        "total_cost",
    ]
    for key in required_keys:
        if key not in order or order[key] is None:
            return False
    return True


def save_orders_to_json(orders_df, file_path):
    """
    Saves the orders DataFrame to a JSON file. If the file exists, it appends the new records.

    Parameters:
        orders_df (pd.DataFrame): The orders DataFrame to save.
        file_path (str): The path to the JSON file.
    """
    if os.path.exists(file_path):
        existing_orders_df = pd.read_json(file_path, orient="records", lines=True)
        orders_df = pd.concat([existing_orders_df, orders_df], ignore_index=True)
    orders_df.to_json(file_path, orient="records", lines=True)


def add_order_to_df(orders_df, new_order):
    """
    Adds a new order to the DataFrame if it is valid and not a duplicate.

    Parameters:
        orders_df (pd.DataFrame): The existing orders DataFrame.
        new_order (dict): The new order to add.

    Returns:
        pd.DataFrame: The updated DataFrame with the new order added.
    """
    # check if order is valid
    if not is_valid_order(new_order):
        return orders_df

    # check if order is not duplicate
    if (
        not orders_df.empty
        and new_order["_order_number"] in orders_df["_order_number"].values
    ):
        return orders_df

    # Convert json order to DataFrame
    new_order_df = pd.DataFrame([new_order])

    return pd.concat([orders_df, new_order_df], ignore_index=True)


def calculate_summary_statistics(orders_df):
    """
    Calculates summary statistics from the existing orders DataFrame.
    - Total number of orders: Count the number of rows in the DataFrame.
    - Total revenue: Sum the total_cost column.
    - Average order value: Calculate the mean of the total_cost column.
    - Most popular restaurant: Find the mode of the restaurant_name column.
    - Most popular dish: Aggregate all items from the customer_order lists and find the mode.
    - Distribution of payment methods: Count occurrences of each payment method in the card_type column.

    Parameters:
            orders_df (pd.DataFrame): The DataFrame containing order data.

    Returns:
            dict: A dictionary containing summary statistics.
    """
    summary = {}

    # Total number of orders
    summary["total_orders"] = len(orders_df)

    # Total revenue
    summary["total_revenue"] = orders_df["total_cost"].sum()

    # Average order value
    summary["average_order_value"] = orders_df["total_cost"].mean()

    # Most popular restaurant
    if not orders_df.empty:
        summary["most_popular_restaurant"] = orders_df["restaurant_name"].mode().iloc[0]
    else:
        summary["most_popular_restaurant"] = None

    # Most popular dish
    all_items = []
    for customer_order in orders_df["customer_order"]:
        all_items.extend([item["item"] for item in customer_order])

    if all_items:
        summary["most_popular_dish"] = pd.Series(all_items).mode().iloc[0]
    else:
        summary["most_popular_dish"] = None

    # Distribution of payment methods
    summary["payment_method_distribution"] = (
        orders_df["card_type"].value_counts().to_dict()
    )

    return summary


# ====== MAIN =======

ORDER_CONFIRMED_KAFKA_TOPIC = "food_order_confirmed"


consumer = KafkaConsumer(
    ORDER_CONFIRMED_KAFKA_TOPIC, bootstrap_servers="localhost:9092"
)

total_orders_count = 0
total_revenue = 0

# Initialize an empty DataFrame to store orders, with the correct columns
orders_df = pd.DataFrame(
    columns=[
        "_order_number",
        "restaurant_name",
        "date_time",
        "user_name",
        "user_phone",
        "user_email",
        "delivery_address",
        "age",
        "card_type",
        "card_number",
        "customer_order",
        "total_cost",
    ]
)

order_count_threshold = (
    1000  # Number of orders after which data is saved to JSON file - periodic saving
)
order_count = 0  # Counter to track the number of orders processed
json_file_path = "orders_data.json"  # Path to the JSON file where orders are saved

print("Start of Analytics... listening")


while True:
    for message in consumer:
        print("Updating analytics..")
        consumed_message = json.loads(message.value.decode())

        # Get a new order
        new_order = consumed_message
        # Add the new order to the DataFrame
        orders_df = add_order_to_df(orders_df, new_order)
        order_count += 1

        # Calculate and print summary statistics
        summary_stats = calculate_summary_statistics(orders_df)
        print(json.dumps(summary_stats, indent=4))

        # Save the DataFrame to JSON after every 100 orders
        if order_count >= order_count_threshold:
            save_orders_to_json(orders_df, json_file_path)
            # orders_df = pd.DataFrame()  # Reset the DataFrame after saving
            # order_count = 0  # Reset the order count
            print("saved")
            # break

        total_cost = float(consumed_message["total_cost"])
        total_orders_count += 1
        total_revenue += total_cost


""" 
Explore correlations between columns.
Identify outliers.
Business Intelligence (BI) Charts: Create informative charts for stakeholders. Some useful BI charts include:
- Bar Charts: Show the distribution of orders by restaurant, user age group, etc.
- Pie Charts: Display the proportion of orders from different restaurants or payment methods.
- Time Series Plots: Visualize order trends over time (daily, weekly, monthly).
- Box Plots: Identify outliers in order amounts or delivery times.
- Heatmaps: Show correlations between features (e.g., age vs. order amount).

"""
