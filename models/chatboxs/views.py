from flask import Blueprint, render_template
import models.users.decorators as user_decorators
from models.chatboxs.chatbox import ChatBox

chatbox_blueprint = Blueprint('chatboxs', __name__)


@chatbox_blueprint.route('/chat/chatbox_group/<string:chatbox_id>')
@user_decorators.require_login
def chatbox(chatbox_id):
    chatbox_ = ChatBox.find_by_id(chatbox_id)
    messages = chatbox_.limit_find_messages()
    users = chatbox_.get_members()
    
    return render_template('chatboxs/chatbox.html', messages=messages, users=users)
