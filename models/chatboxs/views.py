from flask import Blueprint, render_template
import models.users.decorators as user_decorators
from models.chatboxs.chatbox import ChatBox

chatbox_blueprint = Blueprint('chatboxs', __name__)


@chatbox_blueprint.route('/chat/chatbox_group/<string:chatbox_id>')
@user_decorators.require_login
def chatbox(chatbox_id):
    messages = ChatBox.find_by_id()
    
    return render_template('chatboxs/chatbox.html', messages=None)
