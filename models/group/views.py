import os

from flask import Blueprint, request, render_template, session
import models.users.decorators as user_decorators
from models.group.group import Group
from models.users.user import User
from models.group.constants import ALLOWED_GROUP_IMG_FORMATS

group_blueprint = Blueprint('groups', __name__)


@group_blueprint.route('/groups', methods=['GET', 'POST'])
@user_decorators.require_login
def groups():
    all_groups = Group.get_all_shared_groups()
    
    if request.method is 'POST':
        form = request.form['Search']
        all_groups = Group.search_with_elastic(form_data=form, shared=True)
    
    return render_template('groups/shared_groups.html', all_groups=all_groups)


@group_blueprint.route('/create_group', methods=['GET', 'POST'])
@user_decorators.require_login
def create_group():
    all_firends = []
    current_user = User.find_by_id(session['_id'])
    for friend_id in current_user.friends:
        all_firends.append(User.find_by_id(friend_id))

    if request.method is 'POST':
        name = request.form['name']
        members = request.form.getlist('members')
        group_img = request.form['img']
        file_name, file_extenstion = os.path.splitext(group_img)
        if file_extenstion not in ALLOWED_GROUP_IMG_FORMATS or len(group_img) > 1:
            return render_template('groups/create_group.html',
                                   all_firends=all_firends, error_msg='Too much images!! Please upload just one image.',
                                   name=name, members=members)

        shared = request.form.get("shared") != None




    return render_template('groups/create_group.html', all_firends=all_firends)
