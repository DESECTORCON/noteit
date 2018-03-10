import datetime
from src.models.error_logs.error_log import Error_
from flask import Blueprint, request, session, url_for, render_template
from werkzeug.utils import redirect
from src.models.messages.message import Message
import src.models.users.decorators as user_decorators
from src.models.notes.note import Note
from src.models.users.user import User
import traceback

message_blueprint = Blueprint('message', __name__)


@message_blueprint.route('/recived_messages/<string:user_id>')
@user_decorators.require_login
def my_recived_messages(user_id):
    try:
        messages = Message.find_by_reciver_id(user_id)
        user_nickname = User.find_by_id(session['_id']).nick_name

        return render_template('messages/my_recived_messages.html', messages=messages, user_nickname=user_nickname)
    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='my_recived_messages-during message finding')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading your messages')


@message_blueprint.route('/sended_messages/<string:user_id>')
@user_decorators.require_login
def my_sended_messages(user_id):
    try:
        messages = Message.find_by_sender_id(user_id)
        user_nickname = User.find_by_id(session['_id']).nick_name

        return render_template('messages/my_sended_messages.html', messages=messages, user_nickname=user_nickname)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='my_sended_messages-during message finding')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading your messages')


@message_blueprint.route('/send_message', methods=['GET', 'POST'])
@user_decorators.require_login
def send_message():

    try:
        all_users = User.get_all()
        recivers = []

        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']

            if request.form['reciver_email'] in [None, [], ""]:
                return render_template('messages/send_message.html',
                                       e='Your receiver field is empty. Please fill in at least ONE receiver.',
                                       all_users=all_users, title=title,
                                       content=content)

            try:
                # reciver_id = User.find_by_email(request.form['reciver_email'])._id
                recivers_string = request.form['reciver_email'].split()

                for email in recivers_string:
                    recivers.append(User.find_by_email(email)._id)

            except Exception:
                return render_template('messages/send_message.html', e="Please Check That you have coped EXACTLY the target user's email! And separated the emails with spaces!!"
                                       , all_users=all_users, title=title, content=content)

            sender_id = User.find_by_email(session['email'])._id

            message = Message(title=title, content=content, reciver_id=recivers, sender_id=sender_id, is_a_noteOBJ=False)
            message.save_to_mongo()

            return redirect(url_for('.my_sended_messages', user_id=sender_id))

        return render_template('messages/send_message.html', all_users=all_users)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='send_message message sending')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during sending your message...')


@message_blueprint.route('/message/<string:message_id>')
@user_decorators.require_login
def message(message_id, is_sended=False):

    try:

        message = Message.find_by_id(message_id)

        if message is None:
            return 'There was an server error. Please try again a another time!'

        if message.readed_by_reciver is False and is_sended is False and session['_id'] in message.reciver_id and message.readed_date is None:
            message.readed_by_reciver = True
            message.readed_date = datetime.datetime.now()
            message.save_to_mongo()

        sender_nickname = User.find_by_id(message.sender_id).nick_name
        if type(message.reciver_id) is list:
            reciver_nickname = []
            for reciver in message.reciver_id:
                reciver_nickname.append(User.find_by_id(reciver).nick_name)

        else:
            reciver_nickname = User.find_by_id(message.reciver_id).nick_name

        if message.is_a_noteOBJ:
            note = Note.find_by_id(message.content)
        else:
            note = None

        return render_template('messages/message.html', message=message, sender_nickname=sender_nickname,
                               reciver_nickname=reciver_nickname, is_a_note=message.is_a_noteOBJ, note=note)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='message message reading')
        Error_obj.save_to_mongo()

        return render_template('error_page.html', error_msgr='Crashed during reading message...')


@message_blueprint.route('/all_messages/')
@user_decorators.require_login
def all_messages():
    try:
        all_messagess = Message.find_all()

        return render_template('messages/all_messages.html', all_messagess=all_messagess)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='message reading')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading your messages...')


@message_blueprint.route('/delete_message/<string:message_id>')
@user_decorators.require_login
def delete_message(message_id):
    try:
        message = Message.find_by_id(message_id)

        message.delete()
        return redirect(url_for('.my_recived_messages', user_id=session['_id']))

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='delete_message message deleting')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during deleteing your message...')


@message_blueprint.route('/send_note', methods=['GET', 'POST'])
@user_decorators.require_login
def send_note():
    all_notes = Note.get_all()
    all_users = User.get_all()

    if request.method == 'POST':

        try:
            note = Note.find_by_id(request.form['note'])
        except:

            error_msg = traceback.format_exc().split('\n')

            Error_obj = Error_(error_msg=''.join(error_msg), error_location='send_note note finding/reading')
            Error_obj.save_to_mongo()

            return render_template('error_page.html', error_msgr='Crashed during preparing page...')

        message_title = request.form['title']

        if request.form.getlist("user") in [None, [], ""]:
            return render_template('messages/send_note.html',
                                   e="You hadn't selected an reciver. Please select at least ONE reciver.",
                                   all_users=all_users, title=message_title,)

        else:

            recivers = request.form.getlist("user")

        sender_id = User.find_by_email(session['email'])._id

        message = Message(title=message_title, content=note._id, reciver_id=recivers, sender_id=sender_id, is_a_noteOBJ=True)
        message.save_to_mongo()

        return redirect(url_for('.my_sended_messages', user_id=sender_id))

    return render_template('messages/send_note.html',
                           all_notes=all_notes, all_users=all_users)


@message_blueprint.route('/send_note_<string:note_id>', methods=['GET', 'POST'])
@user_decorators.require_login
def send_note_radio(note_id):
    note = Note.find_by_id(note_id)
    all_notes = Note.get_all()
    all_users = User.get_all()

    if request.method == 'POST':

        try:
            note = Note.find_by_id(request.form['note'])
        except:

            error_msg = traceback.format_exc().split('\n')

            Error_obj = Error_(error_msg=''.join(error_msg), error_location='send_note note finding/reading')
            Error_obj.save_to_mongo()

            return render_template('error_page.html', error_msgr='Crashed during preparing page...')

        message_title = request.form['title']

        if request.form.getlist("user") in [None, [], ""]:
            return render_template('messages/send_note.html',
                                   e="You hadn't selected an reciver. Please select at least ONE reciver.",
                                   all_users=all_users, title=message_title,)

        else:

            recivers = request.form.getlist("user")

        sender_id = User.find_by_email(session['email'])._id

        message = Message(title=message_title, content=note._id, reciver_id=recivers, sender_id=sender_id, is_a_noteOBJ=True)
        message.save_to_mongo()

        return redirect(url_for('.my_sended_messages', user_id=sender_id))

    return render_template('messages/send_note.html',
                           all_notes=all_notes, all_users=all_users, note_=note)

