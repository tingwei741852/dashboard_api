# from models import Model
import os
from flask import Flask
from dotenv import load_dotenv
from .view.auth import auth
from .view.dashboard import dashboard
from .config import db,jwt
from datetime import timedelta
from flask_cors import CORS


# 從環境變數中取得連線資訊
load_dotenv()
db_username = os.getenv('DBUSERNAME')
db_password = os.getenv('DBPASSWORD')
db_name = os.getenv('DBNAME')
db_host = os.getenv('DBHOST')
db_port = os.getenv('DBPORT')
print(db_host)
# 初始化app
app = Flask(__name__)
# 設定jwt & session secret
ACCESS_EXPIRES = timedelta(minutes=30)
app.config['JWT_SECRET_KEY'] = os.urandom(24)
app.config['SECRET_KEY'] = os.urandom(24)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
# app.config['JWT_BLACKLIST_ENABLED'] = True
# app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
blacklist = set()
# 設定資料庫連線資訊
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://"+db_username+":"+db_password+"@"+db_host+":"+db_port+"/"+db_name+""
# 初始化資料庫 & jwt
db.init_app(app)
jwt.init_app(app)
# 註冊blueprint
app.register_blueprint(auth,url_prefix= '/auth')
app.register_blueprint(dashboard,url_prefix= '/dashboard')
# 設置CORS
CORS(app)

# run app
if __name__ == '__main__':
    app.run(debug=True)

