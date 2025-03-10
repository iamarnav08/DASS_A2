import sqlite3
try:
    from routes.common import logout_user
except ImportError:
    from app.routes.common import logout_user

def delivery_agent_options(agent):
    while True:
        print("\nWelcome, {}!".format(agent.name))
        print("1. View Profile")
        print("2. View Delivery Details")
        print("3. Logout")
        choice = input("Please select an option\n")

        if choice == '1':
            view_profile(agent)
        elif choice == '2':
            view_delivery_details(agent)
        elif choice == '3':
            logout_user()
            break
        else:
            print("Invalid option. Try Again.")

def view_profile(agent):
    print("\nProfile Information:")
    print(f"Name: {agent.name}")
    print(f"Phone Number: {agent.phone_number}")
    print(f"Vehicle Number: {agent.vehicle_number}")

def view_delivery_details(agent):
    # conn = sqlite3.connect('food_delivery.db')
    try:
        from db import get_db_connection
    except ImportError:
        from app.db import get_db_connection
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Step 2: Fetch the assigned deliveries for the day
    cursor.execute('''SELECT Orders.order_id, Customers.name, Customers.address, Orders.item_name, Orders.quantity, Orders.type, Orders.remaining_time, Orders.price
                      FROM Orders
                      JOIN Customers ON Orders.customer_id = Customers.customer_id
                      WHERE Orders.delivery_agent_id = ? AND Orders.status = 'active' ''', (agent.agent_id,))
    deliveries = cursor.fetchall()
    
    if not deliveries:
        print("No deliveries assigned.")
        conn.close()
        return
    
    # Step 3: Display the delivery details
    print("\nAssigned Deliveries:")
    total_earnings = 0
    for delivery in deliveries:
        order_id, customer_name, address, item_name, quantity, order_type, remaining_time, price = delivery
        print(f"Order ID: {order_id}, Customer Name: {customer_name}, Address: {address}, Item: {item_name}, Quantity: {quantity}, Type: {order_type}, Remaining Time: {remaining_time} mins, Price: ${price:.2f}")
        total_earnings += price
    
    # Step 4: Display total earnings
    print(f"\nTotal Earnings for Today: ${total_earnings:.2f}")
    
    conn.close()