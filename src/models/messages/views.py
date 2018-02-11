import datetime

from flask import Blueprint, request, session, url_for, render_template
from werkzeug.utils import redirect
from src.models.messages.message import Message
import src.models.users.decorators as user_decorators
from src.models.users.user import User

message_blueprint = Blueprint('message', __name__)


@message_blueprint.route('/recived_messages/<string:user_id>')
@user_decorators.require_login
def my_recived_messages(user_id):
    messages = Message.find_by_reciver_id(user_id)
    user_nickname = User.find_by_id(session['_id']).nick_name

    return render_template('messages/my_recived_messages.html', messages=messages, user_nickname=user_nickname)


@message_blueprint.route('/sended_messages/<string:user_id>')
@user_decorators.require_login
def my_sended_messages(user_id):
    messages = Message.find_by_sender_id(user_id)
    user_nickname = User.find_by_id(session['_id']).nick_name

    return render_template('messages/my_sended_messages.html', messages=messages, user_nickname=user_nickname)


@message_blueprint.route('/send_message', methods=['GET', 'POST'])
@user_decorators.require_login
def send_message():

    all_users = User.get_all()
    recivers = []

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        try:
            #reciver_id = User.find_by_email(request.form['reciver_email'])._id
            recivers_string = request.form['reciver_email'].split()
            for email in recivers_string:
                recivers.append(User.find_by_email(email)._id)

        except Exception as e:
            return render_template('messages/send_message.html', e=e, all_users=all_users, title=title, content=content)

        sender_id = User.find_by_email(session['email'])._id

        message = Message(title=title, content=content, reciver_id=recivers, sender_id=sender_id)
        message.save_to_mongo()

        return redirect(url_for('.my_sended_messages', user_id=sender_id))

    return render_template('messages/send_message.html', all_users=all_users)


@message_blueprint.route('/message/<string:message_id>')
@user_decorators.require_login
def message(message_id, is_sended=False):
    message = Message.find_by_id(message_id)

    if message is None:
        return 'There was an server error. Please try again a another time!'

    if message.readed_by_reciver is False and is_sended is False and session['_id'] == message.reciver_id:
        message.readed_by_reciver = True
        message.readed_date = datetime.datetime.now()
        message.save_to_mongo()

    sender_nickname = User.find_by_id(message.sender_id).nick_name
    reciver_nickname = User.find_by_id(message.reciver_id).nick_name

    return render_template('messages/message.html', message=message, sender_nickname=sender_nickname, reciver_nickname=reciver_nickname)


@message_blueprint.route('/all_messages/')
@user_decorators.require_login
def all_messages():
    all_messagess = Message.find_all()

    return render_template('messages/all_messages.html', all_messagess=all_messagess)


@message_blueprint.route('/delete_message/<string:message_id>')
@user_decorators.require_login
def delete_message(message_id):
    message = Message.find_by_id(message_id)

    message.delete()
    return redirect(url_for('.my_recived_messages', user_id=session['_id']))

