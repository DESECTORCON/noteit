import uuid
from flask import Blueprint, render_template, url_for, session, request
from werkzeug.utils import redirect
import models.users.decorators as user_decorators
from models.chatboxs.chatbox import ChatBox
from models.messages.message import Message
from models.users.user import User

chatbox_blueprint = Blueprint('chatboxs', __name__)


@chatbox_blueprint.route('/chat/create_chat/<string:default_members>', methods=['POST', 'GET'])
@user_decorators.require_login
def create_chatbox(default_members=[]):
    current_user = User.find_by_id(session['_id'])
    user_friends = current_user.get_friends()
    if request.method == 'GET':
        if default_members is not []:
            return render_template('chatboxs/create_chatbox.html', user_friends=user_friends, default_members=default_members)
        return render_template('chatboxs/create_chatbox.html', user_friends=user_friends)
        
    if request.method == 'POST':
        chatbox_members = request.form.getlist('user')
        if chatbox_members == [] or chatbox_members is None:
            return render_template('chatboxs/create_chatbox.html', user_friends=user_friends
                                   , error_msgc='You havn\'t selected any friends!')
        
        _id = uuid.uuid4().hex
        chatbox_ = ChatBox(user_ids=chatbox_members, _id=_id)
        chatbox_.save_to_mongo()
        return redirect(url_for('chatboxs.chatbox', chatbox_id=_id))
                

@chatbox_blueprint.route('/chat/chatbox_group/<string:chatbox_id>')
@user_decorators.require_login
def chatbox(chatbox_id):
    chatbox_ = ChatBox.find_by_id(chatbox_id)
    messages = chatbox_.limit_find_messages()
    users = chatbox_.get_members()
    chatbox_.update_last_logined()

    return render_template('chatboxs/chatbox.html', messages=messages, users=users, chatbox_=chatbox_)


@chatbox_blueprint.route('/chat/chatbox_group/send_message/<string:chatbox_id>', methods=['POST'])
@user_decorators.require_login
def save_message(chatbox_id):
    chatbox_ = ChatBox.find_by_id(chatbox_id)
    title = request.form['title']
    content = request.form['content']

    sender_id = User.find_by_email(session['email'])._id
    
    message = Message(title=title, content=content,
                      reciver_id=chatbox_id, sender_id=sender_id, is_a_noteOBJ=False)
    message.save_to_mongo()
    message.save_to_elastic()
    
    chatbox_.messages.extend([message._id])
    chatbox_.save_to_mongo()
    
    return redirect(url_for('chatbox', chatbox_id=chatbox_id))
