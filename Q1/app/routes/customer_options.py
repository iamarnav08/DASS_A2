import sqlite3
try:
    from routes.common import logout_user
    from models.order import Order
except ImportError:
    from app.routes.common import logout_user
    from app.models.order import Order

from datetime import datetime
import time

def customer_options(customer):
    # conn = sqlite3.connect('food_delivery.db')
    from db import get_db_connection
    conn = get_db_connection()
    while True:
        print("\nWelcome, {}!".format(customer.name))
        print("1. View Profile")
        print("2. Place Order")
        print("3. Track Order")
        print("4. Logout")
        choice = input("Please select an option\n")

        if choice == '1':
            view_profile(customer, conn)
        elif choice == '2':
            place_orders(customer, conn)
        elif choice == '3':
            track_order(customer, conn)
        elif choice == '4':
            logout_user()
            break
        else:
            print("Invalid option. Try Again.")
    conn.close()

def view_profile(customer, conn):
    print("\nProfile Information:")
    print(f"Name: {customer.name}")
    print(f"Phone Number: {customer.phone_number}")
    print(f"Address: {customer.address}")

def place_orders(customer, conn):
    cursor = conn.cursor()
    # Check for restaurants first
    cursor.execute('''SELECT * FROM Restaurants''')
    restaurants = cursor.fetchall()
    if not restaurants:
        raise Exception("No restaurants available")
    
    print("\nAvailable Restaurants:")
    for restaurant in restaurants:
        print(f"Restaurant ID: {restaurant[0]}, Name: {restaurant[1]}, Phone: {restaurant[2]}")
    
    restaurant_id = int(input("Enter the Restaurant ID: "))
    cursor.execute('''SELECT * FROM Restaurant_Items WHERE restaurant_id = ?''', (restaurant_id,))
    menu_items = cursor.fetchall()
    
    if not menu_items:
        raise Exception("No menu items available")
    
    order_items = []
    total_price = 0
    while True:
        item_id = int(input("Enter the Item ID: "))
        item = next((item for item in menu_items if item[0] == item_id), None)
        if not item:
            print("Invalid Item ID")
            continue
        quantity = int(input("Enter the quantity: "))
        order_items.append((item, quantity))
        total_price += item[3] * quantity
        if input("Do you want to add more items? (yes/no): ").strip().lower() != 'yes':
            break
    
    if not order_items:
        raise Exception("No items added to the order")
    
    order_type = input("Enter order type (takeaway/delivery): ").strip().lower()
    delivery_agent_id = None
    if order_type == 'delivery':
        try:
            from models.delivery_agent import DeliveryAgent
        except ImportError:
            from app.models.delivery_agent import DeliveryAgent
            
        available_agents = DeliveryAgent.get_available_agents(conn)
        if available_agents:
            selected_agent = available_agents[0]
            delivery_agent_id = selected_agent[0]
            
            # Update delivery agent status
            cursor.execute('''UPDATE Delivery_Agents SET status = 'On Delivery' WHERE agent_id = ?''',
                           (delivery_agent_id,))
        else:
            print("No delivery agents available currently. Will assign one soon!")
            # Continue without delivery agent
    
    print(f"\nTotal Price: ${total_price:.2f}")
    if input("Confirm order? (yes/no): ").strip().lower() != 'yes':
        raise Exception("Order cancelled by user")
    
    # Place orders
    initial_status = 'Pending Driver' if (order_type == 'delivery' and not delivery_agent_id) else 'active'
    
    for item, quantity in order_items:
        order = Order(
            order_id=None,
            customer_id=customer.customer_id,
            restaurant_id=restaurant_id,
            delivery_agent_id=delivery_agent_id,
            item_name=item[2],
            quantity=quantity,
            order_type=order_type,
            remaining_time=item[4] + (item[5] if order_type == 'delivery' else 0),
            price=item[3] * quantity,
            status=initial_status
        )
        order.place_order(conn)

# def place_orders(customer, conn):
#     try:
#         cursor = conn.cursor()
#         cursor.execute('BEGIN TRANSACTION')
        
#         # Get customer ID
#         cursor.execute('''SELECT customer_id FROM Customers WHERE phone_number = ?''', (customer.phone_number,))
#         customer_id = cursor.fetchone()
#         if not customer_id:
#             raise Exception("Customer not found")
#         customer.customer_id = customer_id[0]
        
#         # Get available restaurants
#         cursor.execute('''SELECT * FROM Restaurants''')
#         restaurants = cursor.fetchall()
#         if not restaurants:
#             raise Exception("No restaurants available")
        
#         print("\nAvailable Restaurants:")
#         for restaurant in restaurants:
#             print(f"Restaurant ID: {restaurant[0]}, Name: {restaurant[1]}, Phone: {restaurant[2]}")
        
#         restaurant_id = int(input("\nEnter the Restaurant ID you want to order from: "))
        
#         # Get menu items
#         cursor.execute('''SELECT * FROM Restaurant_Items WHERE restaurant_id = ?''', (restaurant_id,))
#         menu_items = cursor.fetchall()
#         if not menu_items:
#             raise Exception("No menu items available for the selected restaurant")
        
