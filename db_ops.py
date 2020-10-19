import os
from peewee import *

db = SqliteDatabase('phonebook.db')


class Person(Model):
    name = CharField(max_length=60)
    phone = CharField(max_length=12, unique=True)

    class Meta:
        database = db


def init_db():
    if "phonebook.db" in os.listdir('.'):
        os.remove(f'{os.getcwd()}/phonebook.db')
    db.connect()
    db.create_tables([Person])
    db.close()


def connector(func):
    if "phonebook.db" not in os.listdir('.'):
        init_db()

    def wrapper(*args, **kwargs):
        db.connect()
        result = func(*args, **kwargs)
        db.close()
        return result
    return wrapper
