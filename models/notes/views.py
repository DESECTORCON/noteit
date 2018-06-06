import os
import uuid
import shortid
import werkzeug
from elasticsearch import Elasticsearch
from flask import Blueprint, request, session, url_for, render_template, flash
from werkzeug.utils import redirect
from models.boxes.box import Box
from models.group.group import Group
from models.notes.note import Note
import models.users.decorators as user_decorators
from models.users.user import User
from models.error_logs.error_log import Error_
import traceback
from config import ELASTIC_PORT as port
from werkzeug.utils import secure_filename

note_blueprint = Blueprint('notes', __name__)


def is_shared_validator(shared, share_only_with_users):
    if shared is True:
        label = 'Shared to all'
    elif share_only_with_users is True:
        label = 'Shared only to note-it users'
    else:
        label = 'Not shared'

    return label


def share_bool_function(share):
    if share == '0':
        raise ValueError()
    elif share == '1':
        share = True
        share_only_with_users = False

    elif share == '2':
        share = False
        share_only_with_users = True

    else:
        share = False
        share_only_with_users = False

    return share, share_only_with_users


@note_blueprint.route('/my_notes/', defaults={'box_id': None}, methods=['POST', 'GET'])
@note_blueprint.route('/my_notes/<string:box_id>', methods=['POST', 'GET'])
@user_decorators.require_login
def user_notes(box_id=None):
    try:

        boxs = Box.get_user_boxes(session['_id'])
        user = User.find_by_email(session['email'])
        user_name = user.email

        if box_id is None:
            user_notes = User.get_notes(user)
            box_name = ''
            search = True

        else:
            box = Box.find_by_id(box_id)
            user_notes = box.get_notes()
            box_name = box.name
            search = False

        if request.method == 'POST':
            form_ = request.form['form']
            if box_id is None:
                notes = Note.search_with_elastic(form_, user_nickname=user.nick_name, box_id=False)
            else:
                notes = Note.search_with_elastic(form_, user_nickname=user.nick_name, box_id=box_id)

            return render_template('/notes/my_notes_sidebar.html', user_notes=notes, user_name=user_name,
                                   form=form_, boxs=boxs, box_name=box_name, search=search, box_id=box_id)

        else:
            return render_template('/notes/my_notes_sidebar.html', user_name=user_name
                                   , user_notes=user_notes, boxs=boxs, box_name=box_name, search=search, box_id=box_id)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='user note reading USER:' + session['email'])
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading your notes...')


@note_blueprint.route('/note/<string:note_id>')
def note(note_id):
    try:
        all_boxs = Box.get_user_boxes(session['_id'])
        note = Note.find_by_id(note_id)
        user = User.find_by_email(note.author_email)
        filenames = note.file_name

        urls = []
        if filenames is [] or filenames is None:
            pass
        else:
            try:
                for filename in filenames:
                    file_extenstion = filename.split('.')[1]
                    if file_extenstion in ['mp4', 'ogg', 'mov', 'wmv']:
                        is_video = True
                    else:
                        is_video = False

                    if file_extenstion in ['jpg', 'gif', 'bmp', 'tiff', 'png']:
                        is_pic = True
                    else:
                        is_pic = False

                    urls.append({'url': url_for('static', filename=filename),
                                 'is_video': is_video, 'filename': filename, 'is_pic': is_pic,
                                 'extenstion': file_extenstion})
            except:
                file_extenstion = filenames.split('.')[1]
                if file_extenstion in ['mp4', 'ogg', 'mov', 'wmv']:
                    is_video = True
                else:
                    is_video = False

                if file_extenstion in ['jpg', 'gif', 'bmp', 'tiff', 'png']:
                    is_pic = True
                else:
                    is_pic = False

                urls.append({'url': url_for('static', filename=filenames),
                             'is_video': is_video, 'filename': filenames, 'is_pic': is_pic,
                             'extenstion': file_extenstion})

        try:
            if note.author_email == session['email']:
                author_email_is_session = True
            else:
                author_email_is_session = False

        except:
            author_email_is_session = False

        finally:

            return render_template('/notes/note.html', note=note,
                                   author_email_is_session=author_email_is_session, msg_=False, user=user
                                   , url=urls,all_boxs=all_boxs)

    except:
        error_msg = traceback.format_exc().split('\n')

        try:

            Error_obj = Error_(error_msg=''.join(error_msg), error_location='note reading')
        except:
            Error_obj = Error_(error_msg=''.join(error_msg), error_location='note reading NOTE:NONE')

        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading your note...')


