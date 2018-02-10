import datetime
import time
from flask import Blueprint, request, session, url_for, render_template
from werkzeug.utils import redirect
import src.models.users.errors as UserErrors
from src.common.utils import Utils
from src.models.messages.message import Message
from src.models.notes.note import Note
from src.models.users.user import User
import src.models.users.decorators as user_decorators

user_blueprint = Blueprint('users', __name__)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login_user():
    e = ''
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        try:
            if User.is_login_valid(email, password):
                session['email'] = email
                user = User.find_by_email(email)
                session['_id'] = user._id
                user.last_logined = datetime.datetime.now()
                user.save_to_mongo()
                return redirect(url_for("home"))

        except UserErrors.UserError as e:
            return render_template("users/login.html", message=e)

    return render_template("users/login.html", message=e)  # TODO:Send the user an error if their Login was invalid


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register_user():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        nick_name = request.form['nickname']

        try:
            if User.register_user(email, password, nick_name):
                session['email'] = email
                message = Message(title="Welcome to Note-it™!",
                                  content="""Welcome to Note-it! You can make a note,
                                        and share it with other users! Or you can
                                        just keep the note to your selves.
                                        You can send messages to other users too! Check out this website!!""",
                                  reciver_id=User.find_by_email(email)._id,
                                  sender_id=User.find_by_email('SE@SENOREPLAY.COM')._id)
                message.save_to_db()
                return redirect(url_for("home"))

        except UserErrors.UserError as e:
            return e.message

    return render_template("users/register.html")


#@user_blueprint.route('/alerts')
#@user_decorators.require_login
#def user_notes():
#    user = User.find_by_email(session['email'])
#    alerts = user.get_alerts()
#    user_name = user.email
#    return render_template('users/alerts.html', alerts=alerts, user_name=user_name)


@user_blueprint.route('/logout')
@user_decorators.require_login
def logout_user():
    session['email'] = None
    session['_id'] = None

    return redirect(url_for('home'))


@user_blueprint.route('/users', methods=['GET', 'POST'])
def users_page():
    users = User.get_all()
    #TODO: 일래스틱서치 배우고 완료하기
    return render_template('/users/users_page.html', users=users)


@user_blueprint.route('/user/<string:user_id>')
def user_page(user_id):
    try:
        user = User.find_by_id(user_id)
    except:
        user = User.find_by_email(user_id)
    user_notes = Note.find_shared_notes_by_user(user.email)

    return render_template('/users/user.html', user=user, user_notes=user_notes, user_note_count=len(user_notes))


@user_blueprint.route('/delete_user/<string:user_id>', methods=['GET', 'POST'])
@user_decorators.require_login
def delete_user(user_id):

    if request.method == 'POST':
        user = User.find_by_id(user_id)
        user.delete_user_notes()
        user.delete()
        session['email'] = None
        return redirect(url_for('home'))

    return render_template('/users/confrim.html')


@user_blueprint.route('/edit_user/<string:user_id>', methods=['GET', 'POST'])
@user_decorators.require_login
def edit_user(user_id):
    current_user = User.find_by_id(user_id)

    if request.method == 'POST':

        nick_name = request.form['nickname']

        current_user.nick_name = nick_name
        current_user.save_to_mongo()

        return redirect(url_for('.user_page', user_id=user_id))

    return render_template("users/edit_user.html", user=current_user)
