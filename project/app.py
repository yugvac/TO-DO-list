from flask import Flask, render_template, request, redirect, session
import os
import json

app = Flask(__name__)
app.secret_key = 'dev'

DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

def get_user_path(username):
    return os.path.join(DATA_DIR, f'{username}.json')

def get_user_tasks(username):
    path = get_user_path(username)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

def save_user_tasks(username, tasks):
    with open(get_user_path(username), 'w') as f:
        json.dump(tasks, f)

def valid_user(username, password):
    try:
        with open('users.json') as f:
            users = json.load(f)
        return users.get(username) == password
    except:
        return False

def register_user(username, password):
    try:
        with open('users.json') as f:
            users = json.load(f)
    except:
        users = {}
    if username in users:
        return False
    users[username] = password
    with open('users.json', 'w') as f:
        json.dump(users, f)
    return True

@app.route('/')
def index():
    if 'username' in session:
        return redirect('/home')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if valid_user(username, password):
            session['username'] = username
            return redirect('/home')
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if register_user(username, password):
            return redirect('/login')
        return render_template('register.html', error='Username taken')
    return render_template('register.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect('/login')
    user = session['username']
    tasks = get_user_tasks(user)
    search = request.form.get('search')
    if search:
        tasks = [task for task in tasks if search.lower() in task['text'].lower()]
    return render_template('home.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    if 'username' not in session:
        return redirect('/login')
    user = session['username']
    task_text = request.form['task']
    tasks = get_user_tasks(user)
    tasks.append({'text': task_text, 'done': False})
    save_user_tasks(user, tasks)
    return redirect('/home')

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle(task_id):
    if 'username' not in session:
        return redirect('/login')
    user = session['username']
    tasks = get_user_tasks(user)
    if 0 <= task_id < len(tasks):
        tasks[task_id]['done'] = not tasks[task_id]['done']
        save_user_tasks(user, tasks)
    return redirect('/home')

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    if 'username' not in session:
        return redirect('/login')
    user = session['username']
    tasks = get_user_tasks(user)
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_user_tasks(user, tasks)
    return redirect('/home')

@app.route('/clear', methods=['POST'])
def clear():
    if 'username' not in session:
        return redirect('/login')
    user = session['username']
    tasks = get_user_tasks(user)
    tasks = [task for task in tasks if not task['done']]
    save_user_tasks(user, tasks)
    return redirect('/home')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
