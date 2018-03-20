from flask import Flask, render_template, session
import random
from models.notes.note import Note
from models.messages.message import *
import config as config

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = ''

random_int = []
for i in range(100):
    random_int.append(random.randint(1, 10000))
    app.secret_key = ''.join(str(random_int))


@app.before_first_request
def init():
    Database.initialize()
    session['_id'] = None
    session['email'] = None


@app.before_request
def before_request_session_reset():
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
    max_items = config.MAX_ITEMS
    messages = []
    notes = []
    if session['_id'] is not None:
        notes = get_notes(session['email'])

        messages = get_unread_messages(session['_id'])
        if messages is None:
            messages = get_read_messages(session['_id'])

    return render_template('home.html', messages=messages[:max_items], notes=notes[:max_items])


@app.route('/message')
def home2():
    return render_template('home2.html')


@app.route('/loading')
def loading():
    return render_template('loading.html')


@app.errorhandler(404)
def http_error_404(e):
    return render_template('error.html'), 404


from models.users.views import user_blueprint
from models.notes.views import note_blueprint
from models.messages.views import message_blueprint

app.register_blueprint(user_blueprint, url_prefix="/users")
app.register_blueprint(note_blueprint, url_prefix="/notes")
app.register_blueprint(message_blueprint, url_prefix='/messages')
