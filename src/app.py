from flask import Flask, render_template
from src.common.database import Database

app = Flask(__name__)
app.config.from_object('src.config')
app.secret_key = 'hfhawehfwefjwjweojfwpowqkdklfwohor9r83yr2yrf92y39ry239fy2h239298h32fh23892yr839y829ry2r289ryyr923yrqdpkwqpoqr0u38ry2y82y7r'


@app.before_first_request
def init_db():
    Database.initialize()


@app.route('/')
def home():
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
