from model import psql_db, Attendance, User

if __name__ == '__main__':
    psql_db.connect()
    psql_db.create_tables([Attendance, User])
    psql_db.close()
