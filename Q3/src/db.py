import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="ecommerce.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS User (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userID INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_type TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS RetailCustomer (
                id INTEGER PRIMARY KEY,
                orderCount INTEGER DEFAULT 0,
                FOREIGN KEY (id) REFERENCES User(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS BulkCustomer (
                id INTEGER PRIMARY KEY,
                orderCount INTEGER DEFAULT 0,
                FOREIGN KEY (id) REFERENCES User(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Product (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                productID INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                retailPrice REAL NOT NULL,
                bulkPrice REAL NOT NULL,
                inventory_count INTEGER DEFAULT 0
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Order_Table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orderID INTEGER NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivery_date TIMESTAMP,
                total_amount REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES User(id),
                FOREIGN KEY (product_id) REFERENCES Product(id)
            )
        ''')

        self.conn.commit()

    def add_user(self, userID, name, email, password, user_type):
        try:
            self.cursor.execute(
                "INSERT INTO User (userID, name, email, password, user_type) VALUES (?, ?, ?, ?, ?)",
                (userID, name, email, password, user_type)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def add_retail_customer(self, user_id):
        try:
            self.cursor.execute(
                "INSERT INTO RetailCustomer (id) VALUES (?)",
                (user_id,)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def add_bulk_customer(self, user_id):
        try:
            self.cursor.execute(
                "INSERT INTO BulkCustomer (id) VALUES (?)",
                (user_id,)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def add_product(self, productID, name, category, description, retailPrice, bulkPrice, inventory_count=0):
        self.cursor.execute(
            "INSERT INTO Product (productID, name, category, description, retailPrice, bulkPrice, inventory_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (productID, name, category, description, retailPrice, bulkPrice, inventory_count)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def create_order(self, orderID, user_id, product_id, quantity, total_amount, delivery_date=None):
        try:
            if delivery_date is None:
                delivery_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if quantity<1:
                return None
            
            self.cursor.execute(
                "INSERT INTO Order_Table (orderID, user_id, product_id, quantity, delivery_date, total_amount) VALUES (?, ?, ?, ?, ?, ?)",
                (orderID, user_id, product_id, quantity, delivery_date, total_amount)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def apply_discount_to_order(self, order_id, discount_percentage):
        try:
            # Get the current total amount
            self.cursor.execute("SELECT total_amount FROM Order_Table WHERE id = ?", (order_id,))
            result = self.cursor.fetchone()
            
            if result:
                current_amount = result[0]
                discounted_amount = current_amount * (1 - discount_percentage / 100)
                
                # Update the order with the discounted amount
                self.cursor.execute(
                    "UPDATE Order_Table SET total_amount = ? WHERE id = ?",
                    (discounted_amount, order_id)
                )
                self.conn.commit()
                return True
            return False
        except sqlite3.Error:
            return False

    def get_user_orders(self, user_id):
        self.cursor.execute("""
            SELECT o.id, p.name, o.order_date, o.delivery_date, o.total_amount 
            FROM Order_Table o
            JOIN Product p ON o.product_id = p.id
            WHERE o.user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()