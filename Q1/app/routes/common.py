import json

DATA_FILE = "app/data.json"

# def load_data():
#     with open(DATA_FILE, 'r') as file:
#         return json.load(file)

# def save_data(data):
#     with open(DATA_FILE, 'w') as file:
#         json.dump(data, file, indent=4)

def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'logged_in': False}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

def logout_user():
    data = load_data()
    data['logged_in'] = False
    data['user_type'] = ""
    data['phone_number'] = ""
    save_data(data)
    print("Logged out successfully!")