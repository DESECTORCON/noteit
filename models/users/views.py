import datetime
import traceback
from elasticsearch import Elasticsearch
from flask import Blueprint, request, session, url_for, render_template, flash
from werkzeug.utils import redirect
import models.users.errors as UserErrors
from models.error_logs.error_log import Error_
from models.notes.note import Note
from models.users.user import User
import models.users.decorators as user_decorators
from config import ELASTIC_PORT as port

user_blueprint = Blueprint('users', __name__)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login_user():

    try:
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
                    flash('You were successfully logged in')
                    return redirect(url_for("home"))

            except UserErrors.UserError as e:
                return render_template("users/login.html", message=e)

        return render_template("users/login.html", message=e)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='login_user while logining user')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during login...')


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register_user():

    try:
        if request.method == 'POST':

            email = request.form['email']
            if email == '':
                flash('Please type your email')
                return render_template("users/register.html")
            password = request.form['password']
            if password == '':
                flash('Please type your password')
                return render_template("users/register.html")
            nick_name = request.form['nickname']

            try:
                if User.register_user(email, password, nick_name):
                    user_id = User.find_by_email(email)._id
                    session['email'] = email
                    session['_id'] = user_id

                    return redirect(url_for("home"))

            except UserErrors.UserError as e:
                return e.message

        return render_template("users/register.html")

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='register_user while registering user')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during registering you...')


# @user_blueprint.route('/alerts')
# @user_decorators.require_login
# def user_notes():
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
    try:
        if request.method == 'POST':

            el = Elasticsearch(port=port)
            data = el.search(index='users', doc_type='user', body={
                                                    "query": {
                                                        "prefix": {"nick_name": request.form['Search_user']}
                                                    }
                                              })
            # For debug
            # print(request.form['Search_user'])
            # print(data)
            users = []
            try:
                for user in data['hits']['hits']:
                    users.append(User.find_by_id(user['_source']['user_id']))
            except:
                pass
            # print(users)
            del el
            return render_template('/users/users_page.html', users=users, form=request.form['Search_user'])

        else:
            users = User.get_all()
            return render_template('/users/users_page.html', users=users)


    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='users_page while loading users info and posting to html')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading information...')


@user_blueprint.route('/user/<string:user_id>')
def user_page(user_id):

    try:
        try:
            user = User.find_by_id(user_id)
        except:
            user = User.find_by_email(user_id)
        user_notes = Note.find_shared_notes_by_user(user.email)

        return render_template('/users/user.html', user=user, user_notes=user_notes, user_note_count=len(user_notes))

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg),
                           error_location='user_page while loading user{} info'.format(user_id))
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading information...')


@user_blueprint.route('/delete_user/<string:user_id>', methods=['GET', 'POST'])
@user_decorators.require_login
def delete_user(user_id):

    try:
        if request.method == 'POST':
            user = User.find_by_id(user_id)
            user.delete_user_notes()
            user.delete_user_boxes()
            user.delete_user_messages()
            user.delete()
            session['email'] = None
            session['_id'] = None
            return redirect(url_for('home'))

        return render_template('/users/confrim.html')

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='delete_user while removing user from database')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during deleting your account...')


@user_blueprint.route('/edit_user/<string:user_id>', methods=['GET', 'POST'])
@user_decorators.require_login
def edit_user(user_id):

    try:
        current_user = User.find_by_id(user_id)

        if request.method == 'POST':

            nick_name = request.form['nickname']

            current_user.nick_name = nick_name
            current_user.save_to_mongo()

            return redirect(url_for('.user_page', user_id=user_id))

        return render_template("users/edit_user.html", user=current_user)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg),
                           error_location='edit_user while finding user/saving changes to database')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during saving changes...')
