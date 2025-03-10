from db import DatabaseManager

def populate_products():
    db = DatabaseManager()

    products = [
        # Groceries
        (101, "Milk", "groceries", "1 litre of milk", 1.5, 1.2, 100),
        (102, "Bread", "groceries", "Whole grain bread", 2.0, 1.8, 50),
        (103, "Eggs", "groceries", "Pack of 12 eggs", 3.0, 2.5, 200),
        (104, "Butter", "groceries", "200g of butter", 2.5, 2.0, 80),
        (105, "Cheese", "groceries", "500g of cheese", 5.0, 4.5, 60),

        # Electronics
        (201, "Smartphone", "electronics", "Latest model smartphone", 699.99, 649.99, 30),
        (202, "Laptop", "electronics", "High performance laptop", 999.99, 949.99, 20),
        (203, "Headphones", "electronics", "Noise-cancelling headphones", 199.99, 179.99, 100),
        (204, "Smartwatch", "electronics", "Smartwatch with fitness tracking", 149.99, 129.99, 50),
        (205, "Tablet", "electronics", "10-inch tablet", 299.99, 279.99, 40),

        # Well-being
        (301, "Yoga Mat", "well-being", "Non-slip yoga mat", 20.0, 18.0, 150),
        (302, "Dumbbells", "well-being", "Set of 2 dumbbells", 30.0, 27.0, 100),
        (303, "Treadmill", "well-being", "Electric treadmill", 500.0, 450.0, 10),
        (304, "Exercise Bike", "well-being", "Stationary exercise bike", 300.0, 270.0, 15),
        (305, "Resistance Bands", "well-being", "Set of 5 resistance bands", 25.0, 22.0, 200)
    ]

    for product in products:
        db.add_product(*product)

    db.close()

if __name__ == "__main__":
    populate_products()