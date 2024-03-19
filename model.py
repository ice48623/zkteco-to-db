from peewee import Model, IntegerField, DateTimeField, CharField, PostgresqlDatabase, ForeignKeyField
from config import load_config


db_config = load_config(filename='config.ini', section='postgresql')
psql_db = PostgresqlDatabase(
    database=db_config["database"],
    host=db_config["host"],
    port=db_config["port"],
    user=db_config["user"],
    password=db_config["password"]
)


class BaseModel(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = psql_db


class User(BaseModel):
    uid = IntegerField()
    name = CharField()
    privilege = CharField()
    password = CharField()
    group_id = CharField()
    user_id = IntegerField()
    card = IntegerField()

    def __str__(self):
        return f'uid: {self.uid} name: {self.name} privilege: {self.privilege}'


class Attendance(BaseModel):
    uid = IntegerField()
    user_id = ForeignKeyField(User, backref='attendance')
    timestamp = DateTimeField()
    status = CharField()
    punch = IntegerField()
    punch_type = CharField()

    def __str__(self):
        return f'uid: {self.uid} user_id: {self.user_id} timestamp: {self.timestamp}'
