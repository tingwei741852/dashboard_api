from flask import request, session, Blueprint,jsonify
from ..models.Model import RDowntimeTable
from ..models.Model import CMaterialTable
from ..models.Model import CMachineTable
from ..config import db,bcrypt
import datetime
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required
import psycopg2

dashboard = Blueprint('dashboard', __name__)

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
    return jsonify(data = output)

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

    db2 = psycopg2.connect(database="dashboard", user="postgres", password="1qaz@WSX", host="140.114.60.61", port="11249")
    cur = db2.cursor()
    cur.execute('SELECT SUM ("qty") from "r_schedule_table";')
    cr = int(cur.fetchone()[0])
    cur.execute('SELECT COUNT (DISTINCT "machine_id") FROM "r_schedule_table";')
    mr = int(cur.fetchone()[0])
    output = {}

    cur.execute('SELECT SUM(extract(epoch FROM "end_time") - extract(epoch FROM "start_time")) FROM "r_schedule_table";')
    sum_work_time = int(cur.fetchone()[0])
    cur.execute('SELECT SUM(extract(epoch FROM "end_time") - extract(epoch FROM "start_time")) FROM "r_downtime_table";')
    sum_down_time = int(cur.fetchone()[0])
    tu = 100 * sum_work_time / (86400 * mr - sum_down_time)


    output['CAPACITY_REQ'] = cr
    output['MACHINE_REQ'] = mr
    output['OPEN_MACTION'] = open_mac
    output['DOWN_MACTION'] = down_mac
    output['TOTAL_UTILIZATION'] = tu
    output['YIELD'] = y
    return output
