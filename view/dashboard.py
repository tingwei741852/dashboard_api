import datetime
from flask import  Blueprint,jsonify
from ..models.Model import RScheduleTable,CMachineTable
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
        return 'errors: there is  no data exist'
    for ele in arrangement_detail:
        prop = {}
        prop['order_id'] = ele.order_id
        prop['lot'] = ele.lot_id
        prop['start_time'] = ele.start_time
        prop['end_time'] = ele.end_time
        prop['machine'] = ele.machine_id
        prop['qty'] = ele.qty
        output.append(prop)
    # 回傳資料
    return jsonify(data =  output)

@dashboard.route('/machine_performance', methods=['GET'])

def get_machine_performance():
  output = []
  # query當前user的資料
  machine = CMachineTable.query.all()
  if machine is None:
      return 'errors: there is  no machine data exist'
  for ele in machine:
      prop = {}
      prop['machine_id'] = ele.machine_id
      sql = f'''SELECT SUM ("qty") from "r_schedule_table" WHERE "machine_id" = '{ele.machine_id}';'''
      produce_qty = db.engine.execute(sql).fetchone()
      prop['produce_qty'] = int(produce_qty[0])

      sql = f'''SELECT SUM(extract(epoch FROM "end_time") - extract(epoch FROM "start_time")) FROM "r_schedule_table" WHERE "machine_id" = '{ele.machine_id}';'''
      worktime = db.engine.execute(sql).fetchone()

      sql = f'''SELECT SUM(extract(epoch FROM "end_time") - extract(epoch FROM "start_time")) FROM "r_downtime_table" WHERE "machine_id" = '{ele.machine_id}';'''
      downtime = db.engine.execute(sql).fetchone()
      utilization_rate = int(worktime[0])/ (86400-int(downtime[0]))
      prop['utilization_rate'] = utilization_rate
      activation_rate = int(worktime[0]) / 86400
      prop['activation_rate'] = activation_rate

      output.append(prop)
    # 回傳資料
  return jsonify(data =  output) 
  # return "OK"