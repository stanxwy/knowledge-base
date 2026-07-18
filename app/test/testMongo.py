from pymongo import MongoClient

client = MongoClient("mongodb://192.168.222.8:27017")

db = client["local"]
collections = db.list_collection_names()
print(collections)

logs = db["startup_log"].find().sort("startTime", -1).limit(10)
for log in logs:
    print(f"{log['startTimeLocal']}")