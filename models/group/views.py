from flask import Blueprint
import models.users.decorators as user_decorators

group_blueprint = Blueprint('groups', __name__)

@group_blueprint.route('/groups')
@user_decorators.require_login
def groups():
