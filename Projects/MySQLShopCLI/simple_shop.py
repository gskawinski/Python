
import mysql.connector
from datetime import datetime
import time
import random
from faker import Faker
import bcrypt  # Import the bcrypt librar
from pprint import pprint

# Initialize Faker 
fake = Faker()

# Database connection parameters
db_config = {
    "host": "localhost",
    "user": "greg",
    "password": "greg",
    "database": "online_store"
}

# Connect to the MySQL server
db_conn = mysql.connector.connect(**db_config)
cursor = db_conn.cursor()


# ======= FUNCTIONS =============
# Function to perform basic input sanitation (use default values if not provided)
# need to be extended for datatype check, REGEX check etc.
def sanitize_input(input_value, default_value):
    return input_value if input_value else default_value

# Function to create/add a new product to DB
def add_product(product_data):
    try:
        insert_query = "INSERT INTO Products (ProductName, Description, Price, Category, StockQuantity, Manufacturer, ReleaseDate, ImageURL) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, product_data)
        db_conn.commit()
        return cursor.lastrowid  # Return the ID of the newly created product
    except Exception as e:
        print("Error creating product:", e)
        db_conn.rollback()

# Function to read product information by ID or select a random product
def read_product(product_id=None):
    try:
        if product_id is None:
            select_query = "SELECT * FROM Products ORDER BY RAND() LIMIT 1"
            cursor.execute(select_query)
        else:
            select_query = "SELECT * FROM Products WHERE ProductID = %s"
            cursor.execute(select_query, (product_id,))

        # Get the column names from the cursor description
        column_names = [desc[0] for desc in cursor.description]

        product_data = cursor.fetchone()

        if product_data:
            # Convert the result to a dictionary with column names as keys
            product_dict = dict(zip(column_names, product_data))
            return product_dict
        else:
            return None

    except Exception as e:
        print("Error reading product information:", e)

# Function to create a new consumer with a hashed password
def create_consumer(username, password, first_name, last_name, email, phone, address):
    # Generate a password hash using bcrypt
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        insert_query = "INSERT INTO Customers (Username, PasswordHash, FirstName, LastName, Email, Phone, Address, RegistrationDate) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())"
        cursor.execute(insert_query, (username, password_hash, first_name, last_name, email, phone, address))
        db_conn.commit()
        return cursor.lastrowid  # Return the ID of the newly created customer
    except Exception as e:
        print("Error creating customer:", e)
        db_conn.rollback()

# Function to get consumer data
def get_customer_data(customer_id):
    try:
        # Fetch customer information from the database
        select_query = "SELECT * FROM Customers WHERE CustomerID = %s"
        cursor.execute(select_query, (customer_id,))
        customer_data = cursor.fetchone()

        if customer_data:
            # Define the column names to use as keys in the dictionary
            column_names = [desc[0] for desc in cursor.description]

            # Create a dictionary with column names as keys and customer data as values
            customer_dict = dict(zip(column_names, customer_data))
            return customer_dict
        else:
            return None
    except Exception as e:
        print("Error fetching customer data:", e)

# Function to list all products
def list_all_products(list_categories=False, category_name=None):
    # list avalible categories
    if list_categories:
        # Fetch and return the list of unique categories
        try:
            cursor.execute("SELECT DISTINCT Category FROM Products")
            categories = cursor.fetchall()
            categories = [category[0] for category in categories]
            return categories
        
        except Exception as e:
            print("Error fetching category list:", e)
            return []

    elif category_name:
        # Fetch and return the list of products in the specified category
        try:
            cursor.execute("SELECT ProductID, ProductName, Price FROM Products WHERE Category = %s", (category_name,))
            products = cursor.fetchall()
            return products
        
        except Exception as e:
            print(f"Error fetching products in the '{category_name}' category:", e)
            return []

    else:
        # Fetch and return the list of all products
        try:
            cursor.execute("SELECT ProductID, ProductName, Price FROM Products")
            products = cursor.fetchall()
            return products
        except Exception as e:
            print("Error fetching all products:", e)
            return []
        
