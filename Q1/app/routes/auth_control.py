import sqlite3
import hashlib
import json
try:
    from models.customer import Customer
    from models.delivery_agent import DeliveryAgent
    from models.order import Order
    from models.restaurant import Restaurant

    from routes.customer_options import customer_options
    from routes.delivery_agent_options import delivery_agent_options
    from routes.restaurant_options import restaurant_options
    from routes.manager_options import manager_options
    from routes.common import load_data, save_data, logout_user
except ImportError:
    from app.models.customer import Customer
    from app.models.delivery_agent import DeliveryAgent
    from app.models.order import Order
    from app.models.restaurant import Restaurant

    from app.routes.customer_options import customer_options
    from app.routes.delivery_agent_options import delivery_agent_options
    from app.routes.restaurant_options import restaurant_options
    from app.routes.manager_options import manager_options
    from app.routes.common import load_data, save_data, logout_user

DATA_FILE = "data.json"

def check_logged_in():
    data = load_data()
    if data['logged_in']:
        phone_number = data['phone_number']
        user_type = data['user_type']
        if user_type == 'customer':
            for user in data['customers']:
                if user['phone_number'] == phone_number:
                    customer = Customer(**user)
                    customer_options(customer)
                    return True
        elif user_type == 'delivery_agent':
            for user in data['delivery_agents']:
                if user['phone_number'] == phone_number:
                    # Ensure all required fields are present
                    agent_data = {
                        'agent_id': user.get('agent_id'),
                        'name': user.get('name'),
                        'phone_number': user.get('phone_number'),
                        'vehicle_number': user.get('vehicle_number'),
                        'password': user.get('password', ''),  # Provide default empty string if missing
                        'status': user.get('status', 'Available')  # Provide default status if missing
                    }
                    agent = DeliveryAgent(**agent_data)
                    delivery_agent_options(agent)
                    return True
        elif user_type == 'restaurant':
            for user in data['restaurants']:
                if user['phone_number'] == phone_number:
                    restaurant = Restaurant(**user)
                    restaurant_options(restaurant)
                    return True
        elif user_type == 'manager':
            manager_options()
            return True
    return False

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(input, stored_pw):
    return hash_password(input) == stored_pw

