# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    # Sort: Incomplete first, then High > Medium > Low, then soonest due date
    query = '''
        SELECT * FROM tasks
        ORDER BY 
            is_completed ASC,
            CASE priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
                ELSE 4
            END ASC,
            due_date ASC;
    '''
    tasks = conn.execute(query).fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    priority = request.form.get('priority', 'Medium')
    due_date = request.form.get('due_date')

    if title:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO tasks (title, priority, due_date) VALUES (?, ?, ?)',
            (title, priority, due_date)
        )
        conn.commit()
        conn.close()

    return redirect(url_for('index'))

@app.route('/complete/<int:id>', methods=['POST'])
def complete_task(id):
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET is_completed = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_task(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)