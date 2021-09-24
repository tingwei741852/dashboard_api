from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()
db_username = os.getenv('DBUSERNAME')
db_password = os.getenv('DBPASSWORD')
db_name = os.getenv('DBNAME')
db_host = os.getenv('DBHOST')
db_port = os.getenv('DBPORT')

engine = create_engine("postgresql://"+db_username+":"+db_password+"@"+db_host+":"+db_port+"/"+db_name+"", convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = session.query_property()

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()