def register_user():
    print("\nRegister as:")
    print("1. Customer")
    print("2. Delivery Agent")
    print("3. Restaurant")
    choice = input("Please select an option: ")

    data = load_data()
    # conn = sqlite3.connect('food_delivery.db')
    from db import get_db_connection
    conn = get_db_connection()

    try:
        if choice == '1':
            name = input("Enter your name: ")
            phone_number = input("Enter your phone number: ")
            address = input("Enter your address: ")
            password = input("Enter your password: ")
            
            cursor = conn.cursor()
            cursor.execute('BEGIN TRANSACTION')
            
            customer = Customer(None, name, phone_number, address, hash_password(password))
            if customer.register(conn):
                data['customers'].append(customer.__dict__)
                save_data(data)
                conn.commit()
                print("Customer registered successfully!")
            else:
                raise Exception("Failed to register customer")

        elif choice == '2':
            name = input("Enter your name: ")
            phone_number = input("Enter your phone number: ")
            vehicle_number = input("Enter your vehicle number: ")
            password = input("Enter your password: ")
            
            cursor = conn.cursor()
            cursor.execute('BEGIN TRANSACTION')
            
            agent = DeliveryAgent(None, name, phone_number, vehicle_number, hash_password(password))
            cursor.execute('''INSERT INTO Delivery_Agents (name, phone_number, vehicle_number, password, status)
                            VALUES (?, ?, ?, ?, ?)''',
                         (agent.name, agent.phone_number, agent.vehicle_number, agent.password, 'Available'))
            agent.agent_id = cursor.lastrowid
            data['delivery_agents'].append(agent.__dict__)
            save_data(data)
            conn.commit()
            print("Delivery Agent registered successfully!")

        elif choice == '3':
            name = input("Enter restaurant name: ")
            phone_number = input("Enter restaurant phone number: ")
            password = input("Enter password: ")
            
            cursor = conn.cursor()
            cursor.execute('BEGIN TRANSACTION')
            
            restaurant = Restaurant(name, phone_number, hash_password(password))
            restaurant_id = restaurant.register(conn)
            if restaurant_id:
                data['restaurants'].append(restaurant.__dict__)
                save_data(data)
                conn.commit()
                print(f"Restaurant registered successfully with ID: {restaurant_id}")
            else:
                raise Exception("Failed to register restaurant")

        else:
            print("Invalid option. Please try again.")
            
        return False

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def login_user():
    print("\nLogin as:")
    print("1. Customer")
    print("2. Delivery Agent")
    print("3. Restaurant")
    print("4. Manager")
    
    choice = input("Enter your choice: ")
    data = load_data()
    
    try:
        from db import get_db_connection
    except ImportError:
        from app.db import get_db_connection

    conn = get_db_connection()
    cursor = conn.cursor()

    if choice == '1':
        phone_number = input("Enter phone number: ")
        password = input("Enter password: ")
        
        cursor.execute('''SELECT * FROM Customers WHERE phone_number = ?''', (phone_number,))
        customer = cursor.fetchone()
        
        if customer and (check_password(password, customer[4]) or customer[4] == password):
            print("Customer logged in successfully!")
            
            try:
                from models.customer import Customer
            except ImportError:
                from app.models.customer import Customer
                
            customer_obj = Customer(
                customer_id=customer[0],
                name=customer[1], 
                phone_number=customer[2],
                address=customer[3],
                password=customer[4]
            )
            
            data['logged_in'] = True
            data['phone_number'] = phone_number
            data['user_type'] = 'customer'
            save_data(data)
            
            try:
                from routes.customer_options import customer_options
            except ImportError:
                from app.routes.customer_options import customer_options
                
            # Important: Still show menu but RETURN the customer object
            customer_options(customer_obj)
            conn.close()
            return customer_obj
            
        print("Invalid phone number or password.")

    elif choice == '2':
        phone_number = input("Enter phone number: ")
        password = input("Enter password: ")
        
        cursor.execute('''SELECT * FROM Delivery_Agents WHERE phone_number = ?''', (phone_number,))
        agent = cursor.fetchone()
        if agent and (check_password(password, agent[4]) or agent[4] == password):
            print("Delivery Agent logged in successfully!")
            
            try:
                from models.delivery_agent import DeliveryAgent
            except ImportError:
                from app.models.delivery_agent import DeliveryAgent
                
            agent_obj = DeliveryAgent(
                agent_id=agent[0],
                name=agent[1],
                phone_number=agent[2],
                vehicle_number=agent[3],
                password=agent[4]
            )
            
            data['logged_in'] = True
            data['phone_number'] = phone_number
            data['user_type'] = 'delivery_agent'
            save_data(data)
            
            try:
                from routes.delivery_agent_options import delivery_agent_options
            except ImportError:
                from app.routes.delivery_agent_options import delivery_agent_options
                
            delivery_agent_options(agent_obj)
            conn.close()
            return agent_obj
            
        print("Invalid phone number or password.")

    elif choice == '3':
        phone_number = input("Enter phone number: ")
        password = input("Enter password: ")
        
        cursor.execute('''SELECT * FROM Restaurants WHERE phone_number = ?''', (phone_number,))
        restaurant = cursor.fetchone()
        if restaurant and (check_password(password, restaurant[3]) or restaurant[3] == password):
            print("Restaurant logged in successfully!")
            
            try:
                from models.restaurant import Restaurant
            except ImportError:
                from app.models.restaurant import Restaurant
                
            restaurant_obj = Restaurant(
                name=restaurant[1],
                phone_number=restaurant[2],
                password=restaurant[3]
            )
            restaurant_obj.restaurant_id = restaurant[0]
            
            data['logged_in'] = True
            data['phone_number'] = phone_number
            data['user_type'] = 'restaurant'
            save_data(data)
            
            try:
                from routes.restaurant_options import restaurant_options
            except ImportError:
                from app.routes.restaurant_options import restaurant_options
                
            restaurant_options(restaurant_obj)
            conn.close()
            return restaurant_obj
            
        print("Invalid phone number or password.")

    elif choice == '4':
        username = input("Enter username: ")
        password = input("Enter password: ")
        if username == "admin" and password == "admin":
            print("Manager logged in successfully!")
            data['logged_in'] = True
            data['user_type'] = 'manager'
            save_data(data)
            
            try:
                from routes.manager_options import manager_options
            except ImportError:
                from app.routes.manager_options import manager_options
                
            manager_options()
            conn.close()
            return True
            
        print("Invalid username or password.")

    else:
        print("Invalid option. Please try again.")

    conn.close()
    return None


    print("\nLogin as:")
    print("1. Customer")
    print("2. Delivery Agent")
    print("3. Restaurant")
    print("4. Manager")
    
    choice = input("Enter your choice: ")
    data = load_data()
    
    try:
        from db import get_db_connection
    except ImportError:
        from app.db import get_db_connection

    conn = get_db_connection()
    cursor = conn.cursor()

    if choice == '1':
        phone_number = input("Enter phone number: ")
        password = input("Enter password: ")
        
        cursor.execute('''SELECT * FROM Customers WHERE phone_number = ?''', (phone_number,))
        customer = cursor.fetchone()
        # print(f"DEBUG: Found customer: {customer}")
        if customer and customer[4] == hash_password(password):
            print("Customer logged in successfully!")
            customer_obj = Customer(
                customer_id=customer[0],
                name=customer[1],
                phone_number=customer[2],
                address=customer[3],
                password=customer[4]
            )
            data['logged_in'] = True
            data['phone_number'] = phone_number
            data['user_type'] = 'customer'
            save_data(data)
            return customer_obj
        else:
            print("Invalid phone number or password.")

    elif choice == '2':
        phone_number = input("Enter phone number: ")
        password = input("Enter password: ")
        
        cursor.execute('''SELECT * FROM Delivery_Agents WHERE phone_number = ?''', (phone_number,))
        agent = cursor.fetchone()
        if agent and agent[4] == hash_password(password):
            print("Delivery Agent logged in successfully!")
            agent_obj = DeliveryAgent(
                agent_id=agent[0],
                name=agent[1],
                phone_number=agent[2],
                vehicle_number=agent[3],
                password=agent[4]
            )
            data['logged_in'] = True
            data['phone_number'] = phone_number
            data['user_type'] = 'agent'
            save_data(data)
            return agent_obj
        print("Invalid phone number or password.")

    elif choice == '3':
        phone_number = input("Enter phone number: ")
        password = input("Enter password: ")
        
        cursor.execute('''SELECT * FROM Restaurants WHERE phone_number = ?''', (phone_number,))
        restaurant = cursor.fetchone()
        if restaurant and restaurant[3] == hash_password(password):
            print("Restaurant logged in successfully!")
            restaurant_obj = Restaurant(
                name=restaurant[1],
                phone_number=restaurant[2],
                password=restaurant[3]
            )
            restaurant_obj.restaurant_id = restaurant[0]
            data['logged_in'] = True
            data['phone_number'] = phone_number
            data['user_type'] = 'restaurant'
            save_data(data)
            return restaurant_obj
        print("Invalid phone number or password.")

    elif choice == '4':
        username = input("Enter username: ")
        password = input("Enter password: ")
        if username == "admin" and password == "admin":
            print("Manager logged in successfully!")
            data['logged_in'] = True
            data['user_type'] = 'manager'
            save_data(data)
            return True
        print("Invalid username or password.")

    else:
        print("Invalid option. Please try again.")

    conn.close()
    return None