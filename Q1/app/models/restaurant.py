class Restaurant:
    def __init__(self, name, phone_number, password, restaurant_id=None, db_connection=None):
        self.name = name
        self.phone_number = phone_number
        self.password = password
        if restaurant_id is not None:
            self.restaurant_id = restaurant_id
        elif db_connection is not None:
            self._fetch_restaurant_id(db_connection)
        else:
            self.restaurant_id = None
        # print(f"Debug: restaurant_id after init: {self.restaurant_id}")

    def _fetch_restaurant_id(self, db_connection):
        cursor = db_connection.cursor()
        cursor.execute('''SELECT restaurant_id FROM Restaurants WHERE phone_number = ?''',
                       (self.phone_number,))
        result = cursor.fetchone()
        if result:
            self.restaurant_id = result[0]
        else:
            self.restaurant_id = None

    def register(self, db_connection):
        cursor = db_connection.cursor()
        cursor.execute('''INSERT INTO Restaurants (name, phone_number, password)
                          VALUES (?, ?, ?)''',
                       (self.name, self.phone_number, self.password))
        db_connection.commit()
        self.restaurant_id = cursor.lastrowid
        print(f"Restaurant registered with ID: {self.restaurant_id}")
        self.add_menu_items(db_connection)
        return self.restaurant_id

    def add_menu_items(self, db_connection):
        while True:
            item_name = input("Enter item name: ")
            price = float(input("Enter price: $"))
            preparation_time = int(input("Enter preparation time (minutes): "))
            delivery_time = int(input("Enter delivery time (minutes): "))
            self.add_menu_item(db_connection, item_name, price, preparation_time, delivery_time)
            
            more_items = input("Do you want to add more items? (yes/no): ").strip().lower()
            if more_items != 'yes':
                break

    def add_menu_item(self, db_connection, item_name, price, preparation_time, delivery_time):
        cursor = db_connection.cursor()
        cursor.execute('''INSERT INTO Restaurant_Items (restaurant_id, item_name, price, preparation_time, delivery_time) 
                          VALUES (?, ?, ?, ?, ?)''', 
                       (self.restaurant_id, item_name, price, preparation_time, delivery_time))
        db_connection.commit()
        print(f"Added '{item_name}' to the menu")

    def view_received_orders(self, conn):
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM Orders WHERE restaurant_id = ?''', (self.restaurant_id,))
        orders = cursor.fetchall()
        return orders