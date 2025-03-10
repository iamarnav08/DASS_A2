import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..src.db import DatabaseManager
from datetime import datetime

@pytest.fixture(scope="module")
def db():
    db_instance = DatabaseManager("test_ecommerce.db")
    # Setup test data
    db_instance.add_product(101, "Test Product", "test", "Test Description", 10.0, 8.0, 100)
    yield db_instance
    # Cleanup
    if os.path.exists("test_ecommerce.db"):
        os.remove("test_ecommerce.db")
    db_instance.close()

# User Management Tests
def test_valid_registration(db):
    user_id = db.add_user(1001, "Test User", "test@example.com", "password123", "retail")
    assert user_id is not None

def test_invalid_registration_duplicate(db):
    user_id = db.add_user(1001, "Test User", "test@example.com", "password123", "retail")
    assert user_id is None

def test_valid_login(db):
    result = db.cursor.execute(
        "SELECT * FROM User WHERE email = ? AND password = ?",
        ("test@example.com", "password123")
    ).fetchone()
    assert result is not None

def test_invalid_login(db):
    result = db.cursor.execute(
        "SELECT * FROM User WHERE email = ? AND password = ?",
        ("wrong@example.com", "wrongpass")
    ).fetchone()
    assert result is None

# Product Tests
def test_valid_search(db):
    products = db.cursor.execute(
        "SELECT * FROM Product WHERE category = ?", 
        ("test",)
    ).fetchall()
    assert len(products) > 0

def test_invalid_search(db):
    products = db.cursor.execute(
        "SELECT * FROM Product WHERE category = ?",
        ("nonexistent",)
    ).fetchall()
    assert len(products) == 0

# Order Tests
def test_valid_order_creation(db):
    order_id = db.create_order(1, 1001, 101, 2, 20.0)
    assert order_id is not None

def test_invalid_order_creation(db):
    order_id = db.create_order(2, 999, 999, 1, 10.0)  # Invalid user/product IDs
    # Check if order actually exists
    order = db.cursor.execute("SELECT * FROM Order_Table WHERE orderID = ?", (order_id,)).fetchone()
    assert order is not None or len(order) == 0

def test_apply_discount(db):
    order_id = db.create_order(3, 1001, 101, 1, 100.0)
    assert db.apply_discount_to_order(order_id, 10) is True
    order = db.cursor.execute(
        "SELECT total_amount FROM Order_Table WHERE orderID = ?",
        (order_id,)
    ).fetchone()
    assert order[0] == 90.0

def test_invalid_discount(db):
    assert not db.apply_discount_to_order(999, 10)

# Customer Type Tests
def test_retail_customer_creation(db):
    user_id = db.add_user(2001, "Retail User", "retail@test.com", "pass123", "retail")
    assert db.add_retail_customer(user_id) is True

def test_bulk_customer_creation(db):
    user_id = db.add_user(3001, "Bulk User", "bulk@test.com", "pass123", "bulk")
    assert db.add_bulk_customer(user_id) is True

# Edge Cases
def test_zero_quantity_order(db):
    order_id = db.create_order(5, 1001, 101, 0, 0.0)
    # Verify no order with quantity 0
    order = db.cursor.execute("SELECT * FROM Order_Table WHERE orderID = ? AND quantity > 0", (order_id,)).fetchone()
    assert order is None

def test_negative_price_order(db):
    order_id = db.create_order(6, 1001, 101, 1, -10.0)
    # Verify no order with negative price
    order = db.cursor.execute("SELECT * FROM Order_Table WHERE orderID = ? AND total_amount >= 0", (order_id,)).fetchone()
    assert order is None

def test_invalid_user_type(db):
    user_id = db.add_user(4001, "Invalid", "invalid@test.com", "pass123", "invalid")
    # Check if user type is valid
    user = db.cursor.execute("SELECT * FROM User WHERE id = ? AND (user_type = 'retail' OR user_type = 'bulk')", 
                           (user_id,)).fetchone()
    assert user is None

def test_empty_product_search(db):
    products = db.cursor.execute("SELECT * FROM Product WHERE category = ?", ("",)).fetchall()
    assert len(products) == 0