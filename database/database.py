from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

url = "mongodb+srv://lidasokha:lidasokha0303@cluster0.20mu9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(url, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