# Function to get product details by product ID and return a product (dictionary)
def get_product_details(product_id):
    try:
        select_query = "SELECT * FROM Products WHERE ProductID = %s"
        cursor.execute(select_query, (product_id,))
        product_data = cursor.fetchone()

        if product_data:
            # Get the column names from the cursor description
            column_names = [desc[0] for desc in cursor.description]

            # Create a dictionary using column names as keys
            product_dict = dict(zip(column_names, product_data))
            return product_dict
        else:
            return None
    except Exception as e:
        print("Error fetching product details:", e)

# Function to display product review and avg, sort reviews if necessary (asc/desc)
def display_product_reviews(product_id, sorting_direction=None):
    try:
        # base query to fetch reviews, with no sorting
        select_query = "SELECT Rating, Comment, ReviewDate FROM Reviews WHERE ProductID = %s"
        # apply sorting if a direction is provided
        # add sorting direction
        if sorting_direction:
            select_query += f" ORDER BY Rating {sorting_direction}"

        cursor.execute(select_query, (product_id,))
        reviews = cursor.fetchall()
        total_ratings = 0
        num_reviews = len(reviews)

        if num_reviews > 0:
            for review in reviews:
                rating, comment, review_date = review
                total_ratings += rating
                print(f"Rating: {rating}, Review Date: {review_date}, Comment: {comment}")

            average_rating = total_ratings / num_reviews
            print(f"\nAverage Rating: {average_rating:.2f}")
        else:
            print("No reviews found for this product.")
    except Exception as e:
        print("Error fetching and displaying product reviews:", e)

# Function to create a new multiple-item order
def create_order(customer_id, order_items):
    try:
        # Begin a transaction
        # db_conn.start_transaction()

        # Check if a transaction is already active
        if not db_conn.in_transaction:
            # Begin a new transaction
            db_conn.start_transaction()

        # Initialize the total amount
        total_amount = 0

        # Insert a new order in the Orders table, with total amount = 0
        insert_order_query = "INSERT INTO Orders (CustomerID, OrderDate, TotalAmount, OrderStatus) VALUES (%s, NOW(), 0, 'pending')"
        cursor.execute(insert_order_query, (customer_id,))
        order_id = cursor.lastrowid  # Get the order ID

        # Process each item in the order
        for item in order_items:
            product_id, quantity = item

            # Fetch the product price from the database
            select_product_price_query = "SELECT Price FROM Products WHERE ProductID = %s"
            cursor.execute(select_product_price_query, (product_id,))
            product_price = cursor.fetchone()[0]

            # Calculate the item price
            item_total_cost = product_price * quantity

            # Insert order item
            insert_order_item_query = "INSERT INTO OrderItems (OrderID, ProductID, Quantity, ItemPrice) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_order_item_query, (order_id, product_id, quantity, item_total_cost))

            # Add the item's cost to the total amount
            total_amount += item_total_cost
            # Wait for 1 second
            time.sleep(0.5)

        # Update the total amount in the order
        update_order_query = "UPDATE Orders SET TotalAmount = %s WHERE OrderID = %s"
        cursor.execute(update_order_query, (total_amount, order_id))

         # Commit the transaction if it was started in this function
        if not db_conn.in_transaction:
            db_conn.commit()
        
        # Commit the transaction
        #db_conn.commit()

        return order_id
    except Exception as e:
        print("Error creating order:", e)
        db_conn.rollback()

# Function to count TABLE items count
def count_entities(entity_type):
    if entity_type == "customers":
        query = "SELECT COUNT(*) FROM Customers"
    elif entity_type == "orders":
        query = "SELECT COUNT(*) FROM Orders"
    elif entity_type == "products":
        query = "SELECT COUNT(*) FROM Products"
    else:
        print("Invalid entity type. Use 'customers', 'orders', or 'products'.")
        return None

    try:
        cursor.execute(query)
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"Error counting {entity_type}: {e}")
        return None

