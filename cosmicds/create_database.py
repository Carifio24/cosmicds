from pymongo import MongoClient, ASCENDING

# This is just a free database for getting this up and running
MONGO_URI = "mongodb+srv://admin:admin@cluster0.l0zoc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

DBNAME = "COSMICDS"
TEACHER_COLLNAME = "TEACHERS"
STUDENT_COLLNAME = "STUDENTS"
CLASS_COLLNAME = "CLASSES"

db = client[DBNAME]
if db is None:
    db = client.create_database(DBNAME)

collection_names = [
    STUDENT_COLLNAME,
    TEACHER_COLLNAME,
    CLASS_COLLNAME
]

for coll in collection_names:
    if db.get_collection(coll) is None:
        db.create_collection(coll)

# Set some indexes on IDs
collections_and_ids = zip(collection_names, ["student_id", "teacher_id", "class_id"])
for collection_name, id_name in collections_and_ids:
    db[collection_name].create_index([(id_name, ASCENDING)], unique=True)

def add_dummy_data():
    # For testing purposes, let's add a student and a teacher
    student_collection = db[STUDENT_COLLNAME]
    student_collection.insert_one({
        "student_id": 1,
        "first_name": "Student",
        "last_name": "One",
        "stories": [{
            "name": "hubble",
            "class": "Class 1"
        }]
    })

    teacher_collection = db[TEACHER_COLLNAME]
    teacher_collection.insert_one({
        "first_name": "Teacher",
        "last_name": "One",
        "teacher_id": 1,
        "stories": [{
            "name": "hubble",
            "class": "Class One"
        }]
    })

add_dummy_data()
