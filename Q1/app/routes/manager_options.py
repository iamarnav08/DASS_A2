import sqlite3
# from routes.common import logout_user
# from db import get_db_connection   # <--- Import the helper
try:
    from routes.common import logout_user
    from db import get_db_connection
except ImportError:
    from app.routes.common import logout_user
    from app.db import get_db_connection



def manager_options():
    while True:
        print("\nWelcome, Company Manager!")
        print("1. Manage Delivery Fleet")
        print("2. View Restaurant POV")
        print("3. Logout")
        choice = input("Please select an option\n")

        if choice == '1':
            manage_delivery_fleet()
        elif choice == '2':
            view_restaurant_pov()
        elif choice == '3':
            logout_user()
            break
        else:
            print("Invalid option. Try Again.")

def manage_delivery_fleet():
    # conn = get_db_connection()  # use the helper
    # cursor = conn.cursor()
    # cursor.execute('''SELECT * FROM Delivery_Agents''')
    # agents = cursor.fetchall()
    
    # if not agents:
    #     print("No delivery agents available.")
    #     conn.close()
    #     return
    
    # print("\nDelivery Fleet Information:")
    # total_agents = len(agents)
    # available_agents = sum(1 for agent in agents if agent[4] == 'Available')
    # on_delivery_agents = total_agents - available_agents
    
    # print(f"Total Delivery Agents: {total_agents}")
    # print(f"Available: {available_agents}")
    # print(f"On Delivery: {on_delivery_agents}")
    
    # conn.close()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM Delivery_Agents''')
    agents = cursor.fetchall()
    
    if not agents:
        conn.close()
        raise Exception("No delivery agents available.")
    
    print("\nDelivery Fleet Information:")
    total_agents = len(agents)
    available_agents = sum(1 for agent in agents if agent[4] == 'Available')
    on_delivery_agents = total_agents - available_agents
    
    print(f"Total Delivery Agents: {total_agents}")
    print(f"Available: {available_agents}")
    print(f"On Delivery: {on_delivery_agents}")
    
    conn.close()

def view_restaurant_pov():
    conn = get_db_connection()  # use the helper
    cursor = conn.cursor()
    
    cursor.execute('''SELECT * FROM Restaurants''')
    restaurants = cursor.fetchall()
    
    if not restaurants:
        print("No Registered Restaurants.")
        conn.close()
        return
    
    print("\nRegistered Restaurants:")
    for restaurant in restaurants:
        print(f"Restaurant ID: {restaurant[0]}, Name: {restaurant[1]}, Phone: {restaurant[2]}")
    
    restaurant_id = int(input("\nEnter the Restaurant ID you want to view: "))
    
    cursor.execute('''SELECT * FROM Restaurants WHERE restaurant_id = ?''', (restaurant_id,))
    restaurant = cursor.fetchone()
    
    if not restaurant:
        print("Invalid Restaurant ID.")
        conn.close()
        return
    
    print(f"\nRestaurant Details:\nName: {restaurant[1]}\nPhone: {restaurant[2]}")
    
    cursor.execute('''SELECT * FROM Restaurant_Items WHERE restaurant_id = ?''', (restaurant_id,))
    menu_items = cursor.fetchall()
    print("\nMenu Items:")
    for item in menu_items:
        print(f"Item ID: {item[0]}, Name: {item[2]}, Price: ${item[3]}, Preparation Time: {item[4]} mins, Delivery Time: {item[5]} mins")
    
    cursor.execute('''SELECT * FROM Orders WHERE restaurant_id = ? AND status = 'active' ''', (restaurant_id,))
    active_orders = cursor.fetchall()
    print("\nActive Orders:")
    if active_orders:
        for order in active_orders:
            print(f"Order ID: {order[0]}, Customer ID: {order[1]}, Item: {order[4]}, Quantity: {order[5]}, Type: {order[6]}, Remaining Time: {order[7]} mins, Price: ${order[8]:.2f}")
    else:
        print("No active orders found.")
    
    cursor.execute('''SELECT * FROM Orders WHERE restaurant_id = ? AND status = 'completed' ''', (restaurant_id,))
    completed_orders = cursor.fetchall()
    print("\nCompleted Orders:")
    if completed_orders:
        for order in completed_orders:
            print(f"Order ID: {order[0]}, Customer ID: {order[1]}, Item: {order[4]}, Quantity: {order[5]}, Type: {order[6]}, Remaining Time: {order[7]} mins, Price: ${order[8]:.2f}")
    else:
        print("No completed orders found.")
    
    conn.close()
    # conn = sqlite3.connect('food_delivery.db')
    conn = get_db_connection()  # using the helper
    cursor = conn.cursor()
    
    # Step 2: Fetch restaurant information
    cursor.execute('''SELECT * FROM Restaurants''')
    restaurants = cursor.fetchall()
    
    if not restaurants:
        print("No Registered Restaurants.")
        conn.close()
        return
    
    # Step 3: Display the list of registered restaurants
    print("\nRegistered Restaurants:")
    for restaurant in restaurants:
        print(f"Restaurant ID: {restaurant[0]}, Name: {restaurant[1]}, Phone: {restaurant[2]}")
    
    # Step 4: Company Manager selects a restaurant
    restaurant_id = int(input("\nEnter the Restaurant ID you want to view: "))
    
    # Step 5: Display restaurant details
    cursor.execute('''SELECT * FROM Restaurants WHERE restaurant_id = ?''', (restaurant_id,))
    restaurant = cursor.fetchone()
    
    if not restaurant:
        print("Invalid Restaurant ID.")
        conn.close()
        return
    
    print(f"\nRestaurant Details:\nName: {restaurant[1]}\nPhone: {restaurant[2]}")
    
    # Fetch and display menu items
    cursor.execute('''SELECT * FROM Restaurant_Items WHERE restaurant_id = ?''', (restaurant_id,))
    menu_items = cursor.fetchall()
    print("\nMenu Items:")
    for item in menu_items:
        print(f"Item ID: {item[0]}, Name: {item[2]}, Price: ${item[3]}, Preparation Time: {item[4]} mins, Delivery Time: {item[5]} mins")
    
    # Fetch and display active orders
    cursor.execute('''SELECT * FROM Orders WHERE restaurant_id = ? AND status = 'active' ''', (restaurant_id,))
    active_orders = cursor.fetchall()
    print("\nActive Orders:")
    if active_orders:
        for order in active_orders:
            print(f"Order ID: {order[0]}, Customer ID: {order[1]}, Item: {order[3]}, Quantity: {order[4]}, Type: {order[5]}, Remaining Time: {order[6]} mins, Price: ${order[7]:.2f}")
    else:
        print("No active orders found.")
    
    # Fetch and display past completed orders
    cursor.execute('''SELECT * FROM Orders WHERE restaurant_id = ? AND status = 'completed' ''', (restaurant_id,))
    completed_orders = cursor.fetchall()
    print("\nCompleted Orders:")
    if completed_orders:
        for order in completed_orders:
            print(f"Order ID: {order[0]}, Customer ID: {order[1]}, Item: {order[3]}, Quantity: {order[4]}, Type: {order[5]}, Remaining Time: {order[6]} mins, Price: ${order[7]:.2f}")
    else:
        print("No completed orders found.")
    
    conn.close()