from elasticsearch import Elasticsearch
from flask import Blueprint, request, session, url_for, render_template
from werkzeug.utils import redirect
from models.notes.note import Note
import models.users.decorators as user_decorators
from models.users.user import User
from models.error_logs.error_log import Error_
import traceback

note_blueprint = Blueprint('notes', __name__)


@note_blueprint.route('/my_notes/', methods=['POST', 'GET'])
@user_decorators.require_login
def user_notes():
    try:

        user = User.find_by_email(session['email'])
        user_notes = User.get_notes(user)
        user_name = user.email

        if request.method == 'POST':
            el = Elasticsearch(port=9200)
            if request.form['Search_note'] is '':
                data = el.search(index='notes', doc_type='note', body={
                                                        "query": {
                                                            "match_all": {}
                                                        }
                                                  })
            else:
                data = el.search(index='notes', doc_type='note', body={
                    "query": {
                        "prefix": {"title": request.form['Search_note']}
                    }
                })

            notes = []
            try:
                for note in data['hits']['hits']:
                    notes.append(Note.find_by_id(note['_source']['note_id']))
            except:
                pass
            # print(users)
            return render_template('/notes/my_notes.html', user_notes=notes, user_name=user_name, form=request.form['Search_note'])

        else:


            return render_template('/notes/my_notes.html', user_name=user_name, user_notes=user_notes)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='user note reading USER:' + session['email'])
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading your notes...')


@note_blueprint.route('/note/<string:note_id>')
def note(note_id):

    try:
        note = Note.find_by_id(note_id)
        user = User.find_by_email(note.author_email)

        try:
            if note.author_email == session['email']:
                author_email_is_session = True
            else:
                author_email_is_session = False

        except:
            author_email_is_session = False

        finally:

            return render_template('/notes/note.html', note=note,
                                   author_email_is_session=author_email_is_session, msg_=False, user=user)

    except:
        error_msg = traceback.format_exc().split('\n')

        try:

            Error_obj = Error_(error_msg=''.join(error_msg), error_location='note reading NOTE:' + note._id)
        except:
            Error_obj = Error_(error_msg=''.join(error_msg), error_location='note reading NOTE:NONE')

        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading your note...')


@note_blueprint.route('/add_note', methods=['GET', 'POST'])
@user_decorators.require_login
def create_note():

    try:
        if request.method == 'POST':
            share = request.form['inputGroupSelect01']

            if share == '0':
                return render_template('/notes/create_note.html',
                                       error_msg="You did not selected an Share label. Please select an Share label.")

            elif share == '1':
                share = True
                share_only_with_users = False

            elif share == '2':
                share = False
                share_only_with_users = True

            else:
                share = False
                share_only_with_users = False

            title = request.form['title']
            content = request.form['content']
            author_email = session['email']
            author_nickname = User.find_by_email(author_email).nick_name

            note_for_save = Note(title=title, content=content, author_email=author_email, shared=share,
                                 author_nickname=author_nickname ,share_only_with_users=share_only_with_users)
            note_for_save.save_to_mongo()
            note_for_save.save_to_elastic()

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
        note.delete()
    finally:
        return redirect(url_for(redirect_to))


@note_blueprint.route('/share_note/<string:note_id>')
@user_decorators.require_login
def share_note(note_id):

    try:
        Note.find_by_id(note_id).share_or_unshare()
    finally:
        return redirect(url_for('.note', note_id=note_id, msg='Your note is shared!!', msg_=True))


@note_blueprint.route('/pub_notes/')
def notes():

    try:

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

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='notes publick note reading')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during reading users notes...')


@note_blueprint.route('/edit_note/<string:note_id>', methods=['GET', 'POST'])
@user_decorators.require_login
def edit_note(note_id):

    try:
        note = Note.find_by_id(note_id)

        if request.method == 'POST':

            share = request.form['inputGroupSelect01']

            if share == '0':
                return render_template('/notes/create_note.html',
                                       error_msg="You did not selected an Share label. Please select an Share label.")

            if share == '1':
                share = True
                share_only_with_users = False

            else:
                share = False
                share_only_with_users = True

            title = request.form['title']
            content = request.form['content']

            note.shared = share
            note.share_only_with_users = share_only_with_users
            note.title = title
            note.content = content
            note.save_to_mongo()

            return redirect(url_for('.note', note_id=note_id))

        else:
            return render_template('/notes/edit_note.html', note=note)

    except:
        error_msg = traceback.format_exc().split('\n')

        Error_obj = Error_(error_msg=''.join(error_msg), error_location='edit_note saveing and getting input from html file')
        Error_obj.save_to_mongo()
        return render_template('error_page.html', error_msgr='Crashed during saving your note...')
