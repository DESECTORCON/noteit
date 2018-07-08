import uuid
from flask import Blueprint, render_template, url_for, session, request, flash
from werkzeug.utils import redirect
import models.users.decorators as user_decorators
from models.chatboxs.chatbox import ChatBox
from models.messages.message import Message
from models.users.user import User
from flask_socketio import SocketIO, emit
from app import app
import ast

chatbox_blueprint = Blueprint('chatboxs', __name__)
socketio = SocketIO(app)


@chatbox_blueprint.route('/chat/create_chat/<string:default_members>', methods=['POST', 'GET'])
@user_decorators.require_login
def create_chatbox(default_members):
    current_user = User.find_by_id(session['_id'])
    user_friends = current_user.get_friends()
    if request.method == 'GET':
        if default_members is not []:
            default_members_obj = []
            for member in ast.literal_eval(default_members):
                member_obj = User.find_by_id(member)
                if member_obj is not None:
                    default_members_obj.append(member_obj)

            return render_template('chatboxs/create_chatbox.html', user_friends=default_members_obj, default=True)
        return render_template('chatboxs/create_chatbox.html', user_friends=user_friends)

    if request.method == 'POST':
        chatbox_members = request.form.getlist('user')
        chatbox_members.append(session['_id'])
        if chatbox_members == [] or chatbox_members is None:
            return render_template('chatboxs/create_chatbox.html', user_friends=user_friends
                                   , error_msg='You havn\'t selected any friends!')

        _id = uuid.uuid4().hex
        chatbox_ = ChatBox(user_ids=chatbox_members, _id=_id, name=request.form['title'])
        chatbox_.save_to_mongo()
        return redirect(url_for('chatboxs.chatbox', chatbox_id=_id))


@chatbox_blueprint.route('/chat/chatbox_group/<string:chatbox_id>')
@user_decorators.require_login
def chatbox(chatbox_id):
    chatbox_ = ChatBox.find_by_id(chatbox_id)
    messages = chatbox_.limit_find_messages()
    users = chatbox_.get_members()
    session['chatbox_id'] = chatbox_._id

    return render_template('chatboxs/chatbox.html', messages=messages, users=users, chatbox_=chatbox_)


@chatbox_blueprint.route('/chat/chatbox/delete', defaults={'secession_chatbox_id': None}, methods=['POST', 'GET'])
@chatbox_blueprint.route('/chat/chatbox/delete/<string:secession_chatbox_id>', methods=['POST', 'GET'])
@user_decorators.require_login
def secession_chatbox(secession_chatbox_id=None):
    user_chatboxs = ChatBox.get_user_chatboxs(session['_id'])
    if request.method == 'POST':
        if secession_chatbox_id is not None:
            chatbox_obj = ChatBox.find_by_id(secession_chatbox_id)
            chatbox_obj.user_ids.remove(session['_id'])
            chatbox_obj.save_to_mongo()

            flash('Succefully secessioned chatbox '+ chatbox_obj.name)
            return redirect(url_for('chatboxs.chatboxs'))
        secession_chatboxes = request.form.getlist('secession_chatboxes')
        chatbox_objs = []
        for _id in secession_chatboxes:
            if ChatBox.find_by_id(_id) is not None:
                chatbox_objs.append(ChatBox.find_by_id(_id))
        for chatbox in chatbox_objs:
            chatbox.user_ids.remove(session['_id'])
            chatbox.save_to_mongo()
        return redirect(url_for('chatboxs.chatboxs'))

    return render_template('chatboxs/secession_chatbox.html', user_chatboxs=user_chatboxs)


@chatbox_blueprint.route('/chat/chatbox_group/send_message')
@user_decorators.require_login
def save_message(methods=['GET', 'POST']):
    chatbox_ = ChatBox.find_by_id(session['chatbox_id'])
    title = None
    content = request.form['content']
    if content is '':
        return redirect(url_for('chatboxs.chatbox', chatbox_id=session['chatbox_id']))

    sender = User.find_by_email(session['email'])
    sender_name = sender.nick_name
    sender_id = sender._id

    message = Message(title=title, content=content,
                      reciver_id=session['chatbox_id'], sender_id=sender_id, is_a_noteOBJ=False, sender_name=sender_name)
    message.save_to_mongo()
    message.save_to_elastic()

    chatbox_.messages.extend([message._id])
    chatbox_.save_to_mongo()

    return redirect(url_for('chatboxs.chatbox', chatbox_id=session['chatbox_id']))


@chatbox_blueprint.route('/chat/chatboxs')
@user_decorators.require_login
def chatboxs():
    chatboxes = ChatBox.get_user_chatboxs(session['_id'])
    user_ = User.find_by_id(session['_id'])

    return render_template('chatboxs/user_chatboxs.html', chatboxs=chatboxes, user_=user_)


@socketio.on('submit')
def send(json, methods=['POST', 'GET']):
    chatbox_ = ChatBox.find_by_id(session['chatbox_id'])
    title = None
    content = json['content']
    if content is '':
        return
    else:
        sender = User.find_by_email(session['email'])
        sender_name = sender.nick_name
        sender_id = sender._id

        message = Message(title=title, content=content,
                          reciver_id=session['chatbox_id'], sender_id=sender_id, is_a_noteOBJ=False,
                          sender_name=sender_name)
        message.save_to_mongo()
        message.save_to_elastic()

        chatbox_.messages.extend([message._id])
        chatbox_.save_to_mongo()

        # make response data for emit
        response_data = {
            "created_date": message.sended_date.strftime('%m/%d/%Y'),
            "content": message.content,
            "sender_name": message.sender_name,
            "sender_id": message.sender_id
        }

        socketio.emit('chat response', response_data, broadcast=True)


@socketio.on('left')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    emit('status', {'msg': session['email'] + ' has left the room.'})


@socketio.on("request")
def request_():
    latest_message_ = ChatBox.latest_message_()
    emit("response", {'data': latest_message_, 'email': session['email']}, broadcast=True)

