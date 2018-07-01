from flask import Blueprint, render_template, url_for
from werkzeug.utils import redirect
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
