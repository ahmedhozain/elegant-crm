from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session
from datetime import datetime, timedelta
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
DATABASE = 'database.db'
app.secret_key = 'supersecretkey'  # Needed for session

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
    return render_template('contact_page.html')

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
    return render_template('appointment_page.html')

@app.route('/followup', methods=['GET', 'POST'])
def followup():
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
    return render_template('followup_page.html')

@app.route('/employee_stats_login', methods=['GET', 'POST'])
def employee_stats_login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == 'Ahmed2025':
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
        # Completed interviews count
        completed_query = 'SELECT COUNT(*) FROM completed_interviews WHERE 1=1'
        completed_params = []
        if selected_employee:
            completed_query += ' AND employee_name = ?'
            completed_params.append(selected_employee)
        if start_date:
            completed_query += ' AND date(created_at) >= date(?)'
            completed_params.append(start_date)
        if end_date:
            completed_query += ' AND date(created_at) <= date(?)'
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
        completed_count = conn.execute(completed_query, completed_params).fetchone()[0]
        stats = {'total': total, 'interested': interested, 'not_interested': not_interested, 'followups': followup_count, 'not_contacted': not_contacted_count, 'completed_interviews': completed_count}
    conn.close()
    return render_template('employee_stats.html', employees=employees, stats=stats, selected_employee=selected_employee, start_date=start_date, end_date=end_date)

@app.route('/not_contacted', methods=['GET', 'POST'])
def not_contacted():
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO not_contacted (employee_name, client_number, contacted_later, created_at)
            VALUES (?, ?, ?, ?)''', (
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
        query = 'SELECT * FROM not_contacted WHERE 1=1'
        params = []
        if selected_employee:
            query += ' AND employee_name = ?'
            params.append(selected_employee)
        if selected_employee:
            rows = conn.execute(query, params).fetchall()
    # else: do not show any rows
    conn.close()
    return render_template('view_not_contacted.html', rows=rows, employees=employees, selected_employee=selected_employee)

@app.route('/completed_interview', methods=['GET', 'POST'])
def completed_interview():
    employee_names = [
        "احمد محمد", "احمد البسيوني", "محمد ياسر", "محمد فارس", "يوسف عصمت", "استاذ محمد", "رحمه", "شروق", "منه عادل", "فاطمه", "رضوي", "امنيه محمد", "ايه عبد العال", "ايمان حسن", "يؤنا", "الاء", "محمود عماد", "محمود هشام", "تبارك", "ملك بهاء", "شيماء عزت", "نورهان ونس", "نانسي منير", "ندي مصطفي"
    ]
    interviewers = ["استاذه داليا", "مستر وليد", "مستر ابراهيم", "محمود", "الاء"]
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
    interviewers = ["استاذه داليا", "مستر وليد", "مستر ابراهيم", "محمود", "الاء"]
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

@app.route('/view_completed_interviews')
def view_completed_interviews():
    rows = []
    selected_employee = ''
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
        query = 'SELECT * FROM completed_interviews WHERE 1=1'
        params = []
        if selected_employee:
            query += ' AND employee_name = ?'
            params.append(selected_employee)
        if selected_employee:
            rows = conn.execute(query, params).fetchall()
    # else: do not show any rows
    conn.close()
    return render_template('view_completed_interviews.html', rows=rows, employees=employees, selected_employee=selected_employee)

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

# ======= تشغيل التطبيق =======
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
