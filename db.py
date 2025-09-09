import os
from peewee import FloatField, PostgresqlDatabase, Model, CharField, ForeignKeyField

db_url = os.getenv('DATABASE_URL')
if db_url:
    db = PostgresqlDatabase(db_url)
else:
    raise ValueError("DATABASE_URL environment variable not set")

class Visitor(Model):
    ip = CharField(unique=True)
    country = CharField(null=True)
    lat = FloatField(null=True)
    long = FloatField(null=True)
    class Meta:
        database = db

class Visit(Model):
    visitor = ForeignKeyField(Visitor, backref='visits')
    timestamp = FloatField()
    path = CharField()

    class Meta:
        database = db

db.connect()
db.create_tables([Visitor, Visit])