# Function to get all order details
def get_order_details(order_id):
    try:
        # Query to retrieve order details, customer information, and product information
        select_query = """
        SELECT Orders.OrderID, Orders.OrderDate, Orders.TotalAmount, Orders.OrderStatus,
               Customers.CustomerID, Customers.FirstName, Customers.LastName, Customers.Email
        FROM Orders
        JOIN Customers ON Orders.CustomerID = Customers.CustomerID
        WHERE Orders.OrderID = %s
        """
        
        cursor.execute(select_query, (order_id,))
        order_data = cursor.fetchall()
        
        if order_data:
            # Get the column names from the cursor description
            column_names = [desc[0] for desc in cursor.description]
            order_details = dict(zip(column_names, order_data[0]))
            order_details['OrderItems'] = []  # Add an empty list for order items

            # Query to retrieve order items with quantity and price
            order_items_query = """
            SELECT OrderItems.ProductID, Products.ProductName, OrderItems.Quantity, OrderItems.ItemPrice
            FROM OrderItems
            JOIN Products ON OrderItems.ProductID = Products.ProductID
            WHERE OrderItems.OrderID = %s
            """

            cursor.execute(order_items_query, (order_id,))
            order_items = cursor.fetchall()
            for item in order_items:
                item_dict = dict(zip(['ProductID', 'ProductName', 'Quantity', 'ItemPrice'], item))
                order_details['OrderItems'].append(item_dict)

            return order_details
        else:
            return None
    except Exception as e:
        print("Error fetching order details:", e)

# Function to retrieve customer orders
def get_customer_orders(customer_id):
    select_query = "SELECT * FROM Orders WHERE CustomerID = %s"
    cursor.execute(select_query, (customer_id,))
    return cursor.fetchall()


