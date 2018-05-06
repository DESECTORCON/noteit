from flask import Blueprint, request, session, url_for, render_template, flash
from werkzeug.utils import redirect
from models.boxes.box import Box
import models.users.decorators as user_decorators
from models.notes.note import Note
from models.error_logs.error_log import Error_
import traceback

box_blueprint = Blueprint('boxs', __name__)


@box_blueprint.route('/boxs/search/<string:return_page>', methods=['POST'])
@user_decorators.require_login
def search_boxes(return_page):
    try:

        search_ = request.form['search']
        search_result = Box.search_with_elastic(search_, session['_id'])

        return render_template(return_page, all_boxs=search_result, search_=search_)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='boxes box searching')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during searching your boxes...')


@box_blueprint.route('/boxs')
@user_decorators.require_login
def boxs():
    all_boxs = Box.get_user_boxes(session['_id'])

    return render_template('boxs/boxs_page.html', all_boxs=all_boxs)


@box_blueprint.route('/box/<string:box_id>')
@user_decorators.require_login
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

            return redirect(url_for('boxs.boxs'))

        return render_template('boxs/create_box.html', all_notes=all_notes)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='user box creating USER:' + session['email'])
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during creating your box...')


@box_blueprint.route('/box/delete')
@user_decorators.require_login
def delete_box():
    pass
