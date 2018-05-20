from flask import Blueprint, request, render_template
import models.users.decorators as user_decorators
from models.group.group import Group

group_blueprint = Blueprint('groups', __name__)


@group_blueprint.route('/groups', methods=['GET', 'POST'])
@user_decorators.require_login
def groups():
    all_groups = Group.get_all_shared_groups()
    
    if request.method is 'POST':
        form = request.form['Search']
        all_groups = Group.search_with_elastic(form_data=form, shared=True)
    
    return render_template('groups/shared_groups.html', all_groups=all_groups)