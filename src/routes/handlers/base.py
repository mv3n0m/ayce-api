from src.settings import mdb


class Base:
    updates = {}

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_id(cls, _id):
        _user = mdb.get(cls.collection, {"_id": _id})
        if not _user:
            raise ValueError("Invalid id")
        return cls(**_user[0])

    @classmethod
    def _from_query(cls, query):
        _user = mdb.get(cls.collection, query)
        if not _user:
            raise ValueError("Invalid query")
        return cls(**_user[0])

    @classmethod
    def create(cls, kwargs):
        _id = mdb.add(cls.collection, kwargs)
        return cls(_id, **kwargs)

    def push(self, kwargs):
        mdb.alter(self.collection, {"_id": self._id}, kwargs, upsert=True)

    def update(self, kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.updates.update(kwargs)

    def flush(self):
        if self.updates:
            mdb.alter(self.collection, {"_id": self._id}, self.updates, upsert=True)

    @property
    def _pk(self):
        return str(self._id)

    # def as_dict(self):
    #     return {k: str(v) for k, v in items() if k == "_id" k: v }

    # def __del__(self):
    #     print("Destroying object")

    def __getattr__(self, name):
        return None