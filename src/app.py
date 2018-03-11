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


@app.route('/')
def home():
    try:
        if session['_id'] is not None:
            notes = Note.find_by_user_email(session['email'])
            notes_length = len(notes)

            messages = Message.find_by_recivers_not_readed(session['_id'])

            if messages is None:
                messages = Message.find_by_reciver_id(session['_id'])
                if messages is None:
                    return render_template('home.html')
                else:
                    message_length = len(messages)

            else:
                message_length = len(messages)

            if notes_length is 0 and message_length is 0:

                return render_template('home.html')

            elif notes_length is 0 and message_length >= 1:

                try:
                    return render_template('home.html', notes=messages[:4])
                except:
                    return render_template('home.html', notes=messages)

            elif notes_length >= 1 and message_length is 0:

                try:
                    return render_template('home.html', notes=notes[:4])
                except:
                    return render_template('home.html', notes=notes)

            elif notes_length >= 1 and message_length >= 1:

                if message_length > 4 and notes_length > 4:
                    return render_template('home.html', notes=notes[:4], messages=messages[:4])

                elif message_length > 4 and notes_length <= 4:
                    return render_template('home.html', notes=notes, messages=messages[:4])

                elif message_length <= 4 and notes_length > 4:
                    return render_template('home.html', notes=notes[:4], messages=messages)

                elif message_length <= 4 and notes_length <= 4:
                    return render_template('home.html', notes=notes, messages=messages)

            elif notes_length is 0 and message_length is not 0:
                try:
                    return render_template('home.html', messages=messages[:4])
                except:
                    return render_template('home.html', messages=messages)

            elif notes_length is not 0 and message_length is 0:
                try:
                    return render_template('home.html', notes=notes[:4])
                except:
                    return render_template('home.html', notes=notes)

        else:
            return render_template('home.html')
    except:
        return render_template('home.html')


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
