import os
from datetime import timedelta
from flask import Flask, render_template, session, url_for, flash, jsonify
import random
from werkzeug.utils import redirect
from models.notes.note import Note
from models.messages.message import *
import config as config
from models.users.user import User
import psutil


try:
    os.chdir('static')
except FileNotFoundError:
    pass
app = Flask(__name__)
app.config.from_object('config')
app.secret_key = '23ncr92yr932c9y20c23jy9803yn489xrr4#$VT@%YBU%UI^IUVYTt2t¥¨¨¨¨˚¶§•˜˜§¢˙£™£¢®∂¢™£©ç∞˙74'
wsgi_app = app.wsgi_app

random_int = []
for i in range(100):
    random_int.append(random.randint(1, 10000))
    app.secret_key = ''.join(str(random_int))
#
#
# @app.route('/upload', methods=['GET', 'POST'])
# @require_login
# def upload():
#     if request.method == 'POST' and 'media' in request.files:
#         filename = files.save(request.files['media'])
#
#     return redirect(url_for('user_notes'))


@app.before_request
def before_request():
    now = datetime.datetime.now()
    try:
        last_active = session['last_active']
        delta = now - last_active
        if delta.seconds > 3600:
            session['last_active'] = now
            session['email'] = None
            session['_id'] = None
            flash('Your session has expired. Please re-login.')
            return redirect(url_for('users.login'))
    except:
        pass

    try:
        session['last_active'] = now
    except:
        pass


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)


@app.before_first_request
def init():
    Database.initialize()
    session['_id'] = None
    session['email'] = None
    flash('Heads up! service user finding and service Message Centre has been closed.')


def get_read_messages(session_id):
    return Message.find_by_recivers_not_readed(session_id)


def get_unread_messages(session_id):
    return Message.find_by_reciver_id(session_id)


def get_notes(email):
    return Note.find_by_user_email(email)


@app.route('/')
def home():
    try:
        if session['_id'] is None or session['email'] is None:
            pass
    except:
        session['_id'] = None
        session['email'] = None

    max_items = config.MAX_ITEMS
    messages = []
    notes = []
    if session['_id'] is not None:
        notes = get_notes(session['email'])

        messages = get_unread_messages(session['_id'])
        if messages is None:
            messages = get_read_messages(session['_id'])

        user = User.find_by_id(session['_id'])

        return render_template('home.html', messages=messages[:max_items], notes=notes[:max_items], user=user)

    return render_template('home.html', messages=messages[:max_items], notes=notes[:max_items])


@app.route('/message')
def home2():
    return render_template('home2.html')


@app.route('/groups')
def home3():
    return render_template('home3.html')


@app.route('/chatbox')
def home4():
    return render_template('home4.html')


@app.route('/loading')
def loading():
    return render_template('loading.html')


@app.errorhandler(404)
def http_error_404(e):
    return render_template('base_htmls/error.html'), 404


@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify(str(psutil.cpu_percent()))


from models.users.views import user_blueprint
from models.notes.views import note_blueprint
from models.messages.views import message_blueprint
from models.boxes.views import box_blueprint
from models.group.views import group_blueprint
from models.notification.views import notification_blueprint
from models.chatboxs.views import chatbox_blueprint

app.register_blueprint(user_blueprint, url_prefix="/users")
app.register_blueprint(note_blueprint, url_prefix="/notes")
app.register_blueprint(message_blueprint, url_prefix='/messages')
app.register_blueprint(box_blueprint, url_prefix='/boxs')
app.register_blueprint(group_blueprint, url_prefix='/groups')
app.register_blueprint(notification_blueprint, url_prefix='/notifications')
app.register_blueprint(chatbox_blueprint, url_prefix='/chatbox')
