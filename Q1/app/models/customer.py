import sqlite3

class Customer:
    def __init__(self, customer_id, name, phone_number, address, password):
        self.customer_id = customer_id
        self.name = name
        self.phone_number = phone_number
        self.address = address
        self.password = password

    def register(self, conn):
        try:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Customers (name, phone_number, address, password) VALUES (?, ?, ?, ?) ''', 
                        (self.name, self.phone_number, self.address, self.password))
            self.customer_id = cursor.lastrowid
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False

    def view_profile(self, conn):
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM Customers WHERE phone_number = ?''', (self.phone_number,))
        return cursor.fetchone()