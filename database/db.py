# database.py
from sqlalchemy import create_engine, MetaData
from databases import Database

DATABASE_URI = "mysql+pymysql://DMMPrice:Babai%406157201@82.29.161.123:3306/testdb"

# async database connection
database = Database(DATABASE_URI)

# SQLAlchemy metadata object
metadata = MetaData()

# SQLAlchemy engine (used for migrations or table creation)
engine = create_engine(DATABASE_URI)
