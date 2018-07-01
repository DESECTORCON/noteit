from flask import Blueprint, request, session, url_for, render_template, flash
from werkzeug.utils import redirect
from models.boxes.box import Box
import models.users.decorators as user_decorators
from models.notes.note import Note
from models.error_logs.error_log import Error_
import traceback

from models.users.user import User

box_blueprint = Blueprint('boxs', __name__)


@box_blueprint.route('/search_boxs', methods=['POST'])
@user_decorators.require_login
def search_boxes():
    try:

        search_ = request.form['search']
        search_result = Box.search_with_elastic(search_, session['_id'])

        return render_template('boxs/boxs_page.html', all_boxs=search_result, search_=search_)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='boxes box searching')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during searching your boxes...')


@box_blueprint.route('/boxs')
@user_decorators.require_login
def boxs():
    all_boxs = Box.get_user_boxes(session['_id'])
    all_notes = Note.get_user_notes(session['email'])

    return render_template('boxs/boxs_page.html', all_boxs=all_boxs ,all_notes=all_notes)


@box_blueprint.route('/box/<string:box_id>')
@user_decorators.require_login
def box(box_id):
    box = Box.find_by_id(box_id)
    notes = box.get_box_notes()

    return render_template('boxs/box.html', box=box, notes=notes)


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


@box_blueprint.route('/delete/<string:box_id>')
@user_decorators.require_login
def delete_box(box_id):
    try:
        box = Box.find_by_id(box_id)
        box.delete_on_elastic()
        box.delete()
        return redirect(url_for('.boxs'))
    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='user box creating USER:' + session['email'])
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during creating your box...')


@box_blueprint.route('/delete_notes_inbox_/<string:box_id>', methods=['GET', 'POST'])
@user_decorators.require_login
def delete_notes_inbox_(box_id):
    try:
        if request.method == 'POST':
            notes_to_delete = request.form.getlist('delete')
            box = Box.find_by_id(box_id)
            for note in notes_to_delete:
                del box.notes[box.notes.index(note)]
            box.save_to_mongo()
            box.save_to_elastic()
            return redirect(url_for('boxs.box', box_id=box_id))
        else:
            box = Box.find_by_id(box_id)
            box_notes = box.get_box_notes()
            return render_template('boxs/delete_notes_inbox.html', box_notes=box_notes, box_id=box_id)
    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='user box creating USER:' + session['email'])
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during creating your box...')


@box_blueprint.route('/delete_box_mutiple', methods=['POST', 'GET'])
@user_decorators.require_login
def delete_box_mutiple():
    try:
        user = User.find_by_email(session['email'])
        user_boxs = Box.get_user_boxes(session['_id'])
        user_name = user.email

        if request.method == 'POST':
            boxes_id = request.form.getlist('delete')

            for box_id in boxes_id:
                box = Box.find_by_id(box_id)
                if box is not None:
                    box.delete_on_elastic()
                    box.delete()

            flash('Your boxes has successfully deleted.')
            return redirect(url_for('.boxs'))

        return render_template("/boxs/delete_box_mutiple.html", user_boxs=user_boxs, user_name=user_name)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='boxes delete mutiple')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr="Crashed during deleting user's boxes...")
