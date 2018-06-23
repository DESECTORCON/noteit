from flask import Blueprint, render_template, url_for, session, request
from werkzeug.utils import redirect
import models.users.decorators as user_decorators
from models.chatboxs.chatbox import ChatBox
from models.messages.message import Message

chatbox_blueprint = Blueprint('chatboxs', __name__)


@chatbox_blueprint.route('/chat/chatbox_group/<string:chatbox_id>')
@user_decorators.require_login
def chatbox(chatbox_id):
    chatbox_ = ChatBox.find_by_id(chatbox_id)
    messages = chatbox_.limit_find_messages()
    users = chatbox_.get_members()
    chatbox_.update_last_logined()
    session['chatbox'] = chatbox_
    
    return render_template('chatboxs/chatbox.html', messages=messages, users=users)


@chatbox_blueprint.route('/chat/chatbox_group/send_message/<string:chatbox_id>', methods=['POST'])
@user_decorators.require_login
def save_message(chatbox_id):
    chatbox_ = session['chatbox']
    
    message_ = Message()
    
    chatbox_.messages.extend(request.form['message'])
    
    return redirect(url_for('chatbox', chatbox_id=chatbox_id))
