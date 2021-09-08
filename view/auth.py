from flask import request, session, Blueprint,jsonify,abort
from ..models.Model import CMemberTable,CAuthTable,RevokedTokenModel
from ..config import db,bcrypt,jwt
from flask_jwt_extended import (create_access_token,get_jwt_identity,jwt_required,get_jwt)

# 初始化biueprint
auth = Blueprint('auth', __name__)
blacklist = set()

# 註冊api
@auth.route('/sign_up', methods=['POST'])
def sign_up():
  # 取得request資料
    received_json_data = request.get_json()
  #定義每個資料若為none的默認值，但account&password不可為none 
    account = received_json_data.get('ACCOUNT')
    password = "000000"
    pwd_change = "y"
    name = received_json_data.get('NAME', '')
    auth_id = received_json_data.get('AUTH', 1)
    dept = received_json_data.get('DEPT', '')
    fab = received_json_data.get('FAB', '')
    tel = received_json_data.get('TEL', '')
    mail = received_json_data.get('MAIL', '')
    # 如果account or password 為none，回傳error
    if account is None:
      return jsonify(msg='errors: account is None'),400
    #如果帳號已存在 ，回傳error
    if CMemberTable.query.filter_by(account = account).first() is not None:
      return jsonify(msg='errors: account already exist'),400
    # 密碼加密
    pwd = bcrypt.generate_password_hash(password=password).decode('utf-8')
    # 定義member類別
    user = CMemberTable(account, pwd, name, auth_id, dept, fab, tel, mail, pwd_change)
    # 加入註冊資料
    db.session.add(user)
    db.session.commit()
    return 'Success'

# 登入api
@auth.route('/login', methods=['POST'])
def login():
  # 取得request資料
    received_json_data = request.get_json()
    account = received_json_data.get('ACCOUNT')
    password = received_json_data.get('PASSWORD')
  #如果帳號或密碼為none ，回傳error
    if account is None or password is None:
      return jsonify(msg='errors: account or password is None'),400
  #取得query user的第一筆data 
    userdata = CMemberTable.query.filter_by(account = account).first() 
  # 如果user data 為none，回傳error
    if userdata is  None:
      return jsonify(msg='errors: account not exist'),400
  # 取得密碼
    pwd = userdata.password
  #如果解密後的密碼與輸入的密碼時否一致，回傳error
    if not bcrypt.check_password_hash(pwd, password): 
      return jsonify(msg='errors: password error'),400
  # 取得token
    access_token = create_access_token(identity=account)
    PWD_CHANGE = userdata.pwd_change
  #回傳token供前端使用 
    return jsonify(ACCESS_TOKEN=access_token , PWD_CHANGE = PWD_CHANGE)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = db.session.query(RevokedTokenModel.id).filter_by(jti=jti).scalar()
    return token is not None

