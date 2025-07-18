from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session
from datetime import datetime, timedelta
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
DATABASE = 'database.db'
app.secret_key = 'supersecretkey'  # Needed for session

ADMIN_PASSWORD = 'Ahmed2025'
EMPLOYEES_FILE = 'employees.txt'
TOPICS_FILE = 'topics.txt'
INTERVIEWERS_FILE = 'interviewers.txt'

def load_list(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def save_list(filename, items):
    with open(filename, 'w', encoding='utf-8') as f:
        for item in items:
            f.write(item + '\n')

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        with conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_name TEXT,
                    client_number TEXT,
                    client_name TEXT,
                    client_age INTEGER,
                    gender TEXT,
                    governorate TEXT,
                    education TEXT,
                    marital_status TEXT,
                    has_children TEXT,
                    visa_type TEXT,
                    interest TEXT,
                    interest_level TEXT,
                    notes TEXT,
                    created_at TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS followups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_name TEXT,
                    client_number TEXT,
                    client_name TEXT,
                    status TEXT,
                    notes TEXT,
                    followup_date TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_name TEXT,
                    client_name TEXT,
                    client_phone TEXT,
                    appointment_date DATE,
                    created_at TIMESTAMP,
                    attended INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS not_contacted (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_name TEXT,
                    client_number TEXT,
                    contacted_later INTEGER DEFAULT 0,
                    created_at TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS completed_interviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_name TEXT,
                    client_name TEXT,
                    client_number TEXT,
                    client_status TEXT,
                    notes TEXT,
                    interviewer TEXT,
                    created_at TIMESTAMP
                );
            ''')
        conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ======= الصفحات =======

@app.route('/')
def home():
    conn = get_db_connection()
    not_contacted_rows = conn.execute('SELECT * FROM not_contacted ORDER BY created_at DESC LIMIT 10').fetchall()
    # إحصائيات
    total_clients = conn.execute('SELECT COUNT(*) FROM clients').fetchone()[0]
    total_appointments = conn.execute('SELECT COUNT(*) FROM completed_interviews').fetchone()[0]
    total_followups = conn.execute('SELECT COUNT(*) FROM followups').fetchone()[0]
    total_interested = conn.execute("SELECT COUNT(*) FROM clients WHERE interest='مهتم'").fetchone()[0]
    conn.close()
    return render_template('home.html', not_contacted_rows=not_contacted_rows,
                           total_clients=total_clients,
                           total_appointments=total_appointments,
                           total_followups=total_followups,
                           total_interested=total_interested)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    error = None
    existing_client_name = None
    existing_employee_name = None
    employees = load_list(EMPLOYEES_FILE)
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        # Check if client_number already exists
        existing = conn.execute('SELECT client_name, employee_name FROM clients WHERE client_number = ?', (data['client_number'],)).fetchone()
        if existing:
            error = f"رقم الهاتف مسجل بالفعل باسم موظف: {existing['employee_name']} واسم العميل: {existing['client_name']}"
            existing_client_name = existing['client_name']
            existing_employee_name = existing['employee_name']
            conn.close()
            return render_template('contact_page.html', error=error, existing_client_name=existing_client_name, existing_employee_name=existing_employee_name, form_data=data, employees=employees)
        conn.execute('''
            INSERT INTO clients (employee_name, client_number, client_name, client_age, gender, governorate, education, marital_status,
            has_children, visa_type, interest, interest_level, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            data['employee_name'], data['client_number'], data['client_name'],
            int(data['client_age']),
            data['gender'], data['governorate'], data['education'],
            data['marital_status'], data.get('has_children', ''),
            data['visa_type'], data['interest'], data.get('interest_level', ''),
            data.get('notes', ''), datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/contact')
    return render_template('contact_page.html', employees=employees)

@app.route('/view_followups', methods=['GET', 'POST'])
def view_followups():
    rows = []
    selected_employee = ''
    searched_number = ''
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM followups').fetchall()
    if request.method == 'POST':
        selected_employee = request.form.get('employee_name', '')
        searched_number = request.form.get('client_number', '')
        query = 'SELECT * FROM followups WHERE 1=1'
        params = []
        if selected_employee:
            query += ' AND employee_name = ?'
            params.append(selected_employee)
        if searched_number:
            query += ' AND client_number = ?'
            params.append(searched_number)
        if selected_employee or searched_number:
            rows = conn.execute(query, params).fetchall()
    # else: do not show any rows
    conn.close()
    return render_template('view_followups.html', rows=rows, employees=employees, selected_employee=selected_employee, searched_number=searched_number)

@app.route('/view_clients', methods=['GET', 'POST'])
def view_clients():
    rows = []
    selected_employee = ''
    searched_number = ''
    start_date = ''
    end_date = ''
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM clients').fetchall()
    if request.method == 'POST':
        selected_employee = request.form.get('employee_name', '')
        searched_number = request.form.get('client_number', '')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        query = 'SELECT * FROM clients WHERE 1=1'
        params = []
        if searched_number:
            query += ' AND client_number = ?'
            params.append(searched_number)
        if selected_employee:
            query += ' AND employee_name = ?'
            params.append(selected_employee)
        if start_date:
            query += ' AND date(created_at) >= date(?)'
            params.append(start_date)
        if end_date:
            query += ' AND date(created_at) <= date(?)'
            params.append(end_date)
        if searched_number or selected_employee or start_date or end_date:
            rows = conn.execute(query, params).fetchall()
    # else: do not show any rows
    conn.close()
    return render_template('view_clients.html', rows=rows, employees=employees, selected_employee=selected_employee, searched_number=searched_number, start_date=start_date, end_date=end_date)

@app.route('/view_appointments', methods=['GET', 'POST'])
def view_appointments():
    rows = []
    selected_employee = ''
    start_date = ''
    end_date = ''
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM appointments').fetchall()
    if request.method == 'POST':
        selected_employee = request.form.get('employee_name', '')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        query = 'SELECT * FROM appointments WHERE 1=1'
        params = []
        if selected_employee:
            query += ' AND employee_name = ?'
            params.append(selected_employee)
        if start_date:
            query += ' AND date(appointment_date) >= date(?)'
            params.append(start_date)
        if end_date:
            query += ' AND date(appointment_date) <= date(?)'
            params.append(end_date)
        # Only show results if at least one filter is provided
        if selected_employee or start_date or end_date:
            rows = conn.execute(query, params).fetchall()
    # else: do not show any rows
    conn.close()
    return render_template('view_appointments.html', rows=rows, employees=employees, selected_employee=selected_employee, start_date=start_date, end_date=end_date)

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    employees = load_list(EMPLOYEES_FILE)
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO appointments (employee_name, client_name, client_phone, appointment_date, created_at)
            VALUES (?, ?, ?, ?, ?)''', (
            data['employee_name'], data['client_name'], data['client_phone'], data['appointment_date'], datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/appointment')
    return render_template('appointment_page.html', employees=employees)

@app.route('/followup', methods=['GET', 'POST'])
def followup():
    employees = load_list(EMPLOYEES_FILE)
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO followups (employee_name, client_number, client_name, status, notes, followup_date)
            VALUES (?, ?, ?, ?, ?, ?)''', (
            data['employee_name'], data['client_number'], data['client_name'], data['status'], data.get('notes', ''), datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/followup')
    return render_template('followup_page.html', employees=employees)

@app.route('/employee_stats_login', methods=['GET', 'POST'])
def employee_stats_login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['employee_stats_authenticated'] = True
            return redirect(url_for('employee_stats'))
        else:
            error = 'كلمة المرور غير صحيحة'
    return render_template('employee_stats_login.html', error=error)

@app.route('/employee_stats', methods=['GET', 'POST'])
def employee_stats():
    if not session.get('employee_stats_authenticated'):
        return redirect(url_for('employee_stats_login'))
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM clients').fetchall()
    stats = None
    selected_employee = ''
    start_date = ''
    end_date = ''
    if request.method == 'POST':
        clear_employee = request.form.get('clear_employee')
        selected_employee = request.form.get('employee_name')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        if clear_employee:
            selected_employee = None
        query = 'SELECT * FROM clients WHERE 1=1'
        params = []
        if selected_employee is not None and selected_employee != '':
            query += ' AND employee_name = ?'
            params.append(selected_employee)
        if start_date:
            query += ' AND date(created_at) >= date(?)'
            params.append(start_date)
        if end_date:
            query += ' AND date(created_at) <= date(?)'
            params.append(end_date)
        rows = conn.execute(query, params).fetchall()
        total = len(rows)
        interested = len([r for r in rows if r['interest'] == 'مهتم'])
        not_interested = len([r for r in rows if r['interest'] == 'غير مهتم'])
        followup_query = 'SELECT COUNT(*) FROM followups WHERE 1=1'
        followup_params = []
        if selected_employee is not None and selected_employee != '':
            followup_query += ' AND employee_name = ?'
            followup_params.append(selected_employee)
        if start_date:
            followup_query += ' AND date(followup_date) >= date(?)'
            followup_params.append(start_date)
        if end_date:
            followup_query += ' AND date(followup_date) <= date(?)'
            followup_params.append(end_date)
        followup_count = conn.execute(followup_query, followup_params).fetchone()[0]
        not_contacted_query = 'SELECT COUNT(*) FROM not_contacted WHERE 1=1'
        not_contacted_params = []
        if selected_employee is not None and selected_employee != '':
            not_contacted_query += ' AND employee_name = ?'
            not_contacted_params.append(selected_employee)
        if start_date:
            not_contacted_query += ' AND date(created_at) >= date(?)'
            not_contacted_params.append(start_date)
        if end_date:
            not_contacted_query += ' AND date(created_at) <= date(?)'
            not_contacted_params.append(end_date)
        not_contacted_count = conn.execute(not_contacted_query, not_contacted_params).fetchone()[0]
        # Completed interviews count by status
        completed_base = 'SELECT COUNT(*) FROM completed_interviews WHERE 1=1'
        completed_params = []
        if selected_employee is not None and selected_employee != '':
            completed_base += ' AND employee_name = ?'
            completed_params.append(selected_employee)
        if start_date:
            completed_base += ' AND date(created_at) >= date(?)'
            completed_params.append(start_date)
        if end_date:
            completed_base += ' AND date(created_at) <= date(?)'
            completed_params.append(end_date)
        # Ensure table exists
        conn.execute('''CREATE TABLE IF NOT EXISTS completed_interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT,
            client_name TEXT,
            client_number TEXT,
            client_status TEXT,
            notes TEXT,
            interviewer TEXT,
            created_at TIMESTAMP
        )''')
        # Count استشارة
        count_estishara = conn.execute(completed_base + ' AND client_status = ?', completed_params + ['استشارة']).fetchone()[0]
        # Count تم التعاقد
        count_tam_ta3aqod = conn.execute(completed_base + ' AND client_status = ?', completed_params + ['تم التعاقد']).fetchone()[0]
        completed_count = count_estishara + count_tam_ta3aqod
        stats = {
            'total': total,
            'interested': interested,
            'not_interested': not_interested,
            'followups': followup_count,
            'not_contacted': not_contacted_count,
            'completed_interviews': completed_count,
            'completed_estishara': count_estishara,
            'completed_tam_ta3aqod': count_tam_ta3aqod
        }
    conn.close()
    return render_template('employee_stats.html', employees=employees, stats=stats, selected_employee=selected_employee, start_date=start_date, end_date=end_date)

@app.route('/not_contacted', methods=['GET', 'POST'])
def not_contacted():
    employees = load_list(EMPLOYEES_FILE)
    conn = get_db_connection()
    # تأكد من وجود عمود notes
    try:
        conn.execute('SELECT notes FROM not_contacted LIMIT 1')
    except Exception:
        try:
            conn.execute('ALTER TABLE not_contacted ADD COLUMN notes TEXT')
            conn.commit()
        except Exception:
            pass
    if request.method == 'POST':
        data = request.form
        conn.execute('''
            INSERT INTO not_contacted (employee_name, client_number, notes, contacted_later, created_at)
            VALUES (?, ?, ?, ?, ?)''', (
            data['employee_name'],
            data['client_number'],
            data.get('notes', ''),
            data.get('contacted_later', 0),
            datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/not_contacted')
    conn.close()
    return render_template('not_contacted.html', employees=employees)

@app.route('/view_not_contacted', methods=['GET', 'POST'])
def view_not_contacted():
    rows = []
    selected_employee = ''
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM not_contacted').fetchall()
    if request.method == 'POST':
        # حذف عميل
        if 'delete_id' in request.form:
            delete_id = request.form.get('delete_id')
            if delete_id:
                conn.execute('DELETE FROM not_contacted WHERE id = ?', (delete_id,))
                conn.commit()
        selected_employee = request.form.get('employee_name', '')
        query = 'SELECT * FROM not_contacted WHERE 1=1'
        params = []
        if selected_employee:
            query += ' AND employee_name = ?'
            params.append(selected_employee)
        rows = conn.execute(query, params).fetchall()
    else:
        # عرض كل العملاء افتراضياً
        rows = conn.execute('SELECT * FROM not_contacted ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('view_not_contacted.html', rows=rows, employees=employees, selected_employee=selected_employee)

@app.route('/completed_interview', methods=['GET', 'POST'])
def completed_interview():
    employee_names = load_list(EMPLOYEES_FILE)
    interviewers = load_list(INTERVIEWERS_FILE)
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS completed_interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_name TEXT,
                client_name TEXT,
                client_number TEXT,
                client_status TEXT,
                notes TEXT,
                interviewer TEXT,
                created_at TIMESTAMP
            )''')
        conn.execute('''
            INSERT INTO completed_interviews (employee_name, client_name, client_number, client_status, notes, interviewer, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', (
            data['employee_name'],
            data['client_name'],
            data['client_number'],
            data['client_status'],
            data.get('notes', ''),
            data['interviewer'],
            datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/completed_interview')
    return render_template('completed_interview.html', employee_names=employee_names, interviewers=interviewers)

@app.route('/complete_interview/<int:appointment_id>', methods=['GET', 'POST'])
def complete_interview(appointment_id):
    conn = get_db_connection()
    appointment = conn.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,)).fetchone()
    interviewers = load_list(INTERVIEWERS_FILE)
    if request.method == 'POST':
        notes = request.form.get('notes', '')
        interviewer = request.form.get('interviewer', '')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS completed_interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_name TEXT,
                client_name TEXT,
                client_number TEXT,
                notes TEXT,
                interviewer TEXT,
                created_at TIMESTAMP,
                client_status TEXT
            )''')
        conn.execute('''
            INSERT INTO completed_interviews (employee_name, client_name, client_number, notes, interviewer, created_at, client_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', (
            appointment['employee_name'],
            appointment['client_name'],
            appointment['client_phone'],
            notes,
            interviewer,
            datetime.now(),
            'تم التعاقد'
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('view_completed_interviews'))
    conn.close()
    return render_template('complete_interview.html', appointment=appointment, interviewers=interviewers)

@app.route('/view_completed_interviews', methods=['GET', 'POST'])
def view_completed_interviews():
    rows = []
    selected_employee = ''
    start_date = ''
    end_date = ''
    client_status = ''
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS completed_interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_name TEXT,
        client_name TEXT,
        client_number TEXT,
        client_status TEXT,
        notes TEXT,
        interviewer TEXT,
        created_at TIMESTAMP
    )''')
    employees = conn.execute('SELECT DISTINCT employee_name FROM completed_interviews').fetchall()
    if request.method == 'POST':
        selected_employee = request.form.get('employee_name', '')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        client_status = request.form.get('client_status', '')
        query = 'SELECT * FROM completed_interviews WHERE 1=1'
        params = []
        if selected_employee:
            query += ' AND employee_name = ?'
            params.append(selected_employee)
        if start_date:
            query += ' AND date(created_at) >= date(?)'
            params.append(start_date)
        if end_date:
            query += ' AND date(created_at) <= date(?)'
            params.append(end_date)
        if client_status:
            query += ' AND client_status = ?'
            params.append(client_status)
        rows = conn.execute(query, params).fetchall()
    else:
        # Show all by default
        rows = conn.execute('SELECT * FROM completed_interviews ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('view_completed_interviews.html', rows=rows, employees=employees, selected_employee=selected_employee, start_date=start_date, end_date=end_date, client_status=client_status)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == 'elegant2025' and password == 'elegant2025':
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            error = 'اسم المستخدم أو كلمة المرور غير صحيحة'
    return render_template('login.html', error=error)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow access to login and employee_stats_login without login
        if request.endpoint in ['login', 'employee_stats_login', 'static']:
            return f(*args, **kwargs)
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Apply login_required to all routes except login and employee_stats_login
for rule in app.url_map.iter_rules():
    if rule.endpoint not in ['login', 'employee_stats_login', 'static']:
        view_func = app.view_functions[rule.endpoint]
        app.view_functions[rule.endpoint] = login_required(view_func)

@app.context_processor
def inject_notifications():
    notifications = []
    try:
        conn = get_db_connection()
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        rows = conn.execute('SELECT employee_name, client_name, appointment_date FROM appointments WHERE date(appointment_date) = ?', (str(tomorrow),)).fetchall()
        for row in rows:
            notifications.append({
                'employee_name': row['employee_name'],
                'client_name': row['client_name'],
                'date': row['appointment_date'],
                'message': f"لديك مقابلة غداً مع العميل {row['client_name']} (الموظف: {row['employee_name']})"
            })
        conn.close()
    except Exception as e:
        pass
    return dict(notifications=notifications)

@app.route('/number_stats', methods=['GET', 'POST'])
def number_stats():
    stats = None
    client_number = ''
    if request.method == 'POST':
        client_number = request.form.get('client_number', '').strip()
        if client_number:
            conn = get_db_connection()
            # بيانات العميل
            client = conn.execute('SELECT * FROM clients WHERE client_number = ?', (client_number,)).fetchone()
            # بيانات المتابعات
            followups = conn.execute('SELECT followup_date FROM followups WHERE client_number = ?', (client_number,)).fetchall()
            followup_count = len(followups)
            followup_dates = [f['followup_date'] for f in followups]
            # هل له مقابلة مكتملة
            completed = conn.execute('SELECT 1 FROM completed_interviews WHERE client_number = ? LIMIT 1', (client_number,)).fetchone()
            stats = {
                'client_name': client['client_name'] if client else None,
                'employee_name': client['employee_name'] if client else None,
                'created_at': client['created_at'] if client else None,
                'followup_count': followup_count,
                'followup_dates': followup_dates,
                'completed_interview': bool(completed)
            }
            conn.close()
    return render_template('number_stats.html', stats=stats, client_number=client_number)

@app.route('/team_stats_login', methods=['GET', 'POST'])
def team_stats_login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['team_stats_authenticated'] = True
            return redirect(url_for('team_stats'))
        else:
            error = 'كلمة المرور غير صحيحة'
    return render_template('employee_stats_login.html', error=error)

@app.route('/team_stats', methods=['GET', 'POST'])
def team_stats():
    if not session.get('team_stats_authenticated'):
        return redirect(url_for('team_stats_login'))
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM clients WHERE employee_name IS NOT NULL AND employee_name != ""').fetchall()
    start_date = ''
    end_date = ''
    stats = None
    if request.method == 'POST':
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        stats = []
        for emp in employees:
            emp_name = emp['employee_name']
            # العملاء
            query = 'SELECT * FROM clients WHERE employee_name = ?'
            params = [emp_name]
            if start_date:
                query += ' AND date(created_at) >= date(?)'
                params.append(start_date)
            if end_date:
                query += ' AND date(created_at) <= date(?)'
                params.append(end_date)
            rows = conn.execute(query, params).fetchall()
            total = len(rows)
            # المتابعات
            followup_query = 'SELECT COUNT(*) FROM followups WHERE employee_name = ?'
            followup_params = [emp_name]
            if start_date:
                followup_query += ' AND date(followup_date) >= date(?)'
                followup_params.append(start_date)
            if end_date:
                followup_query += ' AND date(followup_date) <= date(?)'
                followup_params.append(end_date)
            followup_count = conn.execute(followup_query, followup_params).fetchone()[0]
            # لم يتم التواصل
            not_contacted_query = 'SELECT COUNT(*) FROM not_contacted WHERE employee_name = ?'
            not_contacted_params = [emp_name]
            if start_date:
                not_contacted_query += ' AND date(created_at) >= date(?)'
                not_contacted_params.append(start_date)
            if end_date:
                not_contacted_query += ' AND date(created_at) <= date(?)'
                not_contacted_params.append(end_date)
            not_contacted_count = conn.execute(not_contacted_query, not_contacted_params).fetchone()[0]
            # المقابلات المكتملة
            completed_base = 'SELECT COUNT(*) FROM completed_interviews WHERE employee_name = ?'
            completed_params = [emp_name]
            if start_date:
                completed_base += ' AND date(created_at) >= date(?)'
                completed_params.append(start_date)
            if end_date:
                completed_base += ' AND date(created_at) <= date(?)'
                completed_params.append(end_date)
            count_estishara = conn.execute(completed_base + ' AND client_status = ?', completed_params + ['استشارة']).fetchone()[0]
            count_tam_ta3aqod = conn.execute(completed_base + ' AND client_status = ?', completed_params + ['تم التعاقد']).fetchone()[0]
            completed_count = count_estishara + count_tam_ta3aqod
            stats.append({
                'employee_name': emp_name,
                'total': total,
                'followups': followup_count,
                'not_contacted': not_contacted_count,
                'completed_interviews': completed_count,
                'completed_estishara': count_estishara,
                'completed_tam_ta3aqod': count_tam_ta3aqod
            })
    conn.close()
    return render_template('team_stats.html', stats=stats, start_date=start_date, end_date=end_date)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/Admin', methods=['GET', 'POST'])
@admin_required
def admin_panel():
    employees = load_list(EMPLOYEES_FILE)
    interviewers = load_list(INTERVIEWERS_FILE)
    if request.method == 'POST':
        # إدارة الموظفين
        if 'add_employee' in request.form:
            new_emp = request.form.get('new_employee', '').strip()
            if new_emp and new_emp not in employees:
                employees.append(new_emp)
                save_list(EMPLOYEES_FILE, employees)
                flash('تمت إضافة الموظف بنجاح', 'success')
            else:
                flash('الاسم فارغ أو مكرر', 'danger')
        elif 'delete_employee' in request.form:
            emp_to_delete = request.form.get('delete_employee', '').strip()
            if emp_to_delete in employees:
                employees.remove(emp_to_delete)
                save_list(EMPLOYEES_FILE, employees)
                flash('تم حذف الموظف', 'success')
            else:
                flash('الموظف غير موجود', 'danger')
        # إدارة المحاورين
        elif 'add_interviewer' in request.form:
            new_interviewer = request.form.get('new_interviewer', '').strip()
            if new_interviewer and new_interviewer not in interviewers:
                interviewers.append(new_interviewer)
                save_list(INTERVIEWERS_FILE, interviewers)
                flash('تمت إضافة المحاور بنجاح', 'success')
            else:
                flash('اسم المحاور موجود بالفعل أو غير صالح', 'danger')
        elif 'delete_interviewer_btn' in request.form:
            del_interviewer = request.form.get('delete_interviewer', '').strip()
            if del_interviewer in interviewers:
                interviewers.remove(del_interviewer)
                save_list(INTERVIEWERS_FILE, interviewers)
                flash('تم حذف المحاور بنجاح', 'success')
            else:
                flash('اسم المحاور غير موجود', 'danger')
        return redirect(url_for('admin_panel'))
    return render_template('admin.html', employees=employees, interviewers=interviewers)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect(url_for('admin_panel'))
        else:
            error = 'كلمة المرور غير صحيحة'
    return render_template('admin_login.html', error=error)

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('admin_login'))

# ======= تشغيل التطبيق =======
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
