from flask import request, session, Blueprint,jsonify
from ..models.Model import CMemberTable
from ..config import db,bcrypt
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required

# 初始化biueprint
auth = Blueprint('auth', __name__)