from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db

class User(UserMixin, db.Model):
    """用户模型（工作人员）"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(100), nullable=False, comment='真实姓名')
    role = db.Column(db.String(50), nullable=False, default='staff', comment='角色：admin, doctor, nurse, staff')
    department = db.Column(db.String(100), comment='科室')
    phone = db.Column(db.String(20), comment='联系电话')
    email = db.Column(db.String(100), comment='邮箱')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Patient(db.Model):
    """患者模型"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='患者编号')
    name = db.Column(db.String(100), nullable=False, comment='姓名')
    gender = db.Column(db.String(10), nullable=False, comment='性别：男/女')
    birth_date = db.Column(db.Date, comment='出生日期')
    age = db.Column(db.Integer, comment='年龄')
    id_card = db.Column(db.String(18), comment='身份证号')
    phone = db.Column(db.String(20), comment='联系电话')
    address = db.Column(db.Text, comment='地址')
    diagnosis = db.Column(db.Text, comment='诊断')
    diagnosis_date = db.Column(db.Date, comment='确诊日期')
    initial_symptoms = db.Column(db.Text, comment='初始症状')
    comorbidities = db.Column(db.Text, comment='合并症')
    family_history = db.Column(db.Text, comment='家族史')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='创建人')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    followup_records = db.relationship('FollowupRecord', backref='patient', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Patient {self.patient_id}: {self.name}>'

class FollowupRecord(db.Model):
    """随访记录模型"""
    __tablename__ = 'followup_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True, comment='患者ID')
    followup_date = db.Column(db.Date, nullable=False, comment='随访日期')
    followup_type = db.Column(db.String(50), comment='随访类型：门诊/电话/住院')
    
    # 症状和体征
    symptoms = db.Column(db.Text, comment='症状')
    blood_pressure = db.Column(db.String(20), comment='血压')
    heart_rate = db.Column(db.Integer, comment='心率')
    body_weight = db.Column(db.Float, comment='体重(kg)')
    height = db.Column(db.Float, comment='身高(cm)')
    bmi = db.Column(db.Float, comment='BMI')
    
    # 实验室检查
    urine_protein = db.Column(db.String(50), comment='尿蛋白')
    urine_rbc = db.Column(db.String(50), comment='尿红细胞')
    urine_protein_24h = db.Column(db.Float, comment='24小时尿蛋白(g/24h)')
    urine_protein_creatinine_ratio = db.Column(db.Float, comment='尿蛋白肌酐比(mg/g)')
    serum_creatinine = db.Column(db.Float, comment='血肌酐(μmol/L)')
    egfr = db.Column(db.Float, comment='eGFR(ml/min/1.73m²)')
    serum_albumin = db.Column(db.Float, comment='血清白蛋白(g/L)')
    hemoglobin = db.Column(db.Float, comment='血红蛋白(g/L)')
    iga_level = db.Column(db.Float, comment='IgA水平')
    
    # 用药情况
    medications = db.Column(db.Text, comment='用药情况')
    medication_compliance = db.Column(db.String(50), comment='用药依从性：良好/一般/差')
    
    # 其他
    notes = db.Column(db.Text, comment='备注')
    next_followup_date = db.Column(db.Date, comment='下次随访日期')
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='记录人')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    recorder = db.relationship('User', foreign_keys=[recorded_by])
    
    def __repr__(self):
        return f'<FollowupRecord {self.id}: Patient {self.patient_id}>'

class SystemSetting(db.Model):
    """系统设置模型"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='设置键')
    value = db.Column(db.Text, comment='设置值')
    description = db.Column(db.String(255), comment='描述')
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='更新人')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    updater = db.relationship('User', foreign_keys=[updated_by])
    
    def __repr__(self):
        return f'<SystemSetting {self.key}>'

