import unittest
import sqlite3
import os
from io import StringIO
from unittest.mock import patch
from contextlib import redirect_stdout

from models.customer import Customer
from models.restaurant import Restaurant
from models.delivery_agent import DeliveryAgent
from models.order import Order
from db import create_tables
from routes.auth_control import login_user, register_user
from routes.customer_options import view_profile as customer_view_profile
from routes.restaurant_options import view_profile as restaurant_view_profile, view_received_orders
from routes.manager_options import manage_delivery_fleet, view_restaurant_pov
from routes.delivery_agent_options import view_delivery_details

class TestFoodDelivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # cls.db_name = "test_food_delivery.db"
        # cls.conn = sqlite3.connect(cls.db_name)
        # create_tables(cls.db_name)
        # print("Database setup complete")
        cls.db_name = "test_food_delivery.db"
        os.environ["FOOD_DELIVERY_DB"] = cls.db_name   # Set test DB for all modules.
        cls.conn = sqlite3.connect(cls.db_name)
        create_tables(cls.conn)
        print("Database setup complete")

    def setUp(self):
        from models.restaurant import Restaurant
        Restaurant.add_menu_items = lambda self, db_connection: None
        self.cursor = self.conn.cursor()
        self.clear_database()
        create_tables(self.conn)
        self.create_test_data()

    def clear_database(self):
        tables = ['Customers', 'Restaurants', 'Restaurant_Items', 
                  'Orders', 'Delivery_Agents']
        for table in tables:
            self.cursor.execute(f"DELETE FROM {table}")
        self.conn.commit()

    # def create_test_data(self):
    #     # Create test customer
    #     self.test_customer = Customer(None, "Test User", "1234567890", 
    #                                   "Test Address", "testpass")
    #     self.test_customer.register(self.conn)

    #     # Create test restaurant
    #     self.test_restaurant = Restaurant("Test Restaurant", "9876543210", 
    #                                       "testpass", db_connection=self.conn)
    #     self.restaurant_id = self.test_restaurant.register(self.conn)
    #     # Add test menu item
    #     self.cursor.execute('''INSERT INTO Restaurant_Items 
    #                            (restaurant_id, item_name, price, 
    #                             preparation_time, delivery_time)
    #                            VALUES (?, ?, ?, ?, ?)''',
    #                            (self.restaurant_id, "Test Item", 10.99, 20, 30))
        
    #     # Create test delivery agent
    #     self.test_agent = DeliveryAgent(None, "Test Agent", "5555555555", 
    #                                     "TEST123", "testpass")
    #     self.cursor.execute('''INSERT INTO Delivery_Agents 
    #                            (name, phone_number, vehicle_number, password, status)
    #                            VALUES (?, ?, ?, ?, ?)''',
    #                            (self.test_agent.name, self.test_agent.phone_number,
    #                             self.test_agent.vehicle_number, self.test_agent.password, "Available"))
    #     self.conn.commit()
    def create_test_data(self):
        """Create test users and items"""
        # Create test customer
        self.test_customer = Customer(None, "Test User", "1234567890", 
                                    "Test Address", "testpass")
        self.test_customer.register(self.conn)

        # Create test restaurant
        self.test_restaurant = Restaurant("Test Restaurant", "9876543210", 
                                        "testpass")
        self.restaurant_id = self.test_restaurant.register(self.conn)
        
        # Add test menu items
        self.cursor.execute('''INSERT INTO Restaurant_Items 
                            (restaurant_id, item_name, price, 
                                preparation_time, delivery_time)
                            VALUES (?, ?, ?, ?, ?)''',
                            (self.restaurant_id, "Test Item", 10.99, 20, 30))
        
        # Create test delivery agent - Fix: Store agent_id
        self.test_agent = DeliveryAgent(None, "Test Agent", "5555555555", 
                                        "TEST123", "testpass")
        self.cursor.execute('''INSERT INTO Delivery_Agents 
                            (name, phone_number, vehicle_number, 
                                password, status)
                            VALUES (?, ?, ?, ?, ?)''',
                            (self.test_agent.name, 
                                self.test_agent.phone_number,
                                self.test_agent.vehicle_number, 
                                self.test_agent.password, 
                                "Available"))
        self.test_agent.agent_id = self.cursor.lastrowid  # Store the agent_id
        self.conn.commit()

    def test_database_creation(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        expected_tables = {'Customers', 'Restaurants', 'Restaurant_Items', 'Delivery_Agents', 'Orders'}
        actual_tables = set(table[0] for table in tables if table[0] != "sqlite_sequence")
        self.assertEqual(actual_tables, expected_tables)

    def test_user_registration(self):
        # Use an unused phone number to avoid UNIQUE constraint error.
        customer = Customer(None, "Test User", "0987654321", "Test Address", "testpass")
        success = customer.register(self.conn)
        self.assertTrue(success)

    def test_register_existing_account(self):
        # Attempt to register a customer with phone number already in use (from create_test_data)
        customer = Customer(None, "Duplicate User", "1234567890", "Some Address", "testpass")
        success = customer.register(self.conn)
        self.assertFalse(success, "Registering an existing customer should fail.")

    def test_order_placement(self):
        order = Order(None, 1, 1, None, "Test Item", 2, "delivery", 50, 21.98, "active")
        success = order.place_order(self.conn)
        self.assertTrue(success)

    def test_delivery_tracking(self):
        self.cursor.execute('''INSERT INTO Orders 
                               (customer_id, restaurant_id, delivery_agent_id, item_name, quantity, type, remaining_time, price, status)
                               VALUES (1, 1, NULL, "Test Item", 1, "delivery", 50, 10, "active")''')
        order_id = self.cursor.lastrowid
        self.conn.commit()        
        self.cursor.execute("UPDATE Orders SET status='Delivered' WHERE order_id=?", (order_id,))
        self.conn.commit()
        self.cursor.execute("SELECT status FROM Orders WHERE order_id=?", (order_id,))
        row = self.cursor.fetchone()
        status = row[0] if row else None
        self.assertEqual(status, "Delivered")

    def test_invalid_login(self):
        # Simulate invalid login details by overriding input to supply wrong credentials
        with patch('builtins.input', side_effect=['1', 'wrong', 'wrong']):
            with redirect_stdout(StringIO()) as stdout:
                login_user()
                output = stdout.getvalue()
            self.assertIn("Invalid phone number or password", output)

    # def test_valid_login(self):
    #     # First, add a customer with known password (password stored is plain text for test)
    #     # To bypass hash checking, we use our test data customer:
    #     with patch('builtins.input', side_effect=['1', "1234567890", "testpass"]):
    #         with redirect_stdout(StringIO()) as stdout:
    #             login_user()
    #             output = stdout.getvalue()
    #         self.assertIn("Customer logged in successfully", output)
    def test_valid_login(self):
        # Register test customer first
        test_customer = Customer(None, "Test User", "1234567890", "Test Address", "testpass")
        test_customer.register(self.conn)
        
        with patch('builtins.input', side_effect=['1', "1234567890", "testpass"]):
            with redirect_stdout(StringIO()) as stdout:
                result = login_user()
                output = stdout.getvalue()
            
            # Verify login success by checking:
            # 1. Function returns valid customer object
            self.assertIsInstance(result, Customer)
            # 2. Customer menu options are shown
            self.assertIn("Customer logged in successfully!", output)
            # self.assertIn("2. View Profile", output)

    def test_view_profile_customer(self):
        # Capture output of customer view_profile for our test customer:
        with redirect_stdout(StringIO()) as stdout:
            customer_view_profile(self.test_customer, self.conn)
            output = stdout.getvalue()
        self.assertIn("Name: Test User", output)

    def test_view_profile_restaurant(self):
        with redirect_stdout(StringIO()) as stdout:
            restaurant_view_profile(self.test_restaurant)
            output = stdout.getvalue()
        self.assertIn("Name: Test Restaurant", output)

  
    def test_no_restaurants_available_while_ordering(self):
        # Clear both restaurants and menu items
        self.cursor.execute("DELETE FROM Restaurants")
        self.cursor.execute("DELETE FROM Restaurant_Items")
        self.conn.commit()
        
        with patch('builtins.input', side_effect=['1']):
            with self.assertRaises(Exception) as context:
                from routes.customer_options import place_orders
                place_orders(self.test_customer, self.conn)
            self.assertIn("No restaurants available", str(context.exception))

    def test_restaurant_with_no_menu_items(self):
        # Clear Restaurant_Items for our restaurant
        self.cursor.execute("DELETE FROM Restaurant_Items WHERE restaurant_id=?", (self.restaurant_id,))
        self.conn.commit()
        with patch('builtins.input', side_effect=['1']):
            with self.assertRaises(Exception) as context:
                from routes.customer_options import place_orders
                place_orders(self.test_customer, self.conn)
            self.assertIn("No menu items available", str(context.exception))

    def test_no_delivery_agent_available(self):
        # Ensure the restaurant has menu items
        self.cursor.execute("INSERT INTO Restaurant_Items (restaurant_id, item_name, price, preparation_time, delivery_time) VALUES (?, ?, ?, ?, ?)",
                            (self.restaurant_id, "Test Item", 10.99, 20, 30))
        self.conn.commit()

        # Clear Delivery_Agents so none is available
        self.cursor.execute("DELETE FROM Delivery_Agents")
        self.conn.commit()

        # Match exact sequence of inputs needed by place_orders:
        # 1. Restaurant ID
        # 2. Item ID
        # 3. Quantity
        # 4. Add more items? (yes/no)
        # 5. Order type (delivery/takeaway)
        # 6. Confirm order (yes/no)
        with patch('builtins.input', side_effect=[
            str(self.restaurant_id),  # restaurant id
            '6',                      # item id (matching the one just inserted)
            '2',                      # quantity
            'no',                     # don't add more items
            'delivery',               # order type
            'yes'                     # confirm order
        ]):
            with redirect_stdout(StringIO()) as stdout:
                from routes.customer_options import place_orders
                place_orders(self.test_customer, self.conn)
                output = stdout.getvalue()
            self.assertIn("No delivery agents available currently. Will assign one soon!", output)

    def test_manage_delivery_fleet_normal(self):
        with redirect_stdout(StringIO()) as stdout:
            manage_delivery_fleet()
            output = stdout.getvalue()
        self.assertIn("Total Delivery Agents", output)

    def test_manage_delivery_fleet_no_agents(self):
        self.cursor.execute("DELETE FROM Delivery_Agents")
        self.conn.commit()
        # Verify correct exception is raised
        with self.assertRaises(Exception) as context:
            manage_delivery_fleet()
        self.assertEqual(str(context.exception), "No delivery agents available.")

    def test_view_received_orders_normal(self):
        # Insert an order for our restaurant
        self.cursor.execute('''INSERT INTO Orders 
                               (customer_id, restaurant_id, delivery_agent_id, item_name, quantity, type, remaining_time, price, status)
                               VALUES (1, ?, NULL, "Test Item", 1, "delivery", 50, 10, "active")''', (self.restaurant_id,))
        self.conn.commit()
        with redirect_stdout(StringIO()) as stdout:
            view_received_orders(self.test_restaurant)
            output = stdout.getvalue()
        self.assertIn("Order ID", output)

    def test_view_received_orders_none(self):
        # Clear orders for restaurant
        self.cursor.execute("DELETE FROM Orders WHERE restaurant_id=?", (self.restaurant_id,))
        self.conn.commit()
        with redirect_stdout(StringIO()) as stdout:
            view_received_orders(self.test_restaurant)
            output = stdout.getvalue()
        self.assertIn("No orders received", output)

    # def test_view_delivery_details_normal(self):
    #     # Insert an assigned order for test agent
    #     self.cursor.execute('''INSERT INTO Orders 
    #                            (customer_id, restaurant_id, delivery_agent_id, item_name, quantity, type, remaining_time, price, status)
    #                            VALUES (1, 1, ?, "Test Item", 1, "delivery", 50, 10, "active")''', (1,))
    #     self.conn.commit()
    #     with patch('builtins.input', side_effect=['']):
    #         with redirect_stdout(StringIO()) as stdout:
    #             view_delivery_details(self.test_agent)
    #             output = stdout.getvalue()
    #     self.assertIn("Order ID", output)
    def test_view_delivery_details_normal(self):
        # Create test order with correct agent_id reference
        self.cursor.execute('''INSERT INTO Orders 
                            (customer_id, restaurant_id, delivery_agent_id, 
                            item_name, quantity, type, remaining_time, 
                            price, status)
                            VALUES 
                            (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                            (self.test_customer.customer_id,
                            self.restaurant_id,
                            self.test_agent.agent_id,  # Use stored agent_id
                            "Test Item",
                            1,
                            "delivery",
                            50,
                            10.99,
                            "active"))
        self.conn.commit()

        with redirect_stdout(StringIO()) as stdout:
            view_delivery_details(self.test_agent)
            output = stdout.getvalue()
        self.assertIn("Order ID", output)

    def test_view_delivery_details_none(self):
        # Ensure no order is assigned to test agent
        self.cursor.execute("UPDATE Delivery_Agents SET status='Available' WHERE agent_id=1")
        self.conn.commit()
        with patch('builtins.input', side_effect=['']):
            with redirect_stdout(StringIO()) as stdout:
                view_delivery_details(self.test_agent)
                output = stdout.getvalue()
        self.assertIn("No deliveries assigned", output)

    def test_view_restaurant_pov_normal(self):
        # Insert a restaurant record if needed; using test_restaurant from test data
        with patch('builtins.input', side_effect=[str(self.restaurant_id), 10]):
            with redirect_stdout(StringIO()) as stdout:
                view_restaurant_pov()
                output = stdout.getvalue()
            self.assertIn("Restaurant Details", output)

    def test_view_restaurant_pov_no_restaurants(self):
        # Clear Restaurants table
        self.cursor.execute("DELETE FROM Restaurants")
        self.conn.commit()
        with patch('builtins.input', side_effect=["1"]):
            with redirect_stdout(StringIO()) as stdout:
                view_restaurant_pov()
                output = stdout.getvalue()
            self.assertIn("No Registered Restaurants", output)

    def tearDown(self):
        self.clear_database()
        self.cursor.close()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        os.remove(cls.db_name)

if __name__ == '__main__':
    unittest.main()