import datetime
from flask import  Blueprint,jsonify
from werkzeug.exceptions import abort
from ..models.Model import RScheduleTable,CMachineTable,RDowntimeTable,CMaterialTable
from ..config import db,bcrypt
from flask_jwt_extended import jwt_required

# db2 = psycopg2.connect(database="dashboard", user="postgres", password="1qaz@WSX", host="140.114.60.61", port="11249")
# cur = db.cursor()
# 初始化biueprint
dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/arrangement', methods=['GET'])
# @jwt_required()
def get_arrangement_detail():
    output = []
    # query當前user的資料
    arrangement_detail = RScheduleTable.query.all()
    # test = RDowntimeTable.query.all()
    if arrangement_detail is None:
      return jsonify(message='errors: there is  no data exist'),400
    for ele in arrangement_detail:
        prop = {}
        prop['ORDER_ID'] = ele.order_id
        prop['LOT'] = ele.lot_id
        prop['START_TIME'] = datetime.datetime.strftime(ele.start_time, '%Y-%m-%d %H:%M')
        prop['END_TIME'] = datetime.datetime.strftime(ele.end_time, '%Y-%m-%d %H:%M')
        prop['MACHINE'] = ele.machine_id
        prop['QTY'] = ele.qty
        output.append(prop)
    # 回傳資料
    return jsonify(output)

@dashboard.route('/machine_performance', methods=['GET'])

def get_machine_performance():
  output = []
  # query當前user的資料
  machine = CMachineTable.query.all()
  if machine is None:
    return jsonify(message='errors: there is  no machine data exist'),400
  for ele in machine:
      prop = {}
      prop['MACHINE_ID'] = ele.machine_id
      sql = f'''SELECT SUM ("qty") from "r_schedule_table" WHERE "machine_id" = '{ele.machine_id}';'''
      produce_qty = db.engine.execute(sql).fetchone()
      prop['PRODUCE_QTY'] = int(produce_qty[0])

      sql = f'''SELECT SUM(extract(epoch FROM "end_time") - extract(epoch FROM "start_time")) FROM "r_schedule_table" WHERE "machine_id" = '{ele.machine_id}';'''
      worktime = db.engine.execute(sql).fetchone()

      sql = f'''SELECT SUM(extract(epoch FROM "end_time") - extract(epoch FROM "start_time")) FROM "r_downtime_table" WHERE "machine_id" = '{ele.machine_id}';'''
      downtime = db.engine.execute(sql).fetchone()
      utilization_rate = int(worktime[0])/ (86400-int(downtime[0]))
      prop['UTILIZATION_RATE'] = str(round(utilization_rate*100,2))+"%"
      activation_rate = int(worktime[0]) / 86400
      prop['ACTIVATION_RATE'] = str(round(activation_rate*100,2))+"%"

      output.append(prop)
    # 回傳資料
  return jsonify(output) 
  # return "OK"

@dashboard.route('/down_time', methods=['GET'])
def Downtime():
    output = []
    machine = RDowntimeTable.query.all()
    for mac in machine:
        this_m_dt = {}
        this_m_dt['MACHINE_ID'] = mac.machine_id
        this_m_dt['START_TIME'] = datetime.datetime.strftime(mac.start_time, '%Y-%m-%d %H:%M')
        this_m_dt['END_TIME'] = datetime.datetime.strftime(mac.end_time, '%Y-%m-%d %H:%M')
        this_m_dt['REASON'] = mac.downtime_type
        output.append(this_m_dt)
    return jsonify(output)

'''{
"CAPACITY_REQ": 1260,需求產能
"MACHINE_REQ": 15,設備需求數
"OPEN_MACTION": 12,當前開機數
"DOWN_MACTION": 1,當前停機數
"TOTAL_ UTILIZATION": "61%"稼動率
"YIELD": "72%"良率
    }
'''

@dashboard.route('/total_API', methods=['GET'])
def TotalAPI():
    #數現在有多少機台不能動
    machine = RDowntimeTable.query.all()
    down_mac = 0
    for mac in machine:
        now = datetime.datetime.now()
        if mac.start_time < now and now < mac.end_time:
            down_mac += 1
    mac_num = len(CMachineTable.query.all())
    open_mac = mac_num - down_mac

    #算良率
    meterial = CMaterialTable.query.all()
    m_sum = 0
    m_ok = 0
    for mtr in meterial:
        m_sum += mtr.qty
        m_ok += mtr.qty * mtr._yield
    y =  m_ok / m_sum * 100

#  sql = f'''SELECT SUM(extract(epoch FROM "end_time") - extract(epoch FROM "start_time")) FROM "r_schedule_table" WHERE "machine_id" = '{ele.machine_id}';'''
#       worktime = db.engine.execute(sql).fetchone()
    sql = 'SELECT SUM ("qty") from "r_schedule_table";'
    cr = int(db.engine.execute(sql).fetchone()[0])
    sql = 'SELECT COUNT (DISTINCT "machine_id") FROM "r_schedule_table";'
    mr = int(db.engine.execute(sql).fetchone()[0])
    output = {}


    sql = 'SELECT SUM(extract(epoch FROM "end_time") - extract(epoch FROM "start_time")) FROM "r_schedule_table";'
    sum_work_time = int(db.engine.execute(sql).fetchone()[0])
    sql = 'SELECT SUM(extract(epoch FROM "end_time") - extract(epoch FROM "start_time")) FROM "r_downtime_table";'
    sum_down_time = int(db.engine.execute(sql).fetchone()[0])
    tu = 100 * sum_work_time / (86400 * mr - sum_down_time)


    output['CAPACITY_REQ'] = cr
    output['MACHINE_REQ'] = mr
    output['OPEN_MACTION'] = open_mac
    output['DOWN_MACTION'] = down_mac
    output['TOTAL_UTILIZATION'] = str(round(tu,2))+"%"
    output['YIELD'] = str(round(y,2))+"%"
    return output