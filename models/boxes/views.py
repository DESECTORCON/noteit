import shortid
from elasticsearch import Elasticsearch
from flask import Blueprint, request, session, url_for, render_template, flash
from werkzeug.utils import redirect
from models.notes.note import Note
import models.users.decorators as user_decorators
from models.users.user import User
from models.error_logs.error_log import Error_
import traceback
from config import ELASTIC_PORT as port

box_blueprint = Blueprint('boxs', __name__)


@box_blueprint.route('/box/<string:box_id>')
def box(box_id):
    pass