# ======= MAIN 
print("\nWelcome to Simple Shop")
while True:
    
    print("\nWhat do you want to do. \nOptions:")
    print("1. Create User")
    print("2. Get Product List")
    print("3. Get Product Details")
    print("4. Get Product Reviews")
    print("5. Create Order")
    print("6. Get Customer Orders")
    print("7. Make Payment")
    print("8. Add Product to Shop")
    print("-1. Exit")

    option = input("Select an option: ")

    if option == "1":
    # Option to create a user
        # Example usage for creating a new consumer
        new_consumer_id = create_consumer(
            fake.user_name(),       # Username
            fake.password(length=8), # password
            fake.first_name(),      # First Name
            fake.last_name(),       # Last Name
            fake.email(),           # Email
            fake.phone_number(),    # Phone
            fake.address().replace("'", "''")   # Address
        )
        if new_consumer_id:
            print(f"New consumer created with ID {new_consumer_id}")
            # get new customer data 
            customer_info = get_customer_data(new_consumer_id)
            if customer_info:
                print("New Customer Data:")
                pprint(customer_info)

    elif option == "2":
    # Option to get a product list
        # Call the list_all_products to get list of categories
        # List categories
        categories = list_all_products(list_categories=True)
        print("List of Product Categories:", categories)
        #category_name = input("Enter Category to List (empty for ALL products): ")
        # Prompt the user to input their choice
        user_input = input(f"Enter Category Number (1-{len(categories)}) or Name (empty for ALL products): ")
        # Check if the user input is empty
        if user_input.strip() == "":
            selected_category = None    # "ALL products"
        else:
            try:
                # Try to convert the user input to an integer
                choice = int(user_input)
                if 1 <= choice <= len(categories):
                    selected_category = categories[choice - 1]
                else:
                    print("Invalid category number.")
                    selected_category = None
            except ValueError:
                # If it's not an integer, treat it as a string and check if it's in the list
                if user_input in categories:
                    selected_category = user_input
                else:
                    print("Invalid category name.")
                    selected_category = None

        category_name = selected_category
        products = list_all_products(category_name=category_name)
        
        # Convert Decimal values to float and create a new list
        # display_data = [(id, name, float(price)) for id, name, price in products]

        if products:
            print(f"\nProducts in the '{category_name}' category:")
            print(f"(Product ID, Product Name, Price):")
            for item in products:
                print(item)
        else: print("Incorrect Category - Try Again")

    elif option == "3":
        # Option to get product details by product ID
        product_id = input("Enter Product ID: ")
        # Read_product data
        product_details = get_product_details(product_id)

        if product_details:
            print("\nProduct Details:")
            for key, value in product_details.items():
                print(f"{key} : {value}")
        else:
            print("Product not found.")
        
    elif option == "4":
        # Option to get product reviews by product ID
        product_id = input("Enter Product ID : ")
        # Display_product_reviews for product_id
        sorting_direction = "asc"  # Change this to "asc" or "desc" for sorting, or set to None for no sorting
        #display_product_reviews(product_id, sorting_direction)
        display_product_reviews(product_id)

    elif option == "5":
        # Option to create an order
        customer_count = count_entities("customers")
        customer_id = random.randint(1, customer_count) 
        #customer_id = input("Enter Customer ID: ")
        product_count = count_entities("products")

        #order_items = [(33, 2), (35, 1)]  # ProductID and quantity =
        order_items = []

        #product_id = input("Enter Product ID: ")
        #quantity = input("Enter Quantity: ")
        for _ in range( random.randint(1, 3)  ):
            # Generate random product ID and quantity
            product_id = random.randint(1, product_count)
            quantity = random.randint(1, 3)
            order_items.append( (product_id, quantity) )

        new_order_id = create_order(customer_id, order_items)
        if new_order_id:
            print("New Order ID:", new_order_id)
            print(f"\nNew Order for Customer: {customer_id}, Item ID / Quantities: {order_items}")
            # print the order details
            order_details = get_order_details(new_order_id)

            if order_details:
                print("Order Details:")
                for key, value in order_details.items():
                    if key == 'OrderItems':
                        print("Order Items:")
                        for item in value:
                            items_ordered =""
                            for item_key, item_value in item.items():
                                items_ordered += f"{item_key} : {item_value}, "
                                # print(f"{item_key} : {item_value}")
                            print(f"{items_ordered}")     # print indyvidual items order.
                        continue
                    print(f"{key} : {value}")           # print order details
                    
                total_amount = order_details['TotalAmount']
                print(f"Total Price: {total_amount}")
                print("You can proceed with the payment to initiate the shipping process.")

            else:
                print("Order not found.")
                
    elif option == "6":
        # Option to get all orders for a customer
        customer_id = input("Enter Customer ID: ")
       
        customer_orders = get_customer_orders(customer_id=customer_id)
        if customer_orders:
            if isinstance(customer_orders, list):
                print("Customer Orders:")
                for order in customer_orders:
                    print(order)
            elif isinstance(customer_orders, str):
                print(customer_orders)
        else:
            print("Orders not found.")


    elif option == "7":
        # Option to Make a Payment for given Order ID.
        order_id = input("Enter Order ID for payment: ")
        order_details = get_order_details(order_id)

        if order_details:
            print("Order Details:")
            print(order_details)
            payment_amount = order_details["TotalAmount"]
            payment_methods =["Card", "PayPal", "Wire"]
            payment_method = random.choice(payment_methods)
            order_id_status = order_details["OrderStatus"]
            # transaction_id = input("Enter Transaction ID: ")
        else:
            print("Order not found.")

    elif option == "8":
    # Option to add a product to the shop
    # add santizied input with default value.. etc

        # define variables
        categories = [ 'Electronics', 'Clothing', 'Furniture', 'Toys','Sports','Home','Shoes','Jewelry','Appliances']
        manufacturers = ['Sony', 'Samsung', 'Apple', 'Nike', 'Adidas', 'Ford', 'Toyota', 'Honda', 'LG', 'Microsoft', 'Sony', 'Panasonic', 'Audi', 'Dell', 'Lenovo', 'Philips', 'LG', 'Sony', 'Puma', 'New Balance']

        product_data = (
            fake.word(),                        # product name
            fake.sentence(),                    # description
            round(random.uniform(10, 1000), 2),     # price
            random.choice(categories),      # categories
            random.randint(1, 1000),        # stock quantity
            random.choice(manufacturers), 
            fake.date_between(start_date='-2y', end_date='today'),  # relase date
            fake.image_url()
        )
        new_product_id = add_product(product_data)
        if new_product_id:
            print(f"New product created with ID {new_product_id}")
            # Reading a product by ID
            product_info = read_product(new_product_id)
            if product_info:
                print("Product Information:", product_info)

    elif option == "-1":
    # Option to exit the program
        break

    else:
        print("Invalid Option. Press 1-7")


# Close the database connection
cursor.close()
db_conn.close()
print("Bye Bye\n")