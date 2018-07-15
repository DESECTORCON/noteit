import datetime
import os
import traceback
import shortid
import werkzeug
from elasticsearch import Elasticsearch
from flask import Blueprint, request, session, url_for, render_template, flash
from werkzeug.utils import redirect, secure_filename
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
                    session['group_id'] = user.group_id
                    return redirect(url_for("home"))

            except UserErrors.UserError as e:
                return render_template("users/login.html", message=e)

        return render_template("users/login.html", message=e)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='login_user while logining user')
        Error_obj.save_to_mongo()
        return render_template('base_htmls/error_page.html', error_msgr='Crashed during login...')


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
            file = request.files.get('file')

            if file and User.allowed_file(file):
                # create name for file
                sid = shortid.ShortId()
                # create path for file
                file_path, file_extenstion = os.path.splitext(file.filename)
                filename = secure_filename(sid.generate()) + file_extenstion

                # os.chdir("static/img/file/")
                # save file and add file to filenames list
                file.save(os.path.join(filename))

            # if extenstion is not supported
            elif file is not None:
                flash("Sorry; your file's extension is supported.")
                return render_template("users/register.html")

            try:
                try:
                    if User.register_user(email, password, nick_name, filename):
                        user = User.find_by_email(email)
                        session['email'] = email
                        session['_id'] = user._id
                        session['group_id'] = user.group_id

                        return redirect(url_for("home"))
                except UnboundLocalError:
                    if User.register_user(email, password, nick_name):
                        user = User.find_by_email(email)
                        session['email'] = email
                        session['_id'] = user._id
                        session['group_id'] = user.group_id

                        return redirect(url_for("home"))

            except UserErrors.UserError as e:
                return e.message

        return render_template("users/register.html")

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='register_user while registering user')
        Error_obj.save_to_mongo()
        return render_template('base_htmls/error_page.html', error_msgr='Crashed during registering you...')


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
    session.clear()

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
        return render_template('base_htmls/error_page.html', error_msgr='Crashed during reading information...')


@user_blueprint.route('/user/<string:user_id>')
def user_page(user_id):

    try:
        user = User.find_by_id(user_id)
        if user is None:
            user = User.find_by_email(user_id)
        user_notes = Note.find_shared_notes_by_user(user.email)
        try:
            filepath = url_for('static', filename=user.picture)
        except werkzeug.routing.BuildError:
            filepath = None

        return render_template('/users/user.html', user=user, user_notes=user_notes
                               , user_note_count=len(user_notes), filepath=filepath)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg),
                           error_location='user_page while loading user{} info'.format(user_id))
        Error_obj.save_to_mongo()
        return render_template('base_htmls/error_page.html', error_msgr='Crashed during reading information...')


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
        return render_template('base_htmls/error_page.html', error_msgr='Crashed during deleting your account...')


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
        return render_template('base_htmls/error_page.html', error_msgr='Crashed during saving changes...')


@user_blueprint.route('/add_friend', methods=['GET', 'POST'])
@user_decorators.require_login
def add_friend():
    all_users = User.get_all()
    current_user = User.find_by_id(session['_id'])
    all_users.remove(current_user)
    user_friends = current_user.friends

    all_users_ = []
    for user in all_users:
        if user._id not in user_friends:
            all_users_.append(user)

    users_list = []
    for user in all_users_:
            try:
                users_list.append({'url': url_for('static', filename=user.picture), 'user_id': user._id,
                                   "last_logined":user.last_logined,
                                   "nickname": user.nick_name,
                                   "email": user.email})

            except werkzeug.routing.BuildError:
                try:
                    users_list.append({'url': url_for('static', filename='img/index.jpg'), 'user_id': user._id,
                                       "last_logined":user.last_logined,
                                       "nickname": user.nick_name,
                                       "email": user.email})
                except:
                    raise Exception('File image not exists. server shutdown')

    if request.method == 'POST':
        current_user.friends.extend(request.form.getlist('users'))
        current_user.save_to_mongo()
        return redirect(url_for('users.user_page', user_id=current_user._id))

    return render_template('users/add_friend.html', all_users=all_users, users_list=users_list)


@user_blueprint.route('/searhc_', methods=['POST'])
def search_for_above():
    users = []
    form = request.form['Search_users']

    el = Elasticsearch(port=port)

    if form is '':
        data = el.search(index='users', doc_type='user', body={
            "query": {
                "match_all": {}
            }
        })
    else:
        data = el.search(index='users', doc_type='user', body={
            "query": {
                "prefix": {"nick_name": form}
            }
        })

    try:
        for user in data['hits']['hits']:
            users.append(User.find_by_id(user['_id']))
    except:
        pass
    # print(users)
    del el
    try:
        return render_template('users/add_friend.html', all_users=users, form=form, selected=request.form['users'])
    except:
        return render_template('users/add_friend.html', all_users=users, form=form)
