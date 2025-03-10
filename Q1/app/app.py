import sqlite3
import json
import hashlib
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from db import create_tables

DB_FILE = "food_delivery.db"

def start_app():
    create_tables()
    from routes.auth_control import register_user, login_user, check_logged_in

    while not check_logged_in():
        print("\nWelcome to the FOOD DELIVERY APP!")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Please select an option\n")

        if choice == '1':
            # print("h1")
            register_user()
        elif choice == '2':
            # print("hello")
            login_user()
        elif choice == '3':
            print("Exiting the app")
            break
        else:
            print("Invalid option. Try Again.")


if __name__ == "__main__":
    start_app()

