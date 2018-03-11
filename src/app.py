from flask import Flask, render_template, session
import random
from src.models.notes.note import Note
from src.models.messages.message import *

app = Flask(__name__)
app.config.from_object('src.config')
app.secret_key = ''


@app.before_first_request
def init():
    Database.initialize()
    random_int = []
    for i in range(100):
        random_int.append(random.randint(1, 10000))
    app.secret_key = ''.join(str(random_int))

    session['_id'] = None
    session['email'] = None


def get_read_messages(session_id):
    return Message.find_by_recivers_not_readed(session_id)


def get_unread_messages(session_id):
    return Message.find_by_reciver_id(session_id)


def get_notes(email):
    return Note.find_by_user_email(email)


@app.route('/')
def home():
    messages = []
    notes = []
    if session['_id'] is not None:
        notes = get_notes(session['email'])

        messages = get_unread_messages(session['_id'])
        if messages is None:
            messages = get_read_messages(session['_id'])

    return render_template('home.html', messages=messages[:4], notes=notes[:4])


@app.route('/message')
def home2():
    return render_template('home2.html')


@app.route('/loading')
def loading():
    return render_template('loading.html')


from src.models.users.views import user_blueprint
from src.models.notes.views import note_blueprint
from src.models.messages.views import message_blueprint

app.register_blueprint(user_blueprint, url_prefix="/users")
app.register_blueprint(note_blueprint, url_prefix="/notes")
app.register_blueprint(message_blueprint, url_prefix='/messages')
