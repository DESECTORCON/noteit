import shortid
from elasticsearch import Elasticsearch
from flask import Blueprint, request, session, url_for, render_template, flash
from werkzeug.utils import redirect
from models.boxes.box import Box
from models.notes.note import Note
import models.users.decorators as user_decorators
from models.notes.note import Note
from models.error_logs.error_log import Error_
import traceback
from config import ELASTIC_PORT as port

box_blueprint = Blueprint('boxs', __name__)


@box_blueprint.route('/boxs')
def boxs():
    all_boxs = Box

    return render_template('boxs/boxs_page.html')


@box_blueprint.route('/box/<string:box_id>')
def box(box_id):
    pass


@box_blueprint.route('/box/create', methods=['GET', 'POST'])
@user_decorators.require_login
def create_box():
    try:
        all_notes = Note.get_user_notes(session['email'])
        if request.method == 'POST':
            notes_selected = request.form.getlist('notes')
            name = request.form['name']
            maker_id = session['_id']

            box_for_save = Box(name=name, notes=notes_selected, maker_id=maker_id)
            box_for_save.save_to_elastic()
            box_for_save.save_to_mongo()

            redirect(url_for('.boxs'))

        return render_template('boxs/create_box.html', all_notes=all_notes)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='user note reading USER:' + session['email'])
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading your notes...')


@box_blueprint.route('/box/delete')
@user_decorators.require_login
def delete_box():
    pass
