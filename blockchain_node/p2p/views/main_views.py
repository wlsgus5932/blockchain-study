from flask import (
    Blueprint,
    jsonify
)

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
def home():
    return "p2p"


@bp.route('/update/', methods=['GET', 'PUT'])
def update() -> dict:
    '''DB에 노드 정보를 업데이트'''

    #TODO: 업데이트 요청이 올 경우 DB 업데이트

    return jsonify({
        'status': 'success',
        'content': 'updated'
    })


@bp.route('/neighbors/', methods=['GET'])
def neighbors() -> dict:
    '''DB에 저장된 이웃 노드 정보를 리턴'''

    #TODO: DB에 저장된 이웃 노드 정보를 사전으로 만들기
    
    return jsonify({
        'status': 'success',
        'content': 'neighbors'
    })