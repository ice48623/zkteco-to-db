# ZKTeco to Database

A tiny Python library for sync user and attendance records from ZkTeco fingerprint scanner to Postgres Database.

### Installation

Clone the repo
```
git clone git@github.com:ice48623/zkteco-to-db.git
```

Create configuration file in project root directory `config.ini`
```
[postgresql]
host=localhost
port=5432
database=abc
user=abc
password=abc

[zkteco]
host=1.1.1.1
port=1111
timeout=5
debug=True
```

Create virtual environment with Poetry
```
poetry init
poetry install
```

Initialize Database
```
cd zkteco-to-db
python init_db.py
```

Sync to database
```
python main.py
```


### Tech Stack
1. Python
2. Poetry
3. Peewee
4. PyZK