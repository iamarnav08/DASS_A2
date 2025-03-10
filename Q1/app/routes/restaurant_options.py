import sqlite3
try:
    from routes.common import logout_user
except ImportError:
    from app.routes.common import logout_user

def restaurant_options(restaurant):
    while True:
        print("\nWelcome, {}!".format(restaurant.name))
        print("1. View Profile")
        print("2. View Received Orders")
        print("3. Logout")
        choice = input("Please select an option\n")

        if choice == '1':
            view_profile(restaurant)
        elif choice == '2':
            view_received_orders(restaurant)
        elif choice == '3':
            logout_user()
            break
        else:
            print("Invalid option. Try Again.")

def view_profile(restaurant):
    print("\nProfile Information:")
    print(f"Name: {restaurant.name}")
    print(f"Phone Number: {restaurant.phone_number}")

def view_received_orders(restaurant):
    # conn = sqlite3.connect('food_delivery.db')
    try:
        from db import get_db_connection
    except ImportError:
        from app.db import get_db_connection
        
    conn = get_db_connection()
    cursor = conn.cursor()
    # print(f"Debug: Restaurant ID = {restaurant.restaurant_id}")
    
    cursor.execute('''SELECT * FROM Orders WHERE restaurant_id = ?''', (restaurant.restaurant_id,))
    orders = cursor.fetchall()
    
    if not orders:
        print("No orders received.")
        cursor.execute('''SELECT COUNT(*) FROM Orders''')
        total_orders = cursor.fetchone()[0]
        print(f"Debug: Total orders in system: {total_orders}")
        conn.close()
        return
    
    print("\nReceived Orders:")
    for order in orders:
        print(f"Order ID: {order[0]}, Customer ID: {order[1]}, Item: {order[4]}, Quantity: {order[5]}, Total Price: ${order[8]}, Status: {order[9]}, Timestamp: {order[10]}")
    
    conn.close()