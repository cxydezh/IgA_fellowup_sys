from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, date
from app import app
from database import db
from models import User, Patient, FollowupRecord, SystemSetting

@app.route('/')
def index():
    """首页重定向到登录页"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
    except:
        pass
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
    except:
        pass
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误，或账户已被禁用', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    flash('您已成功登出', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """仪表盘/主页"""
    # 统计信息
    total_patients = Patient.query.count()
    total_records = FollowupRecord.query.count()
    recent_records = FollowupRecord.query.order_by(FollowupRecord.followup_date.desc()).limit(10).all()
    
    # 最近需要随访的患者（下次随访日期在7天内）
    today = date.today()
    upcoming_followups = FollowupRecord.query.filter(
        FollowupRecord.next_followup_date.isnot(None),
        FollowupRecord.next_followup_date >= today,
        FollowupRecord.next_followup_date <= date(today.year, today.month, today.day + 7)
    ).order_by(FollowupRecord.next_followup_date.asc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         total_patients=total_patients,
                         total_records=total_records,
                         recent_records=recent_records,
                         upcoming_followups=upcoming_followups)

@app.route('/patients')
@login_required
def patients():
    """患者列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    
    query = Patient.query
    if search:
        query = query.filter(
            db.or_(
                Patient.patient_id.like(f'%{search}%'),
                Patient.name.like(f'%{search}%'),
                Patient.phone.like(f'%{search}%')
            )
        )
    
    pagination = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('patients.html', 
                         patients=pagination.items,
                         pagination=pagination,
                         search=search)