#         print("\nMenu Items:")
#         for item in menu_items:
#             print(f"Item ID: {item[0]}, Name: {item[2]}, Price: ${item[3]}, Preparation Time: {item[4]} mins")
        
#         order_items = []
#         total_price = 0
        
#         while True:
#             item_id = int(input("\nEnter the Item ID you want to order: "))
#             quantity = int(input("Enter the quantity: "))
            
#             cursor.execute('''SELECT * FROM Restaurant_Items WHERE item_id = ? AND restaurant_id = ?''', 
#                          (item_id, restaurant_id))
#             item = cursor.fetchone()
            
#             if item:
#                 order_items.append((item, quantity))
#                 total_price += item[3] * quantity
#             else:
#                 print("Invalid Item ID")
                
#             if input("Do you want to add more items? (yes/no): ").strip().lower() != 'yes':
#                 break
        
#         if not order_items:
#             raise Exception("No items added to the order")
        
#         order_type = input("Enter order type (takeaway/delivery): ").strip().lower()
#         delivery_agent_id = None
#         if order_type == 'delivery':
#             from models.delivery_agent import DeliveryAgent
#             available_agents = DeliveryAgent.get_available_agents(conn)
#             if available_agents:
#                 selected_agent = available_agents[0]
#                 delivery_agent_id = selected_agent[0]
                
#                 # Update delivery agent status
#                 cursor.execute('''UPDATE Delivery_Agents SET status = 'On Delivery' WHERE agent_id = ?''',
#                              (delivery_agent_id,))
#             else:
#                 print("No delivery agents available currently. Will assign one soon!")
#                 # Continue without delivery agent
        
#         print(f"\nTotal Price: ${total_price:.2f}")
#         if input("Confirm order? (yes/no): ").strip().lower() != 'yes':
#             raise Exception("Order cancelled by user")
        
#         # Place orders
#         initial_status = 'Pending Driver' if (order_type == 'delivery' and not delivery_agent_id) else 'active'
        
#         for item, quantity in order_items:
#             order = Order(
#                 order_id=None,
#                 customer_id=customer.customer_id,
#                 restaurant_id=restaurant_id,
#                 delivery_agent_id=delivery_agent_id,
#                 item_name=item[2],
#                 quantity=quantity,
#                 order_type=order_type,
#                 remaining_time=item[4] + (item[5] if order_type == 'delivery' else 0),
#                 price=item[3] * quantity,
#                 status=initial_status
#             )
#             if not order.place_order(conn):
#                 raise Exception("Failed to place order")
        
#         conn.commit()
#         print("Order placed successfully!")
        
#     except sqlite3.Error as e:
#         print(f"Database error: {e}")
#         conn.rollback()
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         conn.rollback()
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
        

