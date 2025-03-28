from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError


url = "mongodb+srv://lidasokha:lidasokha0303@cluster0.20mu9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(url, server_api=ServerApi('1'))
db = client["crime_tracker_db"]

crimes_collection = db["crimes"]
lawyers_collection = db["lawyer"]
applicants_collection = db["applicant"]
def_users_collection = db["default_user"]


def add_lawyer(user_data):
    '''
    Add a new user to the database.
    '''
    required_fields = ['full_name', 'email', 'phone']
    if not all(field in user_data for field in required_fields):
        print("Дані користувача неповні. Потрібні поля:", required_fields)
        return None
    try:
        result = lawyers_collection.insert_one(user_data)
        print(f"Користувач доданий з ID: {str(result.inserted_id)}")
        return str(result.inserted_id)
    except PyMongoError as e:
        print(f"Помилка при додаванні користувача: {e}")
        return None


def add_applicant(user_data):
    '''
    Add a new user to the database.
    '''
    required_fields = ['full_name', 'email', 'phone']
    if not all(field in user_data for field in required_fields):
        print("Дані користувача неповні. Потрібні поля:", required_fields)
        return None
    try:
        result = applicants_collection.insert_one(user_data)
        print(f"Користувач доданий з ID: {str(result.inserted_id)}")
        return str(result.inserted_id)
    except PyMongoError as e:
        print(f"Помилка при додаванні користувача: {e}")
        return None


def add_default_user(user_data):
    '''
    Add a new user to the database.
    '''
    required_fields = ['full_name', 'email', 'phone']
    if not all(field in user_data for field in required_fields):
        print("Дані користувача неповні. Потрібні поля:", required_fields)
        return None
    try:
        result = def_users_collection.insert_one(user_data)
        print(f"Користувач доданий з ID: {str(result.inserted_id)}")
        return str(result.inserted_id)
    except PyMongoError as e:
        print(f"Помилка при додаванні користувача: {e}")
        return None


def get_user(email, password):
    '''
    Get a user from the database.
    '''
    collections = [lawyers_collection, applicants_collection, def_users_collection]
    for collection in collections:
        user = collection.find_one({"email": email, "password": password})
        if user:
            return user
    return None

