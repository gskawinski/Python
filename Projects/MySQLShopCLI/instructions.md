
Check if MariaDB is installed
> mysql --version

Start mariaDB / mysql as root
> sudo mysql -u root -p

Create user 'greg' user with a password 'greg'
> CREATE USER 'greg'@'localhost' IDENTIFIED BY 'greg';

Grant admin privileges to the 'greg' user
> GRANT ALL PRIVILEGES ON *.* TO 'greg'@'localhost' WITH GRANT OPTION;

Apply the changes and make them take effect
> FLUSH PRIVILEGES;

> Exit the MariaDB command-line client
EXIT;

Log into MariaDB as greg
> mysql -u greg -p

Create database
> CREATE DATABASE online_store;

Select db
> USE online_store;

Run SQL Script to load TABLE definitions
> source load_tables_def.sql

Verify the Tables
> SHOW TABLES;

Run SQL Script to load TABLE sample data
> source load_tables_data.sql

Verify if data is loaded

> SELECT * FROM Products LIMIT 2;
> SELECT * FROM Customers LIMIT 2;
> SELECT * FROM Orders LIMIT 2;
> SELECT * FROM OrderItems LIMIT 2;
> SELECT * FROM Payments LIMIT 2;
> SELECT * FROM Reviews LIMIT 2;
> SELECT * FROM Categories LIMIT 2;

Below action if deleta or truncate required

Delete Database, permanently removes the entire database and all its tables and data
> DROP DATABASE online_store;

To create and delete a database in one step, will drop the existing database if it exists and then create a new one.
> CREATE DATABASE IF NOT EXISTS online_store;

Truncate all Tables with foreign keys
Disable foreign key checks, to truncate tables with FK
> SET FOREIGN_KEY_CHECKS = 0;

List of tables to be truncated
> TRUNCATE TABLE Products;
> TRUNCATE TABLE Customers;
> TRUNCATE TABLE Orders;
> TRUNCATE TABLE OrderItems;
> TRUNCATE TABLE Payments;
> TRUNCATE TABLE Reviews;
> TRUNCATE TABLE Categories;

Re-enable foreign key checks
> SET FOREIGN_KEY_CHECKS = 1;
