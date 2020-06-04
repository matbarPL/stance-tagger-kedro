import os
from flask import jsonify
from app.api import bp

@bp.route('/model/retrain', methods=['GET'])
def retrain_model():
    os.system(' "..\\Scripts\\activate" & cd ..\\stance-tagger-kedro\\ & kedro run ')
    response = jsonify({'kedro': 'retrained'})
    response.status_code = 201
    return response