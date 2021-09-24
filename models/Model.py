# coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from ..config import Base

db = SQLAlchemy()



# t_c_auth_table = db.Table(
#     'c_auth_table',
#     db.Column('auth_id', db.SmallInteger),
#     db.Column('auth_name', db.String(10)),
#     db.Column('manager', db.Boolean)
# )
class CAuthTable(Base):
    __tablename__ = 'c_auth_table'
    auth_id = db.Column('auth_id', db.SmallInteger, primary_key=True, unique=True)
    auth_name = db.Column('auth_name', db.String(10))
    manager = db.Column('manager', db.Boolean)

    def __init__(self,auth_id, auth_name, manager):
      self.auth_id = auth_id
      self.auth_name = auth_name
      self.manager = manager



class CMachineTable(Base):
    __tablename__ = 'c_machine_table'
    machine_id = db.Column(db.String(50), primary_key=True, unique=True)
    machine_name = db.Column(db.String(50))
    ope_id = db.Column(db.String(50))
    machine_status = db.Column(db.String(15))

    def __init__(self,machine_id, machine_name, ope_id, machine_status):
      self.machine_id = machine_id
      self.machine_name = machine_name
      self.ope_id = ope_id
      self.machine_status = machine_status



class CMaterialTable(Base):
    __tablename__ = 'c_material_table'

    material_id = db.Column(db.String(50), primary_key=True, unique=True)
    material_name = db.Column(db.String(50))
    qty = db.Column(db.SmallInteger)
    _yield = db.Column('yield', db.SmallInteger)

    def __init__(self,material_id, material_name, qty, _yield):
      self.material_id = material_id
      self.machine_name = material_name
      self.qty = qty
      self._yield = _yield



class CMemberTable(Base):
    __tablename__ = 'c_member_table'

    account = db.Column(db.String(20), primary_key=True, unique=True)
    password = db.Column(db.String(128))
    name = db.Column(db.String(10))
    auth_id = db.Column(db.SmallInteger)
    dept = db.Column(db.String(10))
    fab = db.Column(db.String(10))
    tel = db.Column(db.String(20))
    mail = db.Column(db.String(30))
    pwd_change = db.Column(db.Boolean)

    def __init__(self,account, password, name, auth_id, dept, fab, tel, mail, pwd_change):
      self.account = account
      self.password = password
      self.name = name
      self.auth_id = auth_id
      self.dept = dept
      self.fab = fab
      self.tel = tel
      self.mail = mail
      self.pwd_change = pwd_change

# class UserSchema(Schema):
#     account = fields.String(dump_only=True, required=True, validate=validate.Length(3))
#     password = fields.String(required=True, validate=validate.Length(6))
#     name = fields.String()
#     auth_id = fields.Integer()
#     dept = fields.String()
#     fab = fields.String()
#     tel = fields.String()
#     mail = fields.String()



class CMemberlogTable(Base):
    __tablename__ = 'c_memberlog_table'

    log_id = db.Column(db.Integer, primary_key=True, unique=True)
    account = db.Column(db.ForeignKey('c_member_table.account', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    TIMESTAMP = db.Column(db.Date, nullable=False)
    note = db.Column(db.String(60))
    c_member_table = db.relationship('CMemberTable', primaryjoin='CMemberlogTable.account == CMemberTable.account', backref='c_memberlog_tables')
    def __init__(self,account, TIMESTAMP, note):
      self.account = account
      self.TIMESTAMP = TIMESTAMP
      self.note = note



class COpeTable(Base):
    __tablename__ = 'c_ope_table'

    ope_id = db.Column(db.String(50), primary_key=True, unique=True)
    ope_code = db.Column(db.String(50))
    ope_name = db.Column(db.String(50))
    layer_id = db.Column(db.String(50))



class CWipTable(Base):
    __tablename__ = 'c_wip_table'
    __table_args__ = (
        db.Index('c_wip_table_pk', 'order_id', 'lot_id'),
    )

    order_id = db.Column(db.String(50), primary_key=True, nullable=False)
    lot_id = db.Column(db.SmallInteger, primary_key=True, nullable=False)
    ope_id = db.Column(db.ForeignKey('c_ope_table.ope_id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    material_id = db.Column(db.ForeignKey('c_material_table.material_id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    wip_qty = db.Column(db.SmallInteger)
    arrival_time = db.Column(db.Date)
    leave_time = db.Column(db.Date)
    start_time = db.Column(db.Date)
    end_time = db.Column(db.Date)

    material = db.relationship('CMaterialTable', primaryjoin='CWipTable.material_id == CMaterialTable.material_id', backref='c_wip_tables')
    ope = db.relationship('COpeTable', primaryjoin='CWipTable.ope_id == COpeTable.ope_id', backref='c_wip_tables')



class RDowntimeTable(Base):
    __tablename__ = 'r_downtime_table'

    start_time = db.Column(db.String(50), primary_key=True, unique=True)
    machine_id = db.Column(db.ForeignKey('c_machine_table.machine_id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    end_time = db.Column(db.String(50))
    downtime_type = db.Column(db.String(15))

    machine = db.relationship('CMachineTable', primaryjoin='RDowntimeTable.machine_id == CMachineTable.machine_id', backref='r_downtime_tables')



class RScheduleTable(Base):
    __tablename__ = 'r_schedule_table'
    __table_args__ = (
        db.ForeignKeyConstraint(['order_id', 'lot_id'], ['c_wip_table.order_id', 'c_wip_table.lot_id'], ondelete='RESTRICT', onupdate='RESTRICT'),
        db.Index('reference_2_fk', 'order_id', 'lot_id')
    )

    schedule_id = db.Column(db.String(50), primary_key=True, unique=True)
    machine_id = db.Column(db.ForeignKey('c_machine_table.machine_id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    order_id = db.Column(db.String(50), nullable=False)
    lot_id = db.Column(db.SmallInteger, nullable=False)
    start_time = db.Column(db.Date, nullable=False)
    end_time = db.Column(db.Date)
    qty = db.Column(db.SmallInteger)

    machine = db.relationship('CMachineTable', primaryjoin='RScheduleTable.machine_id == CMachineTable.machine_id', backref='r_schedule_tables')
    order = db.relationship('CWipTable', primaryjoin='and_(RScheduleTable.order_id == CWipTable.order_id, RScheduleTable.lot_id == CWipTable.lot_id)', backref='r_schedule_tables')

class RevokedTokenModel(Base):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))

    def __init__(self,jti):
      self.jti = jti