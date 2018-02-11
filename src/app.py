from flask import Flask, render_template, session
import random
from src.models.messages.message import *

app = Flask(__name__)
app.config.from_object('src.config')
app.secret_key = ''


@app.before_first_request
def init_db():
    Database.initialize()
    random_int = []
    for i in range(100):
        random_int.append(random.randint(1, 10000))
    app.secret_key = ''.join(str(random_int))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/message')
def home2():
    #try:
    #    user_messages = Message.find_by_reciver_id(session['_id'])
    #except KeyError:
    #    return render_template('home2.html')

    #for message in user_messages:

     #   if message.readed_by_reciver is True and message.readed_date is not None:
     #       user_messages.remove(message)

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
