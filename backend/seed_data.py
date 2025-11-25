import sqlite3
DB='db.sqlite'
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS attendance_records(id INTEGER PRIMARY KEY, attendance INTEGER, temp REAL, weekday INTEGER, special INTEGER, servings REAL)''')
c.execute('''CREATE TABLE IF NOT EXISTS waste_logs(id INTEGER PRIMARY KEY, date TEXT, dish TEXT, cooked REAL, consumed REAL, wasted REAL)''')
c.execute('DELETE FROM attendance_records')
records = [
    (100,28,1,0,100),
    (120,30,2,0,120),
    (80,25,3,0,80),
    (150,27,4,1,150),
    (95,29,5,0,95)
]
for r in records:
    c.execute('INSERT INTO attendance_records(attendance,temp,weekday,special,servings) VALUES (?,?,?,?,?)', r)
c.execute('DELETE FROM waste_logs')
sample = [
    ('2025-11-10','Rice',10,8,2),
    ('2025-11-10','Dal',8,7.5,0.5),
    ('2025-11-11','Rice',12,10,2),
]
for s in sample:
    c.execute('INSERT INTO waste_logs(date,dish,cooked,consumed,wasted) VALUES (?,?,?,?,?)', s)
conn.commit()
conn.close()
print('seeded db.sqlite')