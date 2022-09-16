
from datetime import datetime
from uuid import uuid4
import requests
import json

from flask import Flask, render_template, session, request, url_for, redirect
from flask_session import Session

app = Flask(__name__,
            static_folder='static',
            template_folder='static/html',
            static_url_path='/static')
app.secret_key = str(uuid4())
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

Errors = {
    'name': 'Invalid Name',
    'email': 'Invalid Email',
    'password': 'Invalid Password or Must Contain 8 Characters',
}

@app.route('/')
@app.route('/index')
def index():
    try:
        if session.get('valid_session'): 
            user_id = session.get('email')
            response = requests.get(
                f'http://localhost:8000/{user_id}/notes')
            
            response_json = json.loads(response.text)
            if response_json['status'] == 'OK':
                notes = response_json['data']
                return render_template('index.html', notes=notes)

            return render_template('index.html')
            # valid_session is True
        else:
            return redirect(url_for("login"))
            # valid_session is False (user logout)
    except (KeyError, TypeError):
        return redirect(url_for("login"))
        # User does not make a account


@app.route('/login')
def login():
    try:
        if session.get('valid_session'):
            return redirect(url_for("index"))
            # User has a session
        else:
            return render_template('login.html')
        # User is going to login
    except KeyError:
        return render_template('login.html')
        # User never created a acount


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    # Make comprobation of data to the api

    # ask to api if exists email
    response = requests.post(
        'http://localhost:8000/authorize/login',
        json={
            "email": email,
            "password": password})
    
    logs = json.loads(response.text)
    if response.status_code == 422:
        return render_template('login.html', error={'status': 'Wrong Email or Password'})
    
    if response.status_code == 200 and logs['status'] == 'OK':
        session['email'] = email
        session['valid_session'] = True
        return redirect(url_for("index"))
    else:
        return render_template('login.html', error={'status' : logs['data']})

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    email = request.form['email']
    password = request.form['password']
    name = request.form['user_name']
    
    # Make comprobation of data to the api
    response = requests.post(
        'http://localhost:8000/authorize/register', 
        json={
            "email": email, 
            "password": password, 
            "name": name})

    if response.status_code == 200:
        logs = json.loads(response.text)
        if logs["status"] != "OK":
            errors = logs['data']
            return render_template('register.html', error={'status': errors})    
        else:
            session['email'] = email
            session['valid_session'] = True
            return redirect(url_for("index"))

    elif response.status_code == 422:
        logs = json.loads(response.text)["detail"]
        errors = { error["loc"][1]: Errors[error["loc"][1]] for error in logs }
        return render_template('register.html', error=errors)

    else:
        return render_template('error.html')

@app.route('/logout')
def logout():
    session['valid_session'] = False
    return redirect(url_for("login"))

@app.route('/note')
def new_note():
    return render_template('note.html')

@app.route('/note', methods=['POST'])
def new_note_post(): # Save Note
    try:
        title = request.form['title']
        content = request.form['content']
        user_id = session.get('email')

        if len(title) == 0:
            return render_template('note.html', msg={"status": "Title must have at least 1 character"}, content=content)
    except UnboundLocalError:
        return render_template('note.html', msg={"status": "Title must have at least 1 character"}, content=content)

    
    title = request.form['title']
    content = request.form['content']
    user_id = session.get('email')
    
    response = requests.post(
        f'http://localhost:8000/{user_id}/new', 
        json={
            "title": title, 
            "content": content,
            "creation_date": str(datetime.utcnow()),
            "last_update": str(datetime.utcnow())
            })
    note_id = json.loads(response.text)['note_id']
    
    if response.status_code == 422:
        return render_template('note.html', msg={"status": "Title must not be empty or contain #$/&*(){}\ characters"}, content=content, title=title)
    else:
        return render_template('note.html', msg={"status": "Saved!"}, content=content, title=title, note_id=note_id, update=True)

@app.route('/note/edit', methods=['POST'])
def update_note_post(): # Update Note
    title = request.form['title']
    content = request.form['content']
    user_id = session.get('email')
    note_id = request.form['note_id']

    response = requests.post(
        f'http://localhost:8000/{user_id}/update', 
        json={
            "note_id": note_id,
            "title": title, 
            "content": content,
            "creation_date": str(datetime.utcnow()),
            "last_update": str(datetime.utcnow())
            })
    if json.loads(response.text)['status'] == 'OK':
        return render_template('note.html', msg={"status": "Saved!"}, content=content, title=title, note_id=note_id, update=True)
    else:
        return render_template('note.html', msg={"status": "Error!"}, content=content, title=title, note_id=note_id, update=True)


@app.route('/note/<note_id>', methods=['GET'])
def return_note(note_id):
    user_id = session.get('email')
    valid = session.get('valid_session')
    # Asks to api if the user has this note
    response = requests.get(
        f'http://localhost:8000/{user_id}/get/{note_id}')

    
    logs = json.loads(response.text)
    if response.status_code == 200 and logs['status'] == "OK":
        title = logs['data']['title']
        content = logs['data']['content']
        note_id = logs['data']['note_id']
        return render_template('note.html', content=content, title=title, note_id=note_id, update=True)
    else:
        return render_template('note.html', msg={"status": "Error loading the note", "data":logs})

@app.route('/delete', methods=['POST'])
def delete_note():
    note_id = request.form['note_id']
    user_id = session.get('email')

    response = requests.get(
        f'http://localhost:8000/{user_id}/delete/{note_id}')

    if json.loads(response.text)['status'] == 'OK':
        return redirect(url_for("index"))
    else:
        return render_template('error.html')

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)