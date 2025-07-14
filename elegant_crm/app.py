from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from datetime import datetime
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'elegant_secret_2025'
DATABASE = 'database.db'

# ===== قاعدة البيانات =====
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
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
                    created_at TIMESTAMP
                );
            ''')
        conn.close()

def ensure_all_tables_exist():
    conn = sqlite3.connect('database.db')
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS clients (
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
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT,
            client_number TEXT,
            client_name TEXT,
            status TEXT,
            notes TEXT,
            followup_date TIMESTAMP
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT,
            client_name TEXT,
            client_phone TEXT,
            appointment_date DATE,
            created_at TIMESTAMP,
            attended INTEGER DEFAULT 0
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS not_contacted (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT,
            client_number TEXT,
            contacted_later INTEGER DEFAULT 0,
            created_at TIMESTAMP
        )''')
    conn.close()

# ======= الصفحات =======

@app.route('/')
def home():
    conn = get_db_connection()
    not_contacted_rows = conn.execute('SELECT * FROM not_contacted ORDER BY created_at DESC LIMIT 10').fetchall()
    conn.close()
    return render_template('home.html', not_contacted_rows=not_contacted_rows)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    error = None
    existing_client_name = None
    existing_employee_name = None
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
            return render_template('contact_page.html', error=error, existing_client_name=existing_client_name, existing_employee_name=existing_employee_name, form_data=data)
        conn.execute('''
            INSERT INTO clients (employee_name, client_number, client_name, client_age, gender, governorate, education, marital_status,
            has_children, visa_type, interest, interest_level, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['employee_name'], data['client_number'], data['client_name'],
            data.get('client_age', None),
            data['gender'], data['governorate'], data['education'],
            data['marital_status'], data.get('has_children', ''),
            data['visa_type'], data['interest'], data.get('interest_level', ''),
            data.get('notes', ''), datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/contact')
    return render_template('contact_page.html')


@app.route('/view_followups', methods=['GET', 'POST'])
def view_followups():
    rows = []
    selected_employee = ''
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM followups').fetchall()

    if request.method == 'POST':
        selected_employee = request.form.get('employee_name', '')
        if selected_employee:
            rows = conn.execute('SELECT * FROM followups WHERE employee_name = ?', (selected_employee,)).fetchall()
    conn.close()

    return render_template('view_followups.html', rows=rows, employees=employees, selected_employee=selected_employee)


@app.route('/view_clients', methods=['GET', 'POST'])
def view_clients():
    rows = []
    selected_employee = ''
    searched_number = ''
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM clients').fetchall()

    if request.method == 'POST':
        selected_employee = request.form.get('employee_name', '')
        searched_number = request.form.get('client_number', '')

        if searched_number:
            rows = conn.execute('SELECT * FROM clients WHERE client_number = ?', (searched_number,)).fetchall()
        elif selected_employee:
            rows = conn.execute('SELECT * FROM clients WHERE employee_name = ?', (selected_employee,)).fetchall()
    conn.close()

    return render_template('view_clients.html', rows=rows, employees=employees,
                           selected_employee=selected_employee, searched_number=searched_number)


@app.route('/view_appointments', methods=['GET', 'POST'])
def view_appointments():
    rows = []
    selected_employee = ''
    selected_date = ''

    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM appointments').fetchall()

    if request.method == 'POST':
        selected_employee = request.form.get('employee_name', '')
        selected_date = request.form.get('appointment_date', '')

        query = 'SELECT * FROM appointments WHERE 1=1'
        params = []

        if selected_employee:
            query += ' AND employee_name = ?'
            params.append(selected_employee)

        if selected_date:
            query += ' AND appointment_date = ?'
            params.append(selected_date)

        rows = conn.execute(query, params).fetchall()

    conn.close()
    return render_template('view_appointments.html', rows=rows, employees=employees,
                           selected_employee=selected_employee, selected_date=selected_date)
@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO appointments (employee_name, client_name, client_phone, appointment_date, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['employee_name'],
            data['client_name'],
            data['client_phone'],
            data['appointment_date'],
            datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/appointment')
    return render_template('appointment_page.html')
@app.route('/followup', methods=['GET', 'POST'])
def followup():
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO followups (employee_name, client_number, client_name, status, notes, followup_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['employee_name'],
            data['client_number'],
            data['client_name'],
            data['status'],
            data.get('notes', ''),
            datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/followup')
    return render_template('followup_page.html')

@app.route('/employee_stats', methods=['GET', 'POST'])
def employee_stats():
    # يطلب كلمة السر في كل مرة
    if request.method == 'POST' and request.form.get('password') == 'Ahmed2025':
        pass  # يسمح بالمتابعة
    elif request.method == 'POST' and 'password' in request.form:
        return render_template('employee_stats_login.html', error=True)
    elif request.method == 'GET' or 'password' in request.form:
        return render_template('employee_stats_login.html', error=False)
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM clients').fetchall()
    stats = None
    selected_employee = ''
    start_date = ''
    end_date = ''
    if request.method == 'POST' and 'password' not in request.form:
        selected_employee = request.form.get('employee_name', '')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        query = 'SELECT * FROM clients WHERE 1=1'
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
        rows = conn.execute(query, params).fetchall()
        total = len(rows)
        interested = len([r for r in rows if r['interest'] == 'مهتم'])
        not_interested = len([r for r in rows if r['interest'] == 'غير مهتم'])
        # إحصاء عدد المتابعات
        followup_query = 'SELECT COUNT(*) FROM followups WHERE 1=1'
        followup_params = []
        if selected_employee:
            followup_query += ' AND employee_name = ?'
            followup_params.append(selected_employee)
        if start_date:
            followup_query += ' AND date(followup_date) >= date(?)'
            followup_params.append(start_date)
        if end_date:
            followup_query += ' AND date(followup_date) <= date(?)'
            followup_params.append(end_date)
        followup_count = conn.execute(followup_query, followup_params).fetchone()[0]
        # إحصاء عدد العملاء لم يتم التواصل معهم
        not_contacted_query = 'SELECT COUNT(*) FROM not_contacted WHERE 1=1'
        not_contacted_params = []
        if selected_employee:
            not_contacted_query += ' AND employee_name = ?'
            not_contacted_params.append(selected_employee)
        if start_date:
            not_contacted_query += ' AND date(created_at) >= date(?)'
            not_contacted_params.append(start_date)
        if end_date:
            not_contacted_query += ' AND date(created_at) <= date(?)'
            not_contacted_params.append(end_date)
        not_contacted_count = conn.execute(not_contacted_query, not_contacted_params).fetchone()[0]
        stats = {'total': total, 'interested': interested, 'not_interested': not_interested, 'followups': followup_count, 'not_contacted': not_contacted_count}
    conn.close()
    return render_template('employee_stats.html', employees=employees, stats=stats, selected_employee=selected_employee, start_date=start_date, end_date=end_date)

@app.route('/not_contacted', methods=['GET', 'POST'])
def not_contacted():
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO not_contacted (employee_name, client_number, contacted_later, created_at)
            VALUES (?, ?, ?, ?)
        ''', (
            data['employee_name'],
            data['client_number'],
            data.get('contacted_later', 0),
            datetime.now()
        ))
        conn.commit()
        conn.close()
        return redirect('/not_contacted')
    return render_template('not_contacted.html')

@app.route('/view_not_contacted', methods=['GET', 'POST'])
def view_not_contacted():
    rows = []
    selected_employee = ''
    conn = get_db_connection()
    employees = conn.execute('SELECT DISTINCT employee_name FROM not_contacted').fetchall()
    if request.method == 'POST':
        selected_employee = request.form.get('employee_name', '')
        if selected_employee:
            rows = conn.execute('SELECT * FROM not_contacted WHERE employee_name = ?', (selected_employee,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM not_contacted').fetchall()
    conn.close()
    return render_template('view_not_contacted.html', rows=rows, employees=employees, selected_employee=selected_employee)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'elegant2025' and password == 'elegant2025':
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            error = True
    return render_template('employee_stats_login.html', error=error)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Protect all main routes except login and static
@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and not session.get('logged_in'):
        return redirect(url_for('login'))

# ======= تشغيل التطبيق =======
if __name__ == '__main__':
    ensure_all_tables_exist()
    # Get port from environment variable (for Render) or use 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