@note_blueprint.route('/add_note', defaults={'box_id': None}, methods=['POST', 'GET'])
@note_blueprint.route('/add_note/<string:box_id>', methods=['GET', 'POST'])
@user_decorators.require_login
def create_note(box_id):
    try:
        if request.method == 'POST':
            # getting forms
            share = request.form['inputGroupSelect01']

            # share label error handler
            try:
                share, share_only_with_users = share_bool_function(share)
            except ValueError:
                return render_template('/notes/create_note.html',
                                       error_msg="You did not selected an Share label. Please select an Share label.")

            # getting title content and email
            title = request.form['title']
            content = request.form['content_'].strip('\n').strip('\r')
            author_email = session['email']

            # getting files and saving
            try:
                # getting files
                files = request.files.getlist('file')

                # file length checker
                if len(files) > 5:
                    flash("Too much files!")
                    return render_template('/notes/create_note.html'
                                           , title=title, content=content, share=share)

                filenames = []
                for file in files:
                    if files and Note.allowed_file(file):
                        # create name for file
                        sid = shortid.ShortId()
                        # create path for file
                        file_path, file_extenstion = os.path.splitext(file.filename)
                        filename = secure_filename(sid.generate()) + file_extenstion

                        # os.chdir("static/img/file/")
                        # save file and add file to filenames list
                        file.save(os.path.join(filename))
                        filenames.append(filename)

                    # if extenstion is not supported
                    elif file is not None:
                        flash("Sorry; your file's extension is supported.")
                        return render_template('/notes/create_note.html'
                                               , title=title, content=content, share=share)
                    else:
                        filenames = []

            except:
                # file = None
                filenames = []

            # getting author nickname, label and user notes
            author_nickname = User.find_by_email(author_email).nick_name

            label = is_shared_validator(share, share_only_with_users)

            user_notes = Note.get_user_notes(session['email'])

            # if too much notes, then redirect
            if len(user_notes) > 20:
                flash("You have the maximum amount of notes. Please delete your notes")
                return redirect(url_for(".user_notes", box_id=box_id))

            # saving note
            all_box_id = box_id
            note_id = uuid.uuid4().hex

            try:
                share_with_group = request.form['share_with_group']

                if share_with_group == 'on':
                    try:
                        user = User.find_by_id(session['_id'])
                        share_with_group = True
                        group = Group.find_by_id(user.group_id)
                        group.shared_notes.append({'note_id': note_id, 'author': user._id})
                        group.save_to_mongo()
                        group.update_to_elastic()
                    except:
                        flash("You aren't in a group. Please join a group to share with group users.")
                        return render_template('/notes/create_note.html'
                                        , title=title, content=content, share=share)

                else:
                    share_with_group = False

            except werkzeug.exceptions.BadRequestKeyError:
                share_with_group = False

            else:
                share_with_group = False

            note_for_save = Note(_id=note_id, title=title, content=content, author_email=author_email, shared=share,
                                 author_nickname=author_nickname, share_only_with_users=share_only_with_users,
                                 share_label=label, file_name=filenames, box_id=all_box_id
                                 , share_with_group=share_with_group)
            note_for_save.save_to_mongo()
            note_for_save.save_to_elastic()
            if box_id is not None:
                box_for_save = Box.find_by_id(all_box_id)
                box_for_save.notes.append(note_id)
                box_for_save.save_to_mongo()
                box_for_save.update_to_elastic()

            # flash message and redirect
            flash('Your note has successfully created.')

            return redirect(url_for('.user_notes'))

        return render_template('/notes/create_note.html')

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='create_note creating note')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during saving your note...')


@note_blueprint.route('/delete_note/<string:note_id>')
@user_decorators.require_login
def delete_note(note_id, redirect_to='.user_notes'):
    try:
        note = Note.find_by_id(note_id)
        note.delete_on_elastic()
        note.delete_img()
        note.delete()
        flash('Your note has successfully deleted.')
        return redirect(url_for(redirect_to))

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='notes deleting note')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during deleting your note...')


@note_blueprint.route('/pub_notes/', methods=['GET', 'POST'])
def notes():
    try:
        all_boxs = Box.get_user_boxes(session['_id'])
        if request.method == 'POST':
            form_ = request.form['Search_note']

            el = Elasticsearch(port=port)

            if form_ is '':
                data = el.search(index='notes', doc_type='note', body={
                    "query": {
                        "match_all": {}
                    }
                })
            else:
                data = el.search(index='notes', doc_type='note', body={
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "prefix": {"title": form_},
                                },
                                {
                                    "prefix": {"author_nickname": form_},
                                },
                                {
                                    "term": {"content": form_}
                                }
                            ]
                        }
                    }
                })

            notes = []
            try:
                for note in data['hits']['hits']:

                    if note['_source']['shared'] is True:
                        notes.append(Note.find_by_id(note['_source']['note_id']))
                    else:
                        if note['_source']['share_only_with_users'] is True and session['email'] is not None:
                            notes.append(Note.find_by_id(note['_source']['note_id']))

                        else:
                            pass
            except:
                pass

            del el
            return render_template('/notes/pub_notes.html', notes=notes, form=form_)

        try:
            if session['email'] is None:
                return render_template('/notes/pub_notes.html', notes=Note.find_shared_notes())
            else:
                return render_template('/notes/pub_notes.html',
                                       notes=Note.get_only_with_users() + Note.find_shared_notes())
        except:
            return render_template('/notes/pub_notes.html', notes=Note.find_shared_notes())

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='notes public note reading')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading users notes...')


