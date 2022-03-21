from uuid import uuid4 as uuid_uuid4


def random_suffix(size=6):
    return uuid_uuid4().hex[:size]
