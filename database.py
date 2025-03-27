from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError


url = "mongodb+srv://lidasokha:lidasokha0303@cluster0.20mu9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(url, server_api=ServerApi('1'))
db = client["crime_tracker_db"]

crimes_collection = db["crimes"]
users_collection = db["user"]

def check_crime(crime_data):
    '''
    Check if all required fields are present in the crime_data dictionary.
    '''
    required_fields = ['applicant', 'date', 'description', 'files']
    if not all(field in crime_data for field in required_fields):
        print("Дані про злочин неповні.")
        return None
    return True

def check_user(user_data):
    '''
    Check if all required fields are present in the user_data dictionary.
    '''
    required_fields = ['name', 'surname', 'email', 'phone_number']
    if not all(field in user_data for field in required_fields):
        print("Дані користувача неповні.")
        return None
    return True

def add_crime(crime_data):
    '''
    Add a new crime to the database.
    '''
    if not check_crime(crime_data):
        print("Дані про злочин неповні.")
        return None
    try:
        result = crimes_collection.insert_one(crime_data)
        return str(result.inserted_id)
    except PyMongoError as e:
        print(f"Помилка: {e}")
        return None

def get_crimes(filter_query=None):
    '''
    Get crimes from the database.
    '''
    try:
        crimes = crimes_collection.find(filter_query or {})
    except PyMongoError as e:
        print(f"Помилка: {e}")
        return None
    return list(crimes)

def add_user(user_data):
    '''
    Add a new user to the database.
    '''
    required_fields = ['full_name', 'email', 'phone']
    if not all(field in user_data for field in required_fields):
        print("Дані користувача неповні. Потрібні поля:", required_fields)
        return None
    try:
        result = users_collection.insert_one(user_data)
        print(f"Користувач доданий з ID: {str(result.inserted_id)}")
        return str(result.inserted_id)
    except PyMongoError as e:
        print(f"Помилка при додаванні користувача: {e}")
        return None

def get_user(email, password):
    try:
        user = users_collection.find_one({"email": email, "password": password})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except PyMongoError as e:
        print(f"Помилка: {e}")
        return None

def get_user_by_email(email):
    '''
    Get a user
    '''
    try:
        user = users_collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except PyMongoError as e:
        print(f"Помилка: {e}")
        return None
