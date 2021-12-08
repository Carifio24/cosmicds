from uuid import uuid4
from pymongo.mongo_client import MongoClient

class DatabaseHandler:

    _DBNAME = "COSMICDS"
    _STUDENT_COLLNAME = "STUDENTS"
    _CLASS_COLLNAME = "CLASSES"
    _TEACHER_COLLNAME = "TEACHERS"
    _GALAXY_ID_FIELD = "galaxy_id"
    _COLLECTION_NAMES = [
        _STUDENT_COLLNAME,
        _TEACHER_COLLNAME,
        _CLASS_COLLNAME
    ]
    _MONGO_URI = "mongodb+srv://admin:admin@cluster0.l0zoc.mongodb.net/COSMICDS?retryWrites=true&w=majority"

    def __init__(self):
        self._client = MongoClient(self._MONGO_URI)
        self._db = self._client[self._DBNAME]

    def _generate_uuid(self):
        return uuid4()

    def add_teacher(self, first_name, last_name):
        self.teacher_collection.insert_one({
            "first_name": first_name,
            "last_name": last_name,
            "teacher_id": self._generate_uuid(),
            "stories": []
        })

    def add_student(self, first_name, last_name):
        self.student_collection.insert_one({
            "first_name": first_name,
            "last_name": last_name,
            "student_id": self._generate_uuid(),
            "stories": []
        })

    def add_class(self, class_name):
        self.class_collection.insert_one({
            "class_name": class_name,
            "class_id": self._generate_uuid(),
            "data": []
        })

    def add_story_for_teacher(self, teacher_id, story_id, class_id):
        doc = self._teacher_collection.update_one(
            { "teacher_id" : teacher_id },
            { "$push" : { "stories" : { "story_id" : story_id, "class_id" : class_id } } }
        )
        if doc is None:
            raise ValueError("Teacher not found!")
        return doc

    def add_story_for_student(self, student_id, story_id, class_id):
        doc = self.student_collection.update_one(
            { "student_id" : student_id },
            { "$push" : { "stories" : { "story_id" : story_id, "class_id" : class_id } } }
        )
        if doc is None:
            raise ValueError("Student not found!")
        return doc

    ## Hubble-specific methods
    def _student_has_galaxy(self, student_id, galaxy_id):
        self.student_collection.aggregate([
            { "$match": { "student_id": student_id } },
            { "$unwind": "$stories" },
            { "$match": {"stories.name": "hubble"} },
            { "$unwind": "$stories.measurements" },
            { "$match" : { "stories.measurements.galaxy_id": galaxy_id } }
        ])

    def _add_galaxy_data_for_student(self, student_id, galaxy_data):
        self.student_collection.find_one_and_update(
            { "student_id": student_id },
            { "$push" : { "stories.$[story].measurements" : galaxy_data } },
            array_filters=[{"story.name": "hubble"}]
        )

    def _update_student_galaxy_entry(self, student_id, galaxy_id, data):
        use_for_set = { "stories.${story].measurements.$[meas].%s" % k : v for k, v in data.items() }
        self._student_collection.find_one_and_update(
            { "student_id": student_id },
            { "$set": use_for_set },
            array_filters=[{"story.name":"hubble"}, {"meas.galaxy_id" : galaxy_id }]
        )
        
    def log_hubble_measurement_for_student(self, student_id, galaxy_data):
        galaxy_id = galaxy_data.get(self._GALAXY_ID_FIELD, None)
        if galaxy_id is None:
            raise ValueError(f"The measurement needs a galaxy_id")
        
        if self._student_has_galaxy(student_id, galaxy_id):
            self._update_student_galaxy_entry(student_id, galaxy_id, galaxy_data)
        else:
            self._add_galaxy_data_for_student(student_id, galaxy_data)

    @property
    def teacher_collection(self):
        return self._db[self._TEACHER_COLLNAME]

    @property
    def student_collection(self):
        return self._db[self._STUDENT_COLLNAME]

    @property
    def class_collection(self):
        return self._db[self._CLASS_COLLNAME]

    @property
    def collection_names(self):
        return self._COLLECTION_NAMES
