from flask import Blueprint, render_template, url_for, session
from werkzeug.utils import redirect

from models.group.group import Group
from models.notification.notification import Notification

notification_blueprint = Blueprint('notification', __name__)


@notification_blueprint.route('/notification/<string:notification_id>')
def notification(notification_id):
    notifi = Notification.find_by_id(notification_id)
    
    return render_template('notifications/notification.html', notifi=notifi)


@notification_blueprint.route('/notifi/delete/<string:notifi_id>')
def delete_notifi(notifi_id, redirect_to):
    Notification.find_by_id(notifi_id).delete()
    return redirect(url_for(redirect_to))


@notification_blueprint.route('/notifi/dismis/dismis_notifi/<string:notification_id>')
def dismis_notifi(notification_id):
    notifi = Notification.find_by_id(notification_id)
    notifi.dismis_to.extend([session['_id']])
    notifi.save_to_mongo()
    if notifi.type == 'to_group':
        group_ = Group.find_by_id(notifi.target)
        if notifi.dismis_to == group_.members:
            notifi.delete()

    return redirect(url_for('groups.group', group_id=session['group_id']))
