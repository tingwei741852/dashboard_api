from flask import request, session, Blueprint,jsonify
from ..models.Model import CMemberTable
from ..config import db,bcrypt
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required

# 初始化biueprint
auth = Blueprint('auth', __name__)

# 註冊api
@auth.route('/sign_up', methods=['POST'])
def sign_up():
  # 取得request資料
    received_json_data = request.get_json()
  #定義每個資料若為none的默認值，但account&password不可為none 
    account = received_json_data.get('ACCOUNT')
    password = "000000"
    name = received_json_data.get('NAME', '')
    auth_id = received_json_data.get('AUTH', 1)
    dept = received_json_data.get('DEPT', '')
    fab = received_json_data.get('FAB', '')
    tel = received_json_data.get('TEL', '')
    mail = received_json_data.get('MAIL', '')
    # 如果account or password 為none，回傳error
    if account is None:
        return 'errors: account is None'
    #如果帳號已存在 ，回傳error
    if CMemberTable.query.filter_by(account = account).first() is not None:
        return 'errors: account already exist'
    # 密碼加密
    pwd = bcrypt.generate_password_hash(password=password).decode('utf-8')
    # 定義member類別
    user = CMemberTable(account, pwd, name, auth_id, dept, fab, tel, mail)
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
      return 'errors: account or password is None'
  #取得query user的第一筆data 
    userdata = CMemberTable.query.filter_by(account = account).first() 
  # 如果user data 為none，回傳error
    if userdata is  None:
        return 'errors: account not exist'
  # 取得密碼
    pwd = userdata.password
  #如果解密後的密碼與輸入的密碼時否一致，回傳error
    if not bcrypt.check_password_hash(pwd, password):   
        return 'errors: password error'
  # 取得token
    access_token = create_access_token(identity=account)
  # 設定session
    session['account'] = userdata.account
  #回傳token供前端使用 
    return jsonify(access_token=access_token)

# 登出api
@auth.route("/logout", methods=['DELETE'])
def sign_out():
  # 清除session
    session['account'] = None
    return 'Success'

# 取得當前使用者
@auth.route('/get_user', methods=['GET'])
@jwt_required()
def GetUser():
    output = {}
    # 取得當前token紀錄的user
    current_user_id = get_jwt_identity()
    # 取得當前session紀錄的user
    user_session = session.get('ACCOUNT')
    # 如果token 和user紀錄的session不一致，回傳error
    if not current_user_id ==  user_session:
       return 'errors: token not exist'
    # query當前user的資料
    user = CMemberTable.query.filter_by(account = current_user_id).first() 
    output['ACCOUNT'] = user.account
    output['DEPT'] = user.dept
    output['FAB'] = user.fab
    output['AUTH'] = user.auth_id
    # 回傳資料
    return output

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
      prop['MAUL'] = ele.mail
      prop['NAME'] = ele.name
      output.append(prop)
      # 回傳資料
    return jsonify(data =  output)


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
      print(getattr(userdata,col))
      setattr(userdata,col,ele.get(col))

  current_db_sessions = db.session.object_session(userdata)
  current_db_sessions.commit()
  return 'Success'

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