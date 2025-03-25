from pymongo import MongoClient

def get_database():
    '''
    ...
    '''
    CONNECTION_STRING = "mongodb+srv://lidasokha:lidasokha0303@cluster0.20mu9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(CONNECTION_STRING)
    return client['crime_tracker_db']

def add_user(user_data):
    dbname = get_database()
    collection = dbname['user']
    collection.insert_one(user_data)

def get_users():
    dbname = get_database()
    collection = dbname['user']
    return collection.find()
