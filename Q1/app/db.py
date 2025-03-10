import os
import sqlite3

def get_db_file():
    # Use the test DB file if set; otherwise default to food_delivery.db.
    return os.getenv("FOOD_DELIVERY_DB", "food_delivery.db")

def get_db_connection():
    return sqlite3.connect(get_db_file())

def create_tables(db_input=None):
    if db_input is None:
        conn = get_db_connection()
        close_conn = True
    elif isinstance(db_input, sqlite3.Connection):
        conn = db_input
        close_conn = False
    else:
        conn = sqlite3.connect(db_input)
        close_conn = True

    cursor = conn.cursor()
    
    # Customers Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Customers (
                        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone_number TEXT UNIQUE NOT NULL,
                        address TEXT NOT NULL,
                        password TEXT NOT NULL)''')
    
    # Delivery Agents Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Delivery_Agents (
                        agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone_number TEXT UNIQUE NOT NULL,
                        vehicle_number TEXT NOT NULL,
                        password TEXT NOT NULL,
                        status TEXT CHECK(status IN ('Available', 'On Delivery')) DEFAULT 'Available')''')
    
    # Restaurants Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Restaurants (
                        restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone_number TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    
    # Restaurant Items Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Restaurant_Items (
                        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        restaurant_id INTEGER,
                        item_name TEXT NOT NULL,
                        price REAL NOT NULL,
                        preparation_time INTEGER NOT NULL,
                        delivery_time INTEGER NOT NULL,
                        FOREIGN KEY(restaurant_id) REFERENCES Restaurants(restaurant_id))''')
    
    # Orders Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        restaurant_id INTEGER NOT NULL,
        delivery_agent_id INTEGER,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        type TEXT NOT NULL,
        remaining_time INTEGER NOT NULL,
        price REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES Customers (customer_id),
        FOREIGN KEY (restaurant_id) REFERENCES Restaurants (restaurant_id),
        FOREIGN KEY (delivery_agent_id) REFERENCES Delivery_Agents (agent_id)
    )
    ''')
    
    conn.commit()
    # print("Database and Tables Created Successfully!")
    if close_conn:
        conn.close()

if __name__ == "__main__":
    create_tables()