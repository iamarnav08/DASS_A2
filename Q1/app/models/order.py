import sqlite3
from datetime import datetime
# from routes.common import load_data, save_data

try:
    # Try relative import first (for normal app operation)
    from routes.common import load_data, save_data
except ImportError:
    # Fall back to absolute import (for tests)
    from app.routes.common import load_data, save_data


class Order:
    def __init__(self, order_id, customer_id, restaurant_id, delivery_agent_id, item_name, quantity, order_type, remaining_time, price, status="active"):
        self.order_id = order_id
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.delivery_agent_id = delivery_agent_id
        self.item_name = item_name
        self.quantity = quantity
        self.order_type = order_type
        self.remaining_time = remaining_time
        self.price = price
        self.status = status
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "restaurant_id": self.restaurant_id,
            "delivery_agent_id": self.delivery_agent_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "order_type": self.order_type,
            "remaining_time": self.remaining_time,
            "price": self.price,
            "status": self.status,
            "timestamp": self.timestamp
        }


    def place_order(self, conn):
        try:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Orders (customer_id, restaurant_id, delivery_agent_id, item_name, quantity, type, remaining_time, price, status, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (self.customer_id, self.restaurant_id, self.delivery_agent_id, self.item_name, self.quantity, self.order_type, self.remaining_time, self.price, self.status, self.timestamp))
            self.order_id = cursor.lastrowid
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False

    @staticmethod
    def track_order(order_id):
        data = load_data()
        
        for order in data.get("orders", []):
            if order["order_id"] == order_id:
                print(f"\nOrder Status: {order['status']}")
                print(f"Restaurant: {order['restaurant_phone']}")
                print(f"Delivery Agent: {order['agent_phone'] or 'Not assigned'}")
                print(f"Items: {order['items']}")
                print(f"Total Amount: ${order['total_amount']}")
                print(f"Timestamp: {order['timestamp']}")
                return True
        
        print("Order not found!")
        return False