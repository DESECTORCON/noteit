from flask import Blueprint, request, session, url_for, render_template
from werkzeug.utils import redirect
from src.models.notes.note import Note
import src.models.users.decorators as user_decorators
from src.models.users.user import User

note_blueprint = Blueprint('notes', __name__)


@note_blueprint.route('/my_notes/')
@user_decorators.require_login
def user_notes():
    user = User.find_by_email(session['email'])
    user_notes = User.get_notes(user)
    user_name = user.email

    return render_template('/notes/my_notes.html', user_name=user_name, user_notes=user_notes)


@note_blueprint.route('/note/<string:note_id>')
def note(note_id):
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

        return render_template('/notes/note.html', note=note, author_email_is_session=author_email_is_session, msg_=False, user=user)


@note_blueprint.route('/add_note', methods=['GET', 'POST'])
@user_decorators.require_login
def create_note():

    if request.method == 'POST':
        share = request.form.get("share") != None
        title = request.form['title']
        content = request.form['content']
        author_email = session['email']
        author_nickname = User.find_by_email(author_email).nick_name

        note_for_save = Note(title=title, content=content, author_email=author_email, shared=share, author_nickname=author_nickname)
        note_for_save.save_to_mongo()

        return redirect(url_for('.user_notes'))

    return render_template('/notes/create_note.html')


@note_blueprint.route('/delete_note/<string:note_id>')
@user_decorators.require_login
def delete_note(note_id):

    try:
        Note.find_by_id(note_id).delete()
    finally:
        return redirect(url_for('.user_notes'))


@note_blueprint.route('/share_note/<string:note_id>')
@user_decorators.require_login
def share_note(note_id):
    try:
        Note.find_by_id(note_id).share_or_unshare()
    finally:
        return redirect(url_for('.note', note_id=note_id, msg='Your note is shared!!', msg_=True))


@note_blueprint.route('/pub_notes/')
def notes():

    return render_template('/notes/pub_notes.html', notes=Note.find_shared_notes())


@note_blueprint.route('/edit_note/<string:note_id>', methods=['GET', 'POST'])
@user_decorators.require_login
def edit_note(note_id):

    note = Note.find_by_id(note_id)

    if request.method == 'POST':
        share = request.form.get("share") != None
        title = request.form['title']
        content = request.form['content']

        note.shared = share
        note.title = title
        note.content = content
        note.save_to_mongo()

        return redirect(url_for('.note', note_id=note_id))

    else:
        return render_template('/notes/edit_note.html', note=note)
