
# Python
from datetime import datetime
from os import stat
from typing import List, Optional, Union
# Others
from human_id import generate_id

# Pydantinc
from pydantic import BaseModel, Required, Field, EmailStr, SecretStr

# FastAPI
from fastapi import FastAPI, Body, Query, Path
from db import db_interface


app = FastAPI()

Note_db = db_interface.Notes()
User_db = db_interface.Users()


# Models

class Note(BaseModel):
    note_id: str = Field(default_factory=generate_id)
    title: str = Field(default=Required, min_length=1)
    content: str = Field(default=Required)
    creation_date: Union[str, None] = Field(default=None)
    last_update: Union[str, None] = Field(default=None)


class Note_ID(BaseModel):
    note_id: str = Field(default=None)
    user_id: str = Field(default=None)

class User(BaseModel):
    user_id: str = Field(default=Required)
    email: EmailStr = Field(default=Required)
    name: str = Field(default=Required, min_length=1)
    notes_id: List[Note_ID] = Field(default_factory=List)

class _Password(BaseModel):
    user_id: str = Field(default=Required)
    password: SecretStr = Field(default=Required)

class UserRegister(BaseModel):
    user_id: str = Field(default_factory=generate_id)
    name: str = Field(default=Required, regex="^[a-zA-Z0-9_.-]+$")
    email: EmailStr = Field(default=Required)#, min_length=5, max_length=50, regex='^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
    password: SecretStr = Field(default=Required, min_length=8, max_length=20)

class UserLogin(BaseModel):
    email: str = Field(default=Required, min_length=5, max_length=50, regex='^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
    password: SecretStr = Field(default=Required, min_length=8, max_length=20)

# Notes App with FastAPI

# endpoints:
# Get: /{user_id}/notes -> Receive: user_id; Return: make a response with all user notes (the notes have a ID)
# Get: /{user_id}/notes/{note_id} -> Receive: user_id, note_id; Return: The specific note.
# Post: /{user_id}/new ->  Receive: user_id, JSON(keys -> 'title', 'content'); Return: A status code
## Post: /authorize/login -> Receive: JSON(keys -> 'email', 'password'); Return: A status code
## Post: /autorize/register -> Receive: JSON(keys -> 'name', 'email', 'password'); Return: A status code
# Put: /{user_id}/edit -> Receive: user_id, note_id; Return: A status code
# Delete: /{user_id}/delete -> Receive: user_id, note_id; Return: Status code


@app.get('/{user_id}/notes')
def get_all_notes(
    user_id: str = Path(default=Required, min_length=1)
):
    status, data = Note_db.query_item(
        'email = :v1',
        {':v1': user_id})

    if status:
        return {'status': 'OK', 'data': data}
    else:
        return {'status': 'Error getting all notes', 'data': data}

@app.get('/{user_id}/get/{note_id}')
def get_note_by_id(
    user_id: str = Path(default=Required, min_length=1), 
    note_id: str = Path(default=Required, min_length=1)
):
    status, data = Note_db.get_item({
        'email': user_id, 
        'note_id': note_id
        })
    if status:
        return {'status': 'OK', 'data': data}
    else:
        return {'status': 'Error getting note by ID', 'info': data}

@app.get('/{user_id}/delete/{note_id}')
def delete_note(
    user_id: str = Path(default=Required, min_length=1), 
    note_id: str = Path(default=Required, min_length=1)
):
    print(user_id, note_id)
    status, data = Note_db.delete_item({
        'email' : user_id,
        'note_id': note_id
        })
    print(status, data)
    if status:
        return {'status':'OK', 'data': data}
    else:
        return {'status': 'Error deleting the note', 'info': data}


@app.post('/{user_id}/update')
def update_note(
    user_id: str = Path(default=Required, min_length=1), 
    note: Note = Body(default=Required)
):
    status, data = Note_db.update_item(
        key={'email' : user_id, 'note_id': note.note_id}, 
        update_expression='set title = :title, content = :content, last_update = :last_update',
        expression_attribute_values={
            ':title': note.title,
            ':content': note.content,
            ':last_update': note.last_update
            })
    if status:
        return {'status': 'OK', 'data': 'Note Updated'}
    else:
        return {'status': 'Error Updating note', 'data': data}

@app.post('/{user_id}/new')
def create_new_note(
    user_id: str = Path(default=Required, min_length=1), 
    note: Note = Body(...)
):
    status, data = Note_db.put_item({
        'email' : user_id,
        **note.dict()
    })

    if status:
        return {'status': 'OK', 'note_id': note.note_id}
    else:
        return {'status': 'Error saving note', 'data': data}



@app.post('/authorize/login')
def login(
    user: UserLogin = Body(...)
):
    status, data = User_db.get_item({
        'email': user.email,
        })
    print(status, data)
    if status and data['password'] == user.password.get_secret_value():
        return {'status': 'OK', 'data': 'User logged in'}
    else:
        return {'status': 'Error', 'data': 'Wrong Email or Password'}


@app.post('/authorize/register')
def register(
    user: UserRegister = Body(...)
):
    # Check if email Exists
    status, data = User_db.get_item({
        'email': user.email,
    })
    if status:
        return {'status': 'Error', 'data': 'Email already exists'}
    else:
        status, data = User_db.put_item({
            'email': user.email,
            'name': user.name,
            'password': user.password.get_secret_value()
        })
        if status:
            return {'status': 'OK', 'data': 'User registered'}
        else:
            return {'status': 'Error', 'data': 'Error registering user'}