def track_order(customer, conn):
    try:
        cursor = conn.cursor()
        
        while True:
            cursor.execute('''
                SELECT Orders.*, Restaurant_Items.preparation_time, Restaurant_Items.delivery_time, 
                       Delivery_Agents.name as agent_name 
                FROM Orders 
                JOIN Restaurant_Items ON Orders.item_name = Restaurant_Items.item_name 
                LEFT JOIN Delivery_Agents ON Orders.delivery_agent_id = Delivery_Agents.agent_id
                WHERE Orders.customer_id = ? AND Orders.status != 'Delivered'
            ''', (customer.customer_id,))
            
            active_orders = cursor.fetchall()
            
            if not active_orders:
                print("No active orders found.")
                return

            print("\nActive Orders:")
            print("-" * 50)
            
            all_delivered = True
            for order in active_orders:
                order_id, _, restaurant_id, delivery_agent_id, item_name, quantity, \
                order_type, initial_time, price, status, timestamp, prep_time, delivery_time, agent_name = order
                
                # Calculate elapsed time
                order_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                current_time = datetime.now()
                elapsed_minutes = (current_time - order_time).total_seconds() / 60
                
                # Calculate remaining times based on phase
                if elapsed_minutes < prep_time:
                    # Still in preparation phase
                    remaining_prep = prep_time - elapsed_minutes
                    remaining_delivery = delivery_time if order_type == 'delivery' else 0
                    phase = "Preparation"
                else:
                    # Preparation done
                    remaining_prep = 0
                    if order_type == 'delivery':
                        if delivery_agent_id:
                            # Delivery phase with assigned driver
                            delivery_elapsed = elapsed_minutes - prep_time
                            remaining_delivery = max(0, delivery_time - delivery_elapsed)
                            phase = "Delivery"
                        else:
                            # Waiting for driver
                            remaining_delivery = delivery_time
                            phase = "Awaiting Driver"
                    else:
                        # Takeaway order
                        remaining_delivery = 0
                        phase = "Ready for pickup"

                total_remaining = remaining_prep + remaining_delivery
                
                # Update status
                if total_remaining == 0:
                    cursor.execute('''
                        UPDATE Orders SET status = 'Delivered' WHERE order_id = ?
                    ''', (order_id,))
                    if delivery_agent_id:
                        cursor.execute('''
                            UPDATE Delivery_Agents SET status = 'Available' 
                            WHERE agent_id = ?
                        ''', (delivery_agent_id,))
                    conn.commit()
                    status = 'Delivered'
                elif status == 'Pending Driver':
                    from models.delivery_agent import DeliveryAgent
                    available_agents = DeliveryAgent.get_available_agents(conn)
                    if available_agents:
                        new_agent = available_agents[0]
                        cursor.execute('''
                            UPDATE Orders 
                            SET delivery_agent_id = ?, status = 'active' 
                            WHERE order_id = ?
                        ''', (new_agent[0], order_id))
                        cursor.execute('''
                            UPDATE Delivery_Agents 
                            SET status = 'On Delivery' 
                            WHERE agent_id = ?
                        ''', (new_agent[0],))
                        conn.commit()
                        delivery_agent_id = new_agent[0]
                        agent_name = new_agent[1]

                # Display order information
                print(f"Order ID: {order_id}")
                print(f"Item: {item_name} x {quantity}")
                print(f"Type: {order_type}")
                print(f"Phase: {phase}")
                if remaining_prep > 0:
                    print(f"Preparation Time Remaining: {int(remaining_prep)} minutes")
                if order_type == 'delivery':
                    if delivery_agent_id:
                        print(f"Delivery Time Remaining: {int(remaining_delivery)} minutes")
                        print(f"Delivery Agent: {agent_name}")
                    else:
                        print("Awaiting driver assignment")
                print(f"Total Time Remaining: {int(total_remaining)} minutes")
                print("-" * 50)
                
                if status != 'Delivered':
                    all_delivered = False
            
            if all_delivered:
                print("All orders delivered!")
                break
                
            time.sleep(10)  # Update every 10 seconds
            print("\033[H\033[J")  # Clear terminal screen
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
    try:
        cursor = conn.cursor()
        
        while True:
            cursor.execute('''
                SELECT Orders.*, Delivery_Agents.name as agent_name 
                FROM Orders 
                LEFT JOIN Delivery_Agents ON Orders.delivery_agent_id = Delivery_Agents.agent_id
                WHERE Orders.customer_id = ? AND Orders.status != 'Delivered'
            ''', (customer.customer_id,))
            
            active_orders = cursor.fetchall()
            
            if not active_orders:
                print("No active orders found.")
                return

            print("\nActive Orders:")
            print("-" * 50)
            
            all_delivered = True
            for order in active_orders:
                order_id, _, restaurant_id, delivery_agent_id, item_name, quantity, \
                order_type, initial_time, price, status, timestamp, agent_name = order
                
                # Calculate remaining time
                order_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                current_time = datetime.now()
                elapsed_minutes = (current_time - order_time).total_seconds() / 60
                remaining_mins = max(0, initial_time - elapsed_minutes)
                
                # Update status based on remaining time
                if remaining_mins == 0:
                    cursor.execute('''
                        UPDATE Orders SET status = 'Delivered' WHERE order_id = ?
                    ''', (order_id,))
                    if delivery_agent_id:
                        cursor.execute('''
                            UPDATE Delivery_Agents SET status = 'Available' 
                            WHERE agent_id = ?
                        ''', (delivery_agent_id,))
                    conn.commit()
                    status = 'Delivered'
                elif status == 'Pending Driver':
                    # Check if we can assign a driver
                    from models.delivery_agent import DeliveryAgent
                    available_agents = DeliveryAgent.get_available_agents(conn)
                    if available_agents:
                        new_agent = available_agents[0]
                        cursor.execute('''
                            UPDATE Orders 
                            SET delivery_agent_id = ?, status = 'active' 
                            WHERE order_id = ?
                        ''', (new_agent[0], order_id))
                        cursor.execute('''
                            UPDATE Delivery_Agents 
                            SET status = 'On Delivery' 
                            WHERE agent_id = ?
                        ''', (new_agent[0],))
                        conn.commit()
                        agent_name = new_agent[1]
                        delivery_agent_id = new_agent[0]
                elif remaining_mins < initial_time * 0.3:
                    status = 'Nearly Done'
                elif remaining_mins < initial_time * 0.7:
                    status = 'In Progress'
                else:
                    status = 'Processing'
                
                # Display order information
                print(f"Order ID: {order_id}")
                print(f"Item: {item_name} x {quantity}")
                print(f"Type: {order_type}")
                print(f"Status: {status}")
                if status == 'Pending Driver':
                    print("Delivery Agent: Will be assigned soon")
                elif agent_name:
                    print(f"Delivery Agent: {agent_name}")
                print(f"Remaining Time: {int(remaining_mins)} minutes")
                print("-" * 50)
                
                if status != 'Delivered':
                    all_delivered = False
            
            if all_delivered:
                print("All orders delivered!")
                break
                
            time.sleep(10)  # Update every 10 seconds
            print("\033[H\033[J")  # Clear terminal screen
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()