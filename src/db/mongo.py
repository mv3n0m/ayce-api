import pymongo
from bson import ObjectId


class MongoWrapper:
    def __init__(self, db_name, db_uri="mongodb://localhost:27017"):
        self.db_name = db_name
        self.db_uri = db_uri

        mongo = pymongo.MongoClient(self.db_uri)
        mongo.server_info()

        db = mongo[self.db_name]
        self.db = db

        create_indexes(db)

    def get(
        self,
        collection,
        db_query=None,
        projection=None,
        limit=None,
        distinct=None,
        sort_keys=None,
    ):
        if "_id" in db_query:
            db_query["_id"] = ObjectId(db_query["_id"])

        db_response = self.db[collection].find(db_query or {}, projection)
        if sort_keys:
            db_response = db_response.sort(sort_keys)
        if limit:
            db_response = db_response.limit(limit)
        if distinct:
            db_response = db_response.distinct(distinct)

        return list(db_response)

    def get_by__id(self, collection, _id, projection=None):
        return self.get(collection, {"_id": _id}, projection)[0]

    def add(self, collection, record):

        inserted_id = self.db[collection].insert_one(record).inserted_id

        return inserted_id

    def alter(
        self,
        collection,
        db_query=None,
        set_values=None,
        unset_values=None,
        inc=None,
        # array_to_update: tuple=None,
        upsert=False
    ):
        if "_id" in db_query:
            db_query["_id"] = ObjectId(db_query["_id"])

        values = {}
        if set_values:
            values["$set"] = set_values
        if unset_values:
            values["$unset"] = unset_values
        if inc:
            values["$inc"] = inc

        # look into this later
        # if array_to_update:
        #     values["$addToSet"] = {array_to_update[0]: array_to_update[1][0]}
        #     values["$setOnInsert"] = {array_to_update[0]: array_to_update[1]}

        db_response = self.db[collection].update_one(
            db_query or {}, values, upsert=upsert
        )
        return db_response.upserted_id

    def delete(self, collection, db_query):
        if "_id" in db_query:
            db_query["_id"] = ObjectId(db_query["_id"])

        self.db[collection].delete_many(db_query)


def create_indexes(db):

    for i, j in [("users", ["email"])]:
        try:
            db[i].create_index([(k, -1) for k in j], unique=True)
        except Exception as e:  # pylint: disable=broad-except
            # TODO: replace with log file
            print(f"Failed while creating index at {i} with field {j}: ", e)
