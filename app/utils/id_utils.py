from uuid import uuid4


def get_uuid_int_type(no_of_chars=10):
    return str(uuid4().int)[:no_of_chars]