@app.route('/patients/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """添加患者"""
    if request.method == 'POST':
        try:
            # 生成患者编号
            last_patient = Patient.query.order_by(Patient.id.desc()).first()
            if last_patient:
                last_id = int(last_patient.patient_id.split('-')[-1]) if '-' in last_patient.patient_id else 0
                patient_id = f'IGA-{str(last_id + 1).zfill(6)}'
            else:
                patient_id = 'IGA-000001'
            
            # 计算年龄
            age = None
            if request.form.get('birth_date'):
                birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date()
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            elif request.form.get('age'):
                age = int(request.form.get('age'))
            
            patient = Patient(
                patient_id=patient_id,
                name=request.form.get('name'),
                gender=request.form.get('gender'),
                birth_date=datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get('birth_date') else None,
                age=age,
                id_card=request.form.get('id_card') or None,
                phone=request.form.get('phone') or None,
                address=request.form.get('address') or None,
                diagnosis=request.form.get('diagnosis') or None,
                diagnosis_date=datetime.strptime(request.form.get('diagnosis_date'), '%Y-%m-%d').date() if request.form.get('diagnosis_date') else None,
                initial_symptoms=request.form.get('initial_symptoms') or None,
                comorbidities=request.form.get('comorbidities') or None,
                family_history=request.form.get('family_history') or None,
                created_by=current_user.id
            )
            
            db.session.add(patient)
            db.session.commit()
            flash('患者添加成功', 'success')
            return redirect(url_for('patients'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加患者失败：{str(e)}', 'error')
    
    return render_template('patient_form.html', patient=None)

@app.route('/patients/<int:patient_id>')
@login_required
def patient_detail(patient_id):
    """患者详情"""
    patient = Patient.query.get_or_404(patient_id)
    records = FollowupRecord.query.filter_by(patient_id=patient_id).order_by(FollowupRecord.followup_date.desc()).all()
    return render_template('patient_detail.html', patient=patient, records=records)

@app.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    """编辑患者"""
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            # 计算年龄
            age = None
            if request.form.get('birth_date'):
                birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date()
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            elif request.form.get('age'):
                age = int(request.form.get('age'))
            
            patient.name = request.form.get('name')
            patient.gender = request.form.get('gender')
            patient.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get('birth_date') else None
            patient.age = age
            patient.id_card = request.form.get('id_card') or None
            patient.phone = request.form.get('phone') or None
            patient.address = request.form.get('address') or None
            patient.diagnosis = request.form.get('diagnosis') or None
            patient.diagnosis_date = datetime.strptime(request.form.get('diagnosis_date'), '%Y-%m-%d').date() if request.form.get('diagnosis_date') else None
            patient.initial_symptoms = request.form.get('initial_symptoms') or None
            patient.comorbidities = request.form.get('comorbidities') or None
            patient.family_history = request.form.get('family_history') or None
            
            db.session.commit()
            flash('患者信息更新成功', 'success')
            return redirect(url_for('patient_detail', patient_id=patient_id))
        except Exception as e:
            db.session.rollback()
            flash(f'更新患者信息失败：{str(e)}', 'error')
    
    return render_template('patient_form.html', patient=patient)

@app.route('/patients/<int:patient_id>/delete', methods=['POST'])
@login_required
def delete_patient(patient_id):
    """删除患者"""
    patient = Patient.query.get_or_404(patient_id)
    try:
        db.session.delete(patient)
        db.session.commit()
        flash('患者删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除患者失败：{str(e)}', 'error')
    return redirect(url_for('patients'))

@app.route('/records')
@login_required
def records():
    """随访记录列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    patient_id = request.args.get('patient_id', type=int)
    
    query = FollowupRecord.query
    if search:
        query = query.join(Patient).filter(
            db.or_(
                Patient.patient_id.like(f'%{search}%'),
                Patient.name.like(f'%{search}%')
            )
        )
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    
    pagination = query.order_by(FollowupRecord.followup_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('records.html', 
                         records=pagination.items,
                         pagination=pagination,
                         search=search,
                         patient_id=patient_id)

@app.route('/records/add', methods=['GET', 'POST'])
@login_required
def add_record():
    """添加随访记录"""
    if request.method == 'POST':
        try:
            patient_id = int(request.form.get('patient_id'))
            patient = Patient.query.get_or_404(patient_id)
            
            # 计算BMI
            bmi = None
            weight = request.form.get('body_weight')
            height = request.form.get('height')
            if weight and height:
                try:
                    weight = float(weight)
                    height = float(height) / 100  # 转换为米
                    if height > 0:
                        bmi = weight / (height * height)
                except:
                    pass
            
            record = FollowupRecord(
                patient_id=patient_id,
                followup_date=datetime.strptime(request.form.get('followup_date'), '%Y-%m-%d').date(),
                followup_type=request.form.get('followup_type') or None,
                symptoms=request.form.get('symptoms') or None,
                blood_pressure=request.form.get('blood_pressure') or None,
                heart_rate=int(request.form.get('heart_rate')) if request.form.get('heart_rate') else None,
                body_weight=float(request.form.get('body_weight')) if request.form.get('body_weight') else None,
                height=float(request.form.get('height')) if request.form.get('height') else None,
                bmi=bmi,
                urine_protein=request.form.get('urine_protein') or None,
                urine_rbc=request.form.get('urine_rbc') or None,
                urine_protein_24h=float(request.form.get('urine_protein_24h')) if request.form.get('urine_protein_24h') else None,
                urine_protein_creatinine_ratio=float(request.form.get('urine_protein_creatinine_ratio')) if request.form.get('urine_protein_creatinine_ratio') else None,
                serum_creatinine=float(request.form.get('serum_creatinine')) if request.form.get('serum_creatinine') else None,
                egfr=float(request.form.get('egfr')) if request.form.get('egfr') else None,
                serum_albumin=float(request.form.get('serum_albumin')) if request.form.get('serum_albumin') else None,
                hemoglobin=float(request.form.get('hemoglobin')) if request.form.get('hemoglobin') else None,
                iga_level=float(request.form.get('iga_level')) if request.form.get('iga_level') else None,
                medications=request.form.get('medications') or None,
                medication_compliance=request.form.get('medication_compliance') or None,
                notes=request.form.get('notes') or None,
                next_followup_date=datetime.strptime(request.form.get('next_followup_date'), '%Y-%m-%d').date() if request.form.get('next_followup_date') else None,
                recorded_by=current_user.id
            )
            
            db.session.add(record)
            db.session.commit()
            flash('随访记录添加成功', 'success')
            return redirect(url_for('patient_detail', patient_id=patient_id))
        except Exception as e:
            db.session.rollback()
            flash(f'添加随访记录失败：{str(e)}', 'error')
    
    patient_id = request.args.get('patient_id', type=int)
    patients = Patient.query.order_by(Patient.name).all()
    return render_template('record_form.html', record=None, patients=patients, patient_id=patient_id)

@app.route('/records/<int:record_id>')
@login_required
def record_detail(record_id):
    """随访记录详情"""
    record = FollowupRecord.query.get_or_404(record_id)
    return render_template('record_detail.html', record=record)

@app.route('/records/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    """编辑随访记录"""
    record = FollowupRecord.query.get_or_404(record_id)
    
    if request.method == 'POST':
        try:
            # 计算BMI
            bmi = None
            weight = request.form.get('body_weight')
            height = request.form.get('height')
            if weight and height:
                try:
                    weight = float(weight)
                    height = float(height) / 100
                    if height > 0:
                        bmi = weight / (height * height)
                except:
                    pass
            
            record.followup_date = datetime.strptime(request.form.get('followup_date'), '%Y-%m-%d').date()
            record.followup_type = request.form.get('followup_type') or None
            record.symptoms = request.form.get('symptoms') or None
            record.blood_pressure = request.form.get('blood_pressure') or None
            record.heart_rate = int(request.form.get('heart_rate')) if request.form.get('heart_rate') else None
            record.body_weight = float(request.form.get('body_weight')) if request.form.get('body_weight') else None
            record.height = float(request.form.get('height')) if request.form.get('height') else None
            record.bmi = bmi
            record.urine_protein = request.form.get('urine_protein') or None
            record.urine_rbc = request.form.get('urine_rbc') or None
            record.urine_protein_24h = float(request.form.get('urine_protein_24h')) if request.form.get('urine_protein_24h') else None
            record.urine_protein_creatinine_ratio = float(request.form.get('urine_protein_creatinine_ratio')) if request.form.get('urine_protein_creatinine_ratio') else None
            record.serum_creatinine = float(request.form.get('serum_creatinine')) if request.form.get('serum_creatinine') else None
            record.egfr = float(request.form.get('egfr')) if request.form.get('egfr') else None
            record.serum_albumin = float(request.form.get('serum_albumin')) if request.form.get('serum_albumin') else None
            record.hemoglobin = float(request.form.get('hemoglobin')) if request.form.get('hemoglobin') else None
            record.iga_level = float(request.form.get('iga_level')) if request.form.get('iga_level') else None
            record.medications = request.form.get('medications') or None
            record.medication_compliance = request.form.get('medication_compliance') or None
            record.notes = request.form.get('notes') or None
            record.next_followup_date = datetime.strptime(request.form.get('next_followup_date'), '%Y-%m-%d').date() if request.form.get('next_followup_date') else None
            
            db.session.commit()
            flash('随访记录更新成功', 'success')
            return redirect(url_for('record_detail', record_id=record_id))
        except Exception as e:
            db.session.rollback()
            flash(f'更新随访记录失败：{str(e)}', 'error')
    
    patients = Patient.query.order_by(Patient.name).all()
    return render_template('record_form.html', record=record, patients=patients, patient_id=record.patient_id)

@app.route('/records/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_record(record_id):
    """删除随访记录"""
    record = FollowupRecord.query.get_or_404(record_id)
    patient_id = record.patient_id
    try:
        db.session.delete(record)
        db.session.commit()
        flash('随访记录删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除随访记录失败：{str(e)}', 'error')
    return redirect(url_for('patient_detail', patient_id=patient_id))

@app.route('/staff')
@login_required
def staff():
    """工作人员列表"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(
            db.or_(
                User.username.like(f'%{search}%'),
                User.real_name.like(f'%{search}%')
            )
        )
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('staff.html', 
                         staff_list=pagination.items,
                         pagination=pagination,
                         search=search)

@app.route('/staff/add', methods=['GET', 'POST'])
@login_required
def add_staff():
    """添加工作人员"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            if User.query.filter_by(username=username).first():
                flash('用户名已存在', 'error')
                return render_template('staff_form.html', staff=None)
            
            staff = User(
                username=username,
                real_name=request.form.get('real_name'),
                role=request.form.get('role', 'staff'),
                department=request.form.get('department') or None,
                phone=request.form.get('phone') or None,
                email=request.form.get('email') or None,
                is_active=True
            )
            staff.set_password(request.form.get('password', '123456'))
            
            db.session.add(staff)
            db.session.commit()
            flash('工作人员添加成功', 'success')
            return redirect(url_for('staff'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加工作人员失败：{str(e)}', 'error')
    
    return render_template('staff_form.html', staff=None)

@app.route('/staff/<int:staff_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_staff(staff_id):
    """编辑工作人员"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('dashboard'))
    
    staff = User.query.get_or_404(staff_id)
    
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            if username != staff.username and User.query.filter_by(username=username).first():
                flash('用户名已存在', 'error')
                return render_template('staff_form.html', staff=staff)
            
            staff.username = username
            staff.real_name = request.form.get('real_name')
            staff.role = request.form.get('role', 'staff')
            staff.department = request.form.get('department') or None
            staff.phone = request.form.get('phone') or None
            staff.email = request.form.get('email') or None
            staff.is_active = request.form.get('is_active') == 'on'
            
            if request.form.get('password'):
                staff.set_password(request.form.get('password'))
            
            db.session.commit()
            flash('工作人员信息更新成功', 'success')
            return redirect(url_for('staff'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新工作人员信息失败：{str(e)}', 'error')
    
    return render_template('staff_form.html', staff=staff)

@app.route('/staff/<int:staff_id>/delete', methods=['POST'])
@login_required
def delete_staff(staff_id):
    """删除工作人员"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('dashboard'))
    
    if staff_id == current_user.id:
        flash('不能删除自己的账户', 'error')
        return redirect(url_for('staff'))
    
    staff = User.query.get_or_404(staff_id)
    try:
        db.session.delete(staff)
        db.session.commit()
        flash('工作人员删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除工作人员失败：{str(e)}', 'error')
    return redirect(url_for('staff'))

@app.route('/settings')
@login_required
def settings():
    """系统设置"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('dashboard'))
    
    settings_list = SystemSetting.query.order_by(SystemSetting.key).all()
    return render_template('settings.html', settings=settings_list)

@app.route('/settings/add', methods=['POST'])
@login_required
def add_setting():
    """添加系统设置"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '没有权限'}), 403
    
    try:
        key = request.form.get('key')
        value = request.form.get('value')
        description = request.form.get('description', '')
        
        if SystemSetting.query.filter_by(key=key).first():
            return jsonify({'success': False, 'message': '设置键已存在'}), 400
        
        setting = SystemSetting(
            key=key,
            value=value,
            description=description,
            updated_by=current_user.id
        )
        
        db.session.add(setting)
        db.session.commit()
        return jsonify({'success': True, 'message': '设置添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'}), 500

@app.route('/settings/<int:setting_id>/update', methods=['POST'])
@login_required
def update_setting(setting_id):
    """更新系统设置"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '没有权限'}), 403
    
    try:
        setting = SystemSetting.query.get_or_404(setting_id)
        setting.value = request.form.get('value')
        setting.description = request.form.get('description', '')
        setting.updated_by = current_user.id
        
        db.session.commit()
        return jsonify({'success': True, 'message': '设置更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'}), 500

@app.route('/settings/<int:setting_id>/delete', methods=['POST'])
@login_required
def delete_setting(setting_id):
    """删除系统设置"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '没有权限'}), 403
    
    try:
        setting = SystemSetting.query.get_or_404(setting_id)
        db.session.delete(setting)
        db.session.commit()
        return jsonify({'success': True, 'message': '设置删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'}), 500

def init_sample_data():
    """初始化示例数据"""
    # 检查是否已有数据
    if User.query.count() > 0:
        return
    
    # 创建管理员用户
    admin = User(
        username='admin',
        real_name='系统管理员',
        role='admin',
        department='信息科',
        is_active=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # 创建医生用户
    doctor = User(
        username='doctor1',
        real_name='张医生',
        role='doctor',
        department='肾内科',
        phone='13800138001',
        email='doctor1@hospital.com',
        is_active=True
    )
    doctor.set_password('123456')
    db.session.add(doctor)
    
    # 创建护士用户
    nurse = User(
        username='nurse1',
        real_name='李护士',
        role='nurse',
        department='肾内科',
        phone='13800138002',
        is_active=True
    )
    nurse.set_password('123456')
    db.session.add(nurse)
    
    db.session.commit()
    
    # 创建示例患者
    from datetime import date, timedelta
    
    patients_data = [
        {
            'patient_id': 'IGA-000001',
            'name': '王明',
            'gender': '男',
            'birth_date': date(1980, 5, 15),
            'age': 44,
            'id_card': '110101198005150001',
            'phone': '13900139001',
            'address': '北京市朝阳区XX街道XX号',
            'diagnosis': 'IgA肾病',
            'diagnosis_date': date(2020, 3, 10),
            'initial_symptoms': '血尿、蛋白尿',
            'comorbidities': '高血压',
            'family_history': '无',
            'created_by': doctor.id
        },
        {
            'patient_id': 'IGA-000002',
            'name': '李红',
            'gender': '女',
            'birth_date': date(1990, 8, 20),
            'age': 34,
            'id_card': '110101199008200002',
            'phone': '13900139002',
            'address': '北京市海淀区XX街道XX号',
            'diagnosis': 'IgA肾病',
            'diagnosis_date': date(2021, 6, 15),
            'initial_symptoms': '蛋白尿、水肿',
            'comorbidities': '无',
            'family_history': '无',
            'created_by': doctor.id
        },
        {
            'patient_id': 'IGA-000003',
            'name': '张强',
            'gender': '男',
            'birth_date': date(1975, 12, 5),
            'age': 49,
            'id_card': '110101197512050003',
            'phone': '13900139003',
            'address': '北京市西城区XX街道XX号',
            'diagnosis': 'IgA肾病',
            'diagnosis_date': date(2019, 9, 20),
            'initial_symptoms': '血尿、蛋白尿、高血压',
            'comorbidities': '高血压、糖尿病',
            'family_history': '父亲有肾病',
            'created_by': doctor.id
        }
    ]
    
    patients = []
    for p_data in patients_data:
        patient = Patient(**p_data)
        db.session.add(patient)
        patients.append(patient)
    
    db.session.commit()
    
    # 创建示例随访记录
    records_data = [
        {
            'patient_id': patients[0].id,
            'followup_date': date.today() - timedelta(days=30),
            'followup_type': '门诊',
            'symptoms': '无明显不适',
            'blood_pressure': '130/80',
            'heart_rate': 72,
            'body_weight': 70.5,
            'height': 175,
            'bmi': 23.0,
            'urine_protein': '1+',
            'urine_rbc': '10-15/HP',
            'serum_creatinine': 95.0,
            'egfr': 85.5,
            'serum_albumin': 42.0,
            'hemoglobin': 145.0,
            'iga_level': 2.5,
            'medications': 'ACEI类药物',
            'medication_compliance': '良好',
            'notes': '病情稳定，继续当前治疗方案',
            'next_followup_date': date.today() + timedelta(days=30),
            'recorded_by': doctor.id
        },
        {
            'patient_id': patients[0].id,
            'followup_date': date.today() - timedelta(days=60),
            'followup_type': '门诊',
            'symptoms': '偶有乏力',
            'blood_pressure': '135/85',
            'heart_rate': 75,
            'body_weight': 71.0,
            'height': 175,
            'bmi': 23.2,
            'urine_protein': '1+',
            'urine_rbc': '8-12/HP',
            'serum_creatinine': 98.0,
            'egfr': 83.0,
            'serum_albumin': 41.5,
            'hemoglobin': 142.0,
            'iga_level': 2.6,
            'medications': 'ACEI类药物',
            'medication_compliance': '良好',
            'notes': '建议注意休息，定期复查',
            'next_followup_date': date.today() - timedelta(days=30),
            'recorded_by': doctor.id
        },
        {
            'patient_id': patients[1].id,
            'followup_date': date.today() - timedelta(days=15),
            'followup_type': '门诊',
            'symptoms': '无不适',
            'blood_pressure': '120/75',
            'heart_rate': 68,
            'body_weight': 58.0,
            'height': 165,
            'bmi': 21.3,
            'urine_protein': '±',
            'urine_rbc': '5-8/HP',
            'serum_creatinine': 78.0,
            'egfr': 92.0,
            'serum_albumin': 45.0,
            'hemoglobin': 128.0,
            'iga_level': 2.2,
            'medications': 'ARB类药物',
            'medication_compliance': '良好',
            'notes': '病情控制良好',
            'next_followup_date': date.today() + timedelta(days=45),
            'recorded_by': doctor.id
        },
        {
            'patient_id': patients[2].id,
            'followup_date': date.today() - timedelta(days=7),
            'followup_type': '电话',
            'symptoms': '偶有头晕',
            'blood_pressure': '140/90',
            'heart_rate': 80,
            'body_weight': 75.0,
            'height': 170,
            'bmi': 26.0,
            'urine_protein': '2+',
            'urine_rbc': '15-20/HP',
            'serum_creatinine': 110.0,
            'egfr': 72.0,
            'serum_albumin': 38.0,
            'hemoglobin': 135.0,
            'iga_level': 3.2,
            'medications': 'ACEI类药物、降压药',
            'medication_compliance': '一般',
            'notes': '血压控制不佳，建议调整用药',
            'next_followup_date': date.today() + timedelta(days=14),
            'recorded_by': doctor.id
        }
    ]
    
    for r_data in records_data:
        record = FollowupRecord(**r_data)
        db.session.add(record)
    
    db.session.commit()
    
    print('示例数据初始化完成！')