@note_blueprint.route('/edit_note/<string:note_id>', methods=['GET', 'POST'])
@user_decorators.require_login
def edit_note(note_id):
    try:
        note = Note.find_by_id(note_id)

        if request.method == 'POST':

            share = request.form['inputGroupSelect01']

            try:
                share, share_only_with_users = share_bool_function(share)
            except ValueError:
                return render_template('/notes/create_note.html',
                                       error_msg="You did not selected an Share label. Please select an Share label.")

            title = request.form['title']
            content = request.form['content']

            note.shared = share
            note.share_only_with_users = share_only_with_users
            note.title = title
            note.content = content
            note.label = is_shared_validator(share, share_only_with_users)
            note.save_to_mongo()
            note.update_to_elastic()
            flash('Your note has successfully saved.')

            return redirect(url_for('.note', note_id=note_id))

        else:
            return render_template('/notes/edit_note.html', note=note, content=note.content.strip('\n').strip('\r'))

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg),
                           error_location='edit_note saveing and getting input from html file')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during saving your note...')


@note_blueprint.route('/delete_note_multiple/')
@user_decorators.require_login
def delete_note_multiple():
    user = User.find_by_email(session['email'])
    user_notes = User.get_notes(user)
    user_name = user.email

    return render_template("/notes/delete_multiple.html", user_notes=user_notes, user_name=user_name)


@note_blueprint.route('/delete_multiple/', methods=['POST'])
@user_decorators.require_login
def delete_multiple():
    try:
        user = User.find_by_email(session['email'])
        user_notes = User.get_notes(user)
        user_name = user.email

        if request.method == 'POST':
            notes_id = request.form.getlist('delete')

            for note_id in notes_id:
                note = Note.find_by_id(note_id)
                note.delete_on_elastic()
                note.delete_img()
                try:
                    box = Box.find_by_id(note.box_id)
                    box.notes.remove(note._id)
                except:
                    note.delete()

            flash('Your notes has successfully deleted.')
            return redirect(url_for('.user_notes'))

        return render_template("/notes/delete_multiple.html", user_notes=user_notes, user_name=user_name)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='notes public note reading')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading users notes...')


@note_blueprint.route('/search_notes', methods=['POST'])
@user_decorators.require_login
def search_notes(box_id):
    user = User.find_by_email(session['email'])
    user_name = user.email
    form_ = request.form['Search_note']
    notes = Note.search_with_elastic(form_, user_nickname=user.nick_name, box_id=box_id)

    return render_template('/notes/delete_multiple.html', user_notes=notes, user_name=user_name,
                               form=form_)


@note_blueprint.route('/add_to_box/<string:note_id>', methods=['POST'])
@user_decorators.require_login
def add_to_box(note_id):
    box_id = request.form['box']

    note_for_save = Note.find_by_id(note_id)
    box_for_save  = Box.find_by_id(box_id)

    note_for_save.box_id = box_id
    box_for_save.notes.append(note_id)
    note_for_save.save_to_mongo()
    note_for_save.update_to_elastic()
    box_for_save.save_to_mongo()
    box_for_save.update_to_elastic()
    return redirect(url_for('.user_notes', box_id=box_id))


@note_blueprint.route('/add_to_group/', methods=['POST', 'GET'])
@user_decorators.require_login
def add_to_group():

    # getting all user's notes
    notes = Note.get_user_notes(session['email'])

    if request.method == 'POST':
        user = User.find_by_id(session['_id'])
        if user.group_id is None:
            flash("You aren't in a group. Please join a group to share notes to friends.")
            return redirect(url_for('groups.groups'))

        group_ = Group.find_by_id(user.group_id)
        add_notes = request.form.getlist('selected_notes')

        for note in add_notes:
            note = Note.find_by_id(note)
            group_.shared_notes.extend([{'author': user._id, 'note_id': note._id}])
        # saving to database
        group_.save_to_elastic()
        group_.save_to_mongo()

        return redirect(url_for('groups.group', group_id=group_._id))

    return render_template('notes/add_to_group.html', notes=notes)
