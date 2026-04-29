import sys
import os
import shutil
from decimal import Decimal
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from models import db, Patient, Prescription, Drug

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clinic-secret-key-2024'

# 根据是否打包调整数据库路径
if getattr(sys, 'frozen', False):
    # 打包后的exe运行时，数据库放在exe同目录
    exe_dir = os.path.dirname(sys.executable)
    db_path = os.path.join(exe_dir, 'clinic.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db.init_app(app)

# ============ 首页 ============
@app.route('/')
def index():
    # 统计数据
    patient_count = Patient.query.count()
    prescription_count = Prescription.query.count()
    drug_count = Drug.query.count()
    today_count = Prescription.query.filter(
        Prescription.date == datetime.now().date()
    ).count()
    return render_template('index.html',
                         patient_count=patient_count,
                         prescription_count=prescription_count,
                         drug_count=drug_count,
                         today_count=today_count)

# ============ 病人管理 ============
@app.route('/patients')
def patients():
    search = request.args.get('search', '')
    if search:
        patients = Patient.query.filter(
            (Patient.name.contains(search)) |
            (Patient.phone.contains(search))
        ).order_by(Patient.updated_at.desc()).all()
    else:
        patients = Patient.query.order_by(Patient.updated_at.desc()).all()
    return render_template('patients/list.html', patients=patients, search=search)

@app.route('/patients/add', methods=['GET', 'POST'])
def patient_add():
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        # 检查电话是否已存在
        if Patient.query.filter_by(phone=phone).first():
            flash('该电话号码已存在', 'danger')
            return render_template('patients/form.html', patient=None)

        patient = Patient(
            phone=phone,
            name=request.form.get('name', '').strip(),
            gender=request.form.get('gender'),
            age=request.form.get('age', type=int),
            address=request.form.get('address', '').strip(),
            allergy=request.form.get('allergy', '').strip()
        )
        db.session.add(patient)
        db.session.commit()
        flash('病人添加成功', 'success')
        return redirect(url_for('patients'))
    return render_template('patients/form.html', patient=None)

@app.route('/patients/<int:id>/edit', methods=['GET', 'POST'])
def patient_edit(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        # 检查电话是否被其他病人使用
        existing = Patient.query.filter_by(phone=phone).first()
        if existing and existing.id != id:
            flash('该电话号码已被其他病人使用', 'danger')
            return render_template('patients/form.html', patient=patient)

        patient.phone = phone
        patient.name = request.form.get('name', '').strip()
        patient.gender = request.form.get('gender')
        patient.age = request.form.get('age', type=int)
        patient.address = request.form.get('address', '').strip()
        patient.allergy = request.form.get('allergy', '').strip()
        db.session.commit()
        flash('病人信息更新成功', 'success')
        return redirect(url_for('patients'))
    return render_template('patients/form.html', patient=patient)

@app.route('/patients/<int:id>/delete', methods=['POST'])
def patient_delete(id):
    patient = Patient.query.get_or_404(id)
    # 检查是否有关联处方
    if patient.prescriptions.count() > 0:
        flash('该病人有关联处方，无法删除', 'danger')
    else:
        db.session.delete(patient)
        db.session.commit()
        flash('病人删除成功', 'success')
    return redirect(url_for('patients'))

@app.route('/patients/<int:id>')
def patient_detail(id):
    patient = Patient.query.get_or_404(id)
    prescriptions = Prescription.query.filter_by(patient_id=id).order_by(Prescription.date.desc()).all()
    return render_template('patients/detail.html', patient=patient, prescriptions=prescriptions)

# ============ 处方管理 ============
@app.route('/prescriptions')
def prescriptions():
    search = request.args.get('search', '')
    date_filter = request.args.get('date', '')

    query = Prescription.query
    if search:
        query = query.filter(
            (Prescription.patient_name.contains(search)) |
            (Prescription.patient_phone.contains(search))
        )
    if date_filter:
        query = query.filter(Prescription.date == date_filter)

    prescriptions = query.order_by(Prescription.date.desc(), Prescription.id.desc()).all()
    # 日期筛选框默认显示当天
    display_date = date_filter if date_filter else datetime.now().strftime('%Y-%m-%d')
    return render_template('prescriptions/list.html', prescriptions=prescriptions, search=search, date_filter=display_date)

@app.route('/prescriptions/add', methods=['GET', 'POST'])
def prescription_add():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        patient = Patient.query.get_or_404(patient_id)

        drug_fee = Decimal(request.form.get('drug_fee', '0') or '0')
        other_fee = Decimal(request.form.get('other_fee', '0') or '0')

        prescription = Prescription(
            patient_id=patient_id,
            patient_name=patient.name,
            patient_phone=patient.phone,
            patient_age=patient.age,
            department=request.form.get('department', '').strip(),
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date() if request.form.get('date') else datetime.now().date(),
            diagnosis=request.form.get('diagnosis', '').strip(),
            prescription=request.form.get('prescription', '').strip(),
            doctor=request.form.get('doctor', '').strip(),
            dispenser=request.form.get('dispenser', '').strip(),
            reviewer=request.form.get('reviewer', '').strip(),
            drug_fee=drug_fee,
            other_fee=other_fee,
            total_fee=drug_fee + other_fee
        )
        db.session.add(prescription)
        db.session.commit()
        flash('处方添加成功', 'success')
        return redirect(url_for('prescription_print', id=prescription.id))

    # GET请求，获取病人信息
    patient_id = request.args.get('patient_id', type=int)
    patient = Patient.query.get(patient_id) if patient_id else None
    drugs = Drug.query.filter_by(is_common=True).all()
    return render_template('prescriptions/form.html', patient=patient, drugs=drugs, prescription=None, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/prescriptions/<int:id>/void', methods=['POST'])
def prescription_void(id):
    """废弃处方"""
    prescription = Prescription.query.get_or_404(id)
    prescription.is_void = True
    db.session.commit()
    flash('处方已废弃', 'warning')
    return redirect(url_for('prescriptions'))

@app.route('/prescriptions/<int:id>/print')
def prescription_print(id):
    prescription = Prescription.query.get_or_404(id)
    return render_template('prescriptions/print.html', prescription=prescription)

# ============ 药品管理 ============
@app.route('/drugs')
def drugs():
    search = request.args.get('search', '')
    if search:
        drugs = Drug.query.filter(Drug.name.contains(search)).order_by(Drug.name).all()
    else:
        drugs = Drug.query.order_by(Drug.name).all()
    return render_template('drugs/list.html', drugs=drugs, search=search)

@app.route('/drugs/add', methods=['GET', 'POST'])
def drug_add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if Drug.query.filter_by(name=name).first():
            flash('该药品已存在', 'danger')
            return render_template('drugs/form.html', drug=None)

        drug = Drug(
            name=name,
            price=request.form.get('price', type=Decimal),
            unit=request.form.get('unit', '盒').strip(),
            is_common=request.form.get('is_common') == 'on'
        )
        db.session.add(drug)
        db.session.commit()
        flash('药品添加成功', 'success')
        return redirect(url_for('drugs'))
    return render_template('drugs/form.html', drug=None)

@app.route('/drugs/<int:id>/edit', methods=['GET', 'POST'])
def drug_edit(id):
    drug = Drug.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        existing = Drug.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash('该药品名称已被使用', 'danger')
            return render_template('drugs/form.html', drug=drug)

        drug.name = name
        drug.price = request.form.get('price', type=Decimal)
        drug.unit = request.form.get('unit', '盒').strip()
        drug.is_common = request.form.get('is_common') == 'on'
        db.session.commit()
        flash('药品更新成功', 'success')
        return redirect(url_for('drugs'))
    return render_template('drugs/form.html', drug=drug)

@app.route('/drugs/<int:id>/delete', methods=['POST'])
def drug_delete(id):
    drug = Drug.query.get_or_404(id)
    db.session.delete(drug)
    db.session.commit()
    flash('药品删除成功', 'success')
    return redirect(url_for('drugs'))

# ============ 数据备份 ============
@app.route('/backup')
def backup():
    return render_template('backup.html')

@app.route('/backup/download')
def backup_download():
    """下载数据库备份文件"""
    # 获取数据库文件路径
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        db_path = os.path.join(exe_dir, 'clinic.db')
    else:
        # Flask-SQLAlchemy 默认将数据库放在 instance 文件夹
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'clinic.db')

    if not os.path.exists(db_path):
        flash('数据库文件不存在', 'danger')
        return redirect(url_for('backup'))

    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'clinic_backup_{timestamp}.db'

    return send_file(db_path, as_attachment=True, download_name=backup_filename)

# ============ API接口 ============
@app.route('/api/patients/search')
def api_patients_search():
    """病人搜索API，用于处方选择病人"""
    q = request.args.get('q', '')
    patients = Patient.query.filter(
        (Patient.name.contains(q)) | (Patient.phone.contains(q))
    ).limit(10).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'phone': p.phone,
        'age': p.age,
        'gender': p.gender,
        'allergy': p.allergy
    } for p in patients])

@app.route('/api/drugs/list')
def api_drugs_list():
    """药品列表API"""
    drugs = Drug.query.filter_by(is_common=True).all()
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'price': float(d.price),
        'unit': d.unit
    } for d in drugs])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
