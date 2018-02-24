from src.models.error_logs.error_log import Error_
from flask import Blueprint, render_template
import traceback


error_log_blueprint = Blueprint('error_log', __name__)


@error_log_blueprint.route('/server_error___@@')
def error_page(error_location=None, error_message=None):
    error_msg = traceback.format_exc().split('\n')

    Error_obj = Error_(error_msg=''.join(error_msg), error_location=error_location)
    Error_obj.save_to_mongo()

    return render_template('error_page.html', error_msgr=error_message)
