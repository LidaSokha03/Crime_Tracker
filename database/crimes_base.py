from pymongo import MongoClient

def get_database():
    '''
    ...
    '''
    CONNECTION_STRING = "mongodb+srv://lidasokha:lidasokha0303@cluster0.20mu9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(CONNECTION_STRING)
    return client['crime_tracker_db']

def add_crime(crime_data):
    dbname = get_database()
    collection = dbname['crimes']
    collection.insert_one(crime_data)

def get_crimes():
    dbname = get_database()
    collection = dbname['crimes']
    return collection.find()
