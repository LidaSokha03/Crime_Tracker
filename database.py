from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError
from bson import ObjectId



url = "mongodb+srv://lidasokha:lidasokha0303@cluster0.20mu9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(url, server_api=ServerApi('1'))
db = client["crime_tracker_db"]

valid_crimes_collection = db["valid_crimes"]
unvalid_crimes_collection = db['unvalid_crimes']
lawyers_collection = db["lawyer"]
applicants_collection = db["applicant"]
def_users_collection = db["default_user"]

def add_lawyer(user_data):
    '''
    Add a new user to the database.
    '''
    required_fields = ['full_name', 'email', 'phone']
    assert all(field in user_data for field in required_fields), \
        f"Дані користувача неповні. Потрібні поля:{required_fields}"
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
    assert all(field in user_data for field in required_fields), \
        f"Дані користувача неповні. Потрібні поля:{required_fields}"
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
    assert all(field in user_data for field in required_fields), \
        f"Дані користувача неповні. Потрібні поля:{required_fields}"
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
            if isinstance(user.get('_id'), ObjectId):
                user['_id'] = str(user['_id'])
            return user
    return None

def find_user_by_email(email):
    '''
    ...
    '''
    collections = [lawyers_collection, applicants_collection, def_users_collection]
    for collection in collections:
        user = collection.find_one({"email": email,})
        if user:
            if isinstance(user.get('_id'), ObjectId):
                user['_id'] = str(user['_id'])
            return user
    return None

def update_users_password(email, password):
    '''
    ...
    '''
    user = find_user_by_email(email)
    if user:
        new_password = password
        collections = [lawyers_collection, applicants_collection, def_users_collection]
        for collection in collections:
            result = collection.update_one(
                {"email": email},
                {"$set": {"password": new_password}})
            if result.modified_count > 0:
                return True
    return False

def crime_report(crime):
    required_fields = ['applicant', 'applicant_number']
    assert all(field in crime for field in required_fields), \
        print("Unluck")
    try:
        result = unvalid_crimes_collection.insert_one(crime)
        return str(result.inserted_id)
    except PyMongoError as e:
        print(f"{e}")
        return None