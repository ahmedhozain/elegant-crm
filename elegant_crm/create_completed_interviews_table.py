import sqlite3
conn = sqlite3.connect('database.db')
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
    );
''')
conn.commit()
conn.close()
print('تم إنشاء جدول completed_interviews بنجاح.') 