# 登出api
@auth.route("/logout", methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    db.session.add(RevokedTokenModel(jti=jti))
    db.session.commit()
    return 'Success'

# 取得當前使用者
@auth.route('/get_user', methods=['GET'])
@jwt_required()
def GetUser():
    output = {}
    # 取得當前token紀錄的user
    current_user_id = get_jwt_identity()
    # query當前user的資料
    user = CMemberTable.query.filter_by(account = current_user_id).first() 
    output['ACCOUNT'] = user.account
    output['DEPT'] = user.dept
    output['FAB'] = user.fab
    output['AUTH'] = user.auth_id
    # 回傳資料 
    return output
# @auth.route('/get_block', methods=['GET'])
# @jwt.token_in_blocklist_loader
# def check_if_token_is_revoked(jwt_header, jwt_payload):
#     jti = jwt_payload["jti"]
#     token_in_redis = blacklist.get(jti)
#     return token_in_redis is not None

# 取得所有使用者
@auth.route('/get_alluser', methods=['GET'])   
# @jwt_required()
def GetAllUser():
    output = []
    # query當前user的資料
    user = CMemberTable.query.all()
    for ele in user:
      prop = {}
      prop['ACCOUNT'] = ele.account
      prop['DEPT'] = ele.dept
      prop['FAB'] = ele.fab
      prop['AUTH'] = ele.auth_id
      prop['TEL'] = ele.tel
      prop['MAIL'] = ele.mail
      prop['NAME'] = ele.name
      output.append(prop)
      # 回傳資料
    return jsonify(output)

# 取得管理者
@auth.route('/get_manager', methods=['GET'])
def GetManager():
    # query當前user的資料
    sql = f'''select * from c_member_table a inner join c_auth_table b on a.auth_id = b.auth_id where b.manager  = 't';'''
    user = db.engine.execute(sql).fetchone()
    print(user)
    prop = {}
    prop['ACCOUNT'] = user[0]
    prop['DEPT'] = user[4]
    prop['FAB'] = user[5]
    prop['AUTH'] = user[3]
    prop['TEL'] = user[6]
    prop['MAIL'] = user[7]
    prop['NAME'] = user[2]
      # 回傳資料
    return jsonify(prop)


# 修改會員資料
@auth.route("/update", methods=['PUT'])
@jwt_required()
def update():
  received_json_data = request.get_json()
  ele ={}
  ele['NAME'] = received_json_data.get('NAME')
  ele['AUTH'] = received_json_data.get('AUTH')
  ele['DEPT'] = received_json_data.get('DEPT')
  ele['FAB'] = received_json_data.get('FAB')
  ele['TEL'] = received_json_data.get('TEL')
  ele['MAIL'] = received_json_data.get('MAIL')
  update_account = received_json_data.get('ACCOUNT')
  userdata = CMemberTable.query.filter_by(account=update_account).first()
  # userdata.name = 'name2'
  for col in ele:
    if  ele.get(col) is not None:
      setattr(userdata,col,ele.get(col))

  current_db_sessions = db.session.object_session(userdata)
  current_db_sessions.commit()
  return 'Success'

# 修改密碼
@auth.route("/update_pwd", methods=['PUT'])
@jwt_required()
def update_pwd():
  received_json_data = request.get_json()
  password = received_json_data.get('PASSWORD')
  update_account = get_jwt_identity()
  userdata = CMemberTable.query.filter_by(account=update_account).first()
  if password is not None or password !="":
   # 密碼加密
    pwd = bcrypt.generate_password_hash(password=password).decode('utf-8')
    userdata.password = pwd
    userdata.pwd_change = False

    current_db_sessions = db.session.object_session(userdata)
    current_db_sessions.commit()
    return 'Success'
  else:
    return jsonify(msg='error: password is none'),400

# 重設密碼
@auth.route("/reset_pwd", methods=['PUT'])
# @jwt_required()
def reset_pwd():
  received_json_data = request.get_json()
  update_account = received_json_data.get('ACCOUNT')
  password = '000000'
  userdata = CMemberTable.query.filter_by(account=update_account).first()
  if password is not None or password !="":
   # 密碼加密
    pwd = bcrypt.generate_password_hash(password=password).decode('utf-8')
    userdata.password = pwd
    userdata.pwd_change = True

    current_db_sessions = db.session.object_session(userdata)
    current_db_sessions.commit()
    return 'Success'
  else:
    return jsonify(msg='error: password is none'),400
# 刪除使用者
@jwt_required()
@auth.route("/delete", methods=['DELETE'])
def delete():
 
 received_json_data = request.get_json()
 delete_account = received_json_data.get('ACCOUNT')
 userdata = CMemberTable.query.filter_by(account=delete_account).first()
 current_db_sessions = db.session.object_session(userdata)
 current_db_sessions.delete(userdata)
 current_db_sessions.commit()
 return 'Success'

# 取得所有權限
@auth.route('/get_auth', methods=['GET'])   
# @jwt_required()
def GetAuth():
    output = []
    # query當前user的資料
    user = CAuthTable.query.all()
    for ele in user:
      prop = {}
      prop['AUTH_ID'] = ele.auth_id
      prop['AUTH_NAME'] = ele.auth_name
      prop['MANAGER '] = ele.manager
      output.append(prop)
      # 回傳資料
    return jsonify(output)

# 取得所有部門
@auth.route('/get_dept', methods=['GET'])   
# @jwt_required()
def Getdept():
    output = []
    # query當前user的資料
    sql = f'''select DISTINCT dept from c_member_table order by dept'''
    data = db.engine.execute(sql).fetchall()
    for ele in data:
      output.append(ele.dept)
      # 回傳資料
    return jsonify(output)

# 取得所有廠區
@auth.route('/get_fab', methods=['GET'])   
# @jwt_required()
def GetFab():
    output = []
    # query當前user的資料
    sql = f'''select DISTINCT fab from c_member_table order by fab'''
    data = db.engine.execute(sql).fetchall()
    for ele in data:
      output.append(ele.fab)
      # 回傳資料
    return jsonify(output)
