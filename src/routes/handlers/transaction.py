from .base import Base


class Transaction(Base):
    collection = "trans"

    @classmethod
    def from_txid(cls, txid):
        return super()._from_query({"txid": txid})

    @classmethod
    def from_reference_id(cls, ref_id):
        return super()._from_query({"reference_id": reference_id})

    @classmethod
    def from_settlement_id(cls, settlement_id):
        return super()._from_query({"txid": settlement_id})

    def update_status(self, status="pending"):
        self.push({"status": status})

    @property
    def status(self):
        return self.status

    @property
    def reference_id(self):
        return self.reference_id

    @property
    def needs_settlement(self):
        return self.status == "pending" and self.needs_settlement


