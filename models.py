from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

db = SQLAlchemy()

class Patient(db.Model):
    """病人表"""
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, comment='电话(业务唯一键)')
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    gender = db.Column(db.String(10), comment='性别')
    age = db.Column(db.Integer, comment='年龄')
    address = db.Column(db.String(200), comment='住址')
    allergy = db.Column(db.Text, comment='过敏史')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    prescriptions = db.relationship('Prescription', backref='patient', lazy='dynamic')

    def __repr__(self):
        return f'<Patient {self.name}>'


class Prescription(db.Model):
    """处方表"""
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, comment='病人ID')
    patient_name = db.Column(db.String(50), nullable=False, comment='病人姓名(冗余)')
    patient_phone = db.Column(db.String(20), comment='病人电话(冗余)')
    patient_age = db.Column(db.Integer, comment='病人年龄(冗余)')
    department = db.Column(db.String(50), comment='科别')
    date = db.Column(db.Date, nullable=False, default=datetime.now().date, comment='处方日期')
    diagnosis = db.Column(db.Text, comment='诊断')
    prescription = db.Column(db.Text, comment='处方明细')
    doctor = db.Column(db.String(50), comment='医生')
    dispenser = db.Column(db.String(50), comment='配药')
    reviewer = db.Column(db.String(50), comment='复核')
    drug_fee = db.Column(db.Numeric(10, 2), default=0, comment='药费')
    other_fee = db.Column(db.Numeric(10, 2), default=0, comment='其他费用')
    total_fee = db.Column(db.Numeric(10, 2), default=0, comment='合计')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    def __repr__(self):
        return f'<Prescription {self.id}>'


class Drug(db.Model):
    """药品表"""
    __tablename__ = 'drugs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, comment='药品名称')
    price = db.Column(db.Numeric(10, 2), nullable=False, comment='价格')
    unit = db.Column(db.String(20), default='盒', comment='单位')
    is_common = db.Column(db.Boolean, default=True, comment='是否常用')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f'<Drug {self.name}>'
