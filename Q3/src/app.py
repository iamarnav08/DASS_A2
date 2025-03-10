import getpass
from db import DatabaseManager

class App:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None

    def register(self):
        print("Register")
        userID = int(input("Enter user ID: "))
        name = input("Enter name: ")
        email = input("Enter email: ")
        password = getpass.getpass("Enter password: ")
        user_type = input("Enter user type (retail/bulk): ").lower()

        user_id = self.db.add_user(userID, name, email, password, user_type)
        if user_id:
            if user_type == "retail":
                self.db.add_retail_customer(user_id)
            elif user_type == "bulk":
                self.db.add_bulk_customer(user_id)
            print("Registration successful!")
        else:
            print("Registration failed. User ID or email might already be in use.")

    def login(self):
        print("Login")
        email = input("Enter email: ")
        password = getpass.getpass("Enter password: ")

        self.db.cursor.execute("SELECT * FROM User WHERE email = ? AND password = ?", (email, password))
        user = self.db.cursor.fetchone()
        if user:
            self.current_user = user
            print(f"Login successful! Welcome, {user[2]}")
        else:
            print("Login failed. Invalid email or password.")

    def search_items(self):
        self.db.cursor.execute("SELECT DISTINCT category FROM Product")
        categories = self.db.cursor.fetchall()
        if categories:
            print("Available categories:")
            for category in categories:
                print(f"- {category[0]}")
        else:
            print("No categories found.")

        category = input("Enter category to search: ").lower()
        self.db.cursor.execute("SELECT * FROM Product WHERE category = ?", (category,))
        products = self.db.cursor.fetchall()
        if products:
            print(f"Products in category '{category}':")
            for product in products:
                print(f"ID: {product[1]}, Name: {product[2]}, Price: {product[5]}")
        else:
            print(f"No products found in category '{category}'.")

    def place_order(self):
        product_id = int(input("Enter product ID to buy: "))
        quantity = int(input("Enter quantity: "))
        self.db.cursor.execute("SELECT * FROM Product WHERE productID = ?", (product_id,))
        product = self.db.cursor.fetchone()
        if product:
            total_amount = product[5] * quantity if self.current_user[7] == "retail" else product[6] * quantity
            order_id = self.db.create_order(product_id, self.current_user[0], product_id, quantity, total_amount)
            if order_id:
                print("Order placed successfully!")
            else:
                print("Failed to place order.")
        else:
            print("Invalid product ID.")

    def logout(self):
        self.current_user = None
        print("Logged out successfully.")

    def run(self):
        while True:
            if self.current_user:
                print("\n1. Search items by category")
                print("2. Place order")
                print("3. Logout")
                choice = input("Enter choice: ")
                if choice == "1":
                    self.search_items()
                elif choice == "2":
                    self.place_order()
                elif choice == "3":
                    self.logout()
                else:
                    print("Invalid choice. Please try again.")
            else:
                print("\n1. Register")
                print("2. Login")
                print("3. Exit")
                choice = input("Enter choice: ")
                if choice == "1":
                    self.register()
                elif choice == "2":
                    self.login()
                elif choice == "3":
                    break
                else:
                    print("Invalid choice. Please try again.")

if __name__ == "__main__":
    app = App()
    app.run()