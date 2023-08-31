import logging


class Store:

    def init_store(self, instance):
        self.i = instance

    def _set(self, key, value=None):
        self.i.set(key, str(value))
        logging.info(f"key set: {key}")

    def _get(self, key):
        if not self.i.exists(key):
            raise ValueError("Invalid key.")

        value = self.i.get(key)
        logging.info(f"rst fetch: {key}, value: {value}")

        return value.decode()

    def _del(self, key):
        if not self.i.exists(key):
            raise ValueError("Invalid key.")

        self.i.delete(key)
        logging.info(f"key delete: {key}")

    def _all(self):
        all_keys = self.i.keys('*')
        values = self.i.mget(all_keys)
        key_value_dict = dict(zip(all_keys, values))

        logging.info(f"all records in cache: {self._all()}")

        return key_value_dict
