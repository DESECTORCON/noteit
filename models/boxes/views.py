import shortid
from elasticsearch import Elasticsearch
from flask import Blueprint, request, session, url_for, render_template, flash
from werkzeug.utils import redirect
from models.notes.note import Note
import models.users.decorators as user_decorators
from models.notes.note import Note
from models.error_logs.error_log import Error_
import traceback
from config import ELASTIC_PORT as port

box_blueprint = Blueprint('boxs', __name__)


@box_blueprint.route('/box/<string:box_id>')
def box(box_id):
    pass


@box_blueprint.route('/box/create', methods=['GET', 'POST'])
@user_decorators.require_login
def create_box():
    all_notes = Note.get_user_notes(session['email'])
    if request.method == 'POST':
        pass

    return render_template('boxs/create_box.html', all_notes=all_notes)


@box_blueprint.route('/box/delete')
@user_decorators.require_login
def delete_box():
    pass
