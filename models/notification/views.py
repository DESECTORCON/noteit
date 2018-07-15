from flask import Blueprint, render_template, url_for, session
from werkzeug.utils import redirect
from models.group.group import Group
from models.notification.notification import Notification
from models.chatboxs.views import socketio

notification_blueprint = Blueprint('notification', __name__)


@notification_blueprint.route('/notification/<string:notification_id>')
def notification(notification_id):
    notifi = Notification.find_by_id(notification_id)
    
    return render_template('notifications/notification.html', notifi=notifi)


@notification_blueprint.route('/notifi/delete/<string:notifi_id>')
def delete_notifi(notifi_id, redirect_to):
    Notification.find_by_id(notifi_id).delete()
    return redirect(url_for(redirect_to))


@socketio.on('delete notifi')
def delete_notifi_socket(json, methods=['POST', 'GET']):
    Notification.find_by_id(json['notifi_id']).delete()
    socketio.emit('delete notifi response', {"success": True, "notifi_id": json['notifi_id']}, broadcast=True)


@socketio.on('connect notifi')
def connect():
    pass


@notification_blueprint.route('/notifi/dismis/dismis_notifi/<string:notification_id>')
def dismis_notifi(notification_id):
    notifi = Notification.find_by_id(notification_id)
    notifi.dismis_to.extend([session['_id']])
    notifi.save_to_mongo()
    if notifi.type == 'to_group':
        group_ = Group.find_by_id(notifi.target)
        if set(notifi.dismis_to) == set(group_.members):
            notifi.delete()

    return redirect(url_for('groups.group', group_id=session['group_id']))
