import uuid
from flask import Blueprint, render_template, url_for, session, request, flash
from werkzeug.utils import redirect
import models.users.decorators as user_decorators
from models.chatboxs.chatbox import ChatBox
from models.messages.message import Message
from models.users.user import User
from flask_socketio import SocketIO, emit, join_room, leave_room
from app import app
import ast

chatbox_blueprint = Blueprint('chatboxs', __name__)
socketio = SocketIO(app)


@chatbox_blueprint.route('/chat/create_chat/<string:default_members>', methods=['POST', 'GET'])
@user_decorators.require_login
def create_chatbox(default_members):
    current_user = User.find_by_id(session['_id'])
    user_friends = current_user.get_friends()
    default_members = ast.literal_eval(default_members)
    if request.method == 'GET':
        if default_members != []:
            default_members_obj = []
            for member in ast.literal_eval(default_members):
                member_obj = User.find_by_id(member)
                if member_obj is not None:
                    default_members_obj.append(member_obj)

            return render_template('chatboxs/create_chatbox.html', user_friends=default_members_obj, default=True)
        return render_template('chatboxs/create_chatbox.html', user_friends=user_friends, default=False)

    if request.method == 'POST':
        chatbox_members = request.form.getlist('user')
        if chatbox_members == [] or chatbox_members is None:
            return render_template('chatboxs/create_chatbox.html', user_friends=user_friends
                                   , error_msg='You havn\'t selected any friends!')
        chatbox_members.append(session['_id'])

        _id = uuid.uuid4().hex
        chatbox_ = ChatBox(user_ids=chatbox_members, _id=_id, name=request.form['title'])
        chatbox_.save_to_mongo()
        return redirect(url_for('chatboxs.chatbox', chatbox_id=_id))


@chatbox_blueprint.route('/chat/chatbox_group/<string:chatbox_id>')
@user_decorators.require_login
def chatbox(chatbox_id):
    chatbox_ = ChatBox.find_by_id(chatbox_id)
    if chatbox_ is None:
        flash('The chatbox you requested don\'t exists.')
        return redirect(url_for('chatboxs.chatboxs'))

    messages = chatbox_.limit_find_messages()
    users = chatbox_.get_members()
    session['chatbox_id'] = chatbox_._id

    current_user_friends = User.find_by_id(session['_id']).get_friends()
    addable_friends = []
    for user in current_user_friends:
        if user not in users:
            addable_friends.append(user)


    return render_template('chatboxs/chatbox.html', messages=messages, users=users, chatbox_=chatbox_,
                           user_friends=addable_friends)


@chatbox_blueprint.route('/chat/chatbox/delete', defaults={'secession_chatbox_id': None}, methods=['POST', 'GET'])
@chatbox_blueprint.route('/chat/chatbox/delete/<string:secession_chatbox_id>', methods=['GET'])
@user_decorators.require_login
def secession_chatbox(secession_chatbox_id):
    user_chatboxs = ChatBox.get_user_chatboxs(session['_id'])
    if secession_chatbox_id is not None:
        chatbox_obj = ChatBox.find_by_id(secession_chatbox_id)
        chatbox_obj.user_ids.remove(session['_id'])
        chatbox_obj.save_to_mongo()
        current_user_name = User.find_by_id(session['_id']).nick_name

        flash('Successfully secessioned chatbox ' + chatbox_obj.name)
        message_bar = Message(title="User %s has secessioned." % (current_user_name), content=None, reciver_id=None
                              , sender_id=None, sender_name="System")
        message_bar.save_to_mongo()
        return redirect(url_for('chatboxs.chatboxs'))

    if request.method == 'POST':
        if secession_chatbox_id is not None:
            chatbox_obj = ChatBox.find_by_id(secession_chatbox_id)
            chatbox_obj.user_ids.remove(session['_id'])
            chatbox_obj.save_to_mongo()

            flash('Successfully secessioned chatbox '+ chatbox_obj.name)
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
    socketio.emit('secession')
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
                          sender_name=sender_name, is_chat_message=True)
        message.save_to_mongo()
        try:
            message.save_to_elastic()
        except:
            pass

        chatbox_.messages.extend([message._id])
        chatbox_.save_to_mongo()

        # make response data for emit
        response_data = {
            "created_date": message.sended_date.strftime('%m/%d/%Y'),
            "content": message.content,
            "sender_name": message.sender_name,
            "sender_id": message.sender_id,
            "chatbox_members": chatbox_.user_ids
        }

        socketio.emit('chat response', response_data, broadcast=True, room=json['room'])



@socketio.on('secession')
def secession_chatbox(json):
    chatbox_obj = ChatBox.find_by_id(json['chatbox_id'])
    chatbox_obj.user_ids.remove(session['_id'])
    chatbox_obj.save_to_mongo()

    flash('Successfully secessioned chatbox '+ chatbox_obj.name)
    socketio.emit('secession_response', {"user_id": session['_id']}, broadcast=True, room=json['room'])
    return redirect(url_for('chatboxs.chatboxs'))

#
#
# @socketio.on('left')
# def left(message):
#     """Sent by clients when they leave a room.
#     A status message is broadcast to all people in the room."""
#     emit('status', {'msg': session['email'] + ' has left the room.'}, room=None)


@socketio.on('join')
def connect_join(data):
    useremail = data['user_email']
    room = data['room']
    join_room(room)
    socketio.send(useremail + 'has entered the room.', room=room)


@socketio.on('left')
def on_leave(data):
    username = data['user_email']
    room = data['room_id']
    leave_room(room)
    socketio.send(username + ' has left the room.', room=room)


@socketio.on("request")
def request_():
    latest_message_ = ChatBox.latest_message_()
    emit("response", {'data': latest_message_, 'email': session['email']}, broadcast=True)


@socketio.on('addfriend')
def add_friend(json, methods=['POST', 'GET']):
    data = json['data_']
    chatbox = ChatBox.find_by_id(session['chatbox_id'])
    if data is '':
        return
    else:
        user_objs = []
        for dic in data:
            if not dic['value'] in chatbox.user_ids:
                chatbox.user_ids.append(dic['value'])
                user_obj = User.find_by_id(dic['value'])
                if user_obj.picture is None or user_obj.picture == '':
                    user_objs.append(
                        {
                            "user_name": user_obj.nick_name,
                            "user_email": user_obj.email,
                            "user_photo_path": url_for('static', filename='img/index.jpg'),
                            "user_url": url_for('users.user_page', user_id=user_obj._id)
                        }
                    )
                else:
                    user_objs.append(
                        {
                            "user_name": user_obj.nick_name,
                            "user_email": user_obj.email,
                            "user_photo_path": url_for('static', filename=user_obj.picture),
                            "user_url": url_for('users.user_page', user_id=user_obj._id)
                        }
                    )

                chatbox.save_to_mongo()

    emit("addfriend response", {'data': data, 'user_objs': user_objs}, broadcast=True, room=json['room'])
