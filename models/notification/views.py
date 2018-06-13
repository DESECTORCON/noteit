from flask import Blueprint, render_template
from models.notification.notification import Notification

notification_blueprint = Blueprint('notification', __name__)


@notification_blueprint.route('/notification/<string:notification_id>')
def notification(notification_id):
    notifi = Notification.find_by_id(notification_id)
    
    return render_template('notifications/notification.html', notifi=notifi)
