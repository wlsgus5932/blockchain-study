import time
import requests

from flask import (
    Blueprint,
    jsonify,
    request
)
from p2p import p2p_utils, config, db
from p2p.models import MiningNode


bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
def home():
    return "p2p"


@bp.route('/update/', methods=['GET', 'PUT'])
def update() -> dict:
    '''DB에 노드 정보를 업데이트'''

    # 요청 노드 정보 업데이트, 없으면 새로 만들어서 추가
    client_ip = request.args.get('ip')
    client_port = request.args.get('port')
    
    print(f'ip: {client_ip}, port: {client_port}')
    
    # if request.method == 'PUT':
    #     client_ip = request.json.get('ip')
    #     client_port = request.json.get('port')

    # 요청자가 IP 또는 PORT 정보를 보내지 않았을 경우 처리
    if not client_ip or not client_port:
        return jsonify({
            'status': 'fail',
            'content': f'cannot update using ip: {client_ip}, port: {client_port}'
        })
    
    client_exist = p2p_utils.check_node_exist(client_ip, client_port)

    # 요청 노드의 정보가 없다면 새로 추가
    if not client_exist:
        p2p_utils.add_new_node(client_ip, client_port)
    else:
    # 노드 정보가 존재한다면 timestamp 업데이트
        client_exist.timestamp = time.time()
        db.session.commit()

    # Seed node 기본으로 추가
    seed_exist = p2p_utils.check_node_exist(config.SEED_NODE_IP, config.PORT_P2P)
    if not seed_exist:
        p2p_utils.add_new_node(
            config.SEED_NODE_IP, 
            config.PORT_P2P
            )
        
    # DB에서 neighbors 정보 추출
    nodes = MiningNode.query.all()

    # Neighbor node로부터 정보를 받아서 저장
    for node in nodes:
        #자기 자신에게는 업데이트 요청을 하지 않음
        if node.ip==config.MY_PUBLIC_IP and node.port==config.PORT_P2P:
            continue
        else:
            url = f'http://{node.ip}:{node.port}/neighbors'
            try:
                resp = requests.get(url, timeout=3)
            except:
                print(f'Cannot access to {url}')
                continue
            
            neighbors_data = resp.json()
            neighbors = neighbors_data.values()
            
            for neighbor in neighbors:
                neighbor_exist = p2p_utils.check_node_exist(
                    neighbor['ip'],
                    neighbor['port']
                )
                if neighbor_exist is False:
                    p2p_utils.add_new_node(
                        neighbor['ip'],
                        neighbor['port']
                    )
                else: 
                    neighbor_exist.timestamp = time.time()
                    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'content': 'updated'
    })


@bp.route('/neighbors/', methods=['GET'])
def neighbors() -> dict:
    '''DB에 저장된 이웃 노드 정보를 리턴'''

    #TODO: DB에 저장된 이웃 노드 정보를 사전으로 만들기
    #내 정보를 확인 
    # -> 있다면 접속시간 업데이트
    # -> 없다면 새로 만들어서 저장
    my_info = p2p_utils.check_node_exist(
        config.MY_PUBLIC_IP,
        config.PORT_P2P
    )

    if not my_info:
        p2p_utils.add_new_node(
            config.MY_PUBLIC_IP,
            config.PORT_P2P
        )

    # DB의 모든 neighbors 정보를 기반으로 dict 생성
    p2p_data = MiningNode.query.all()
    p2p_data_dic = {}

    for idx, node in enumerate(p2p_data):
        p2p_data_dic[idx] = {
            'ip': node.ip,
            'port': node.port,
            'timestamp': node.timestamp
        }

    try:
        return jsonify(p2p_data_dic), 200
    except Exception as e:
        print(f'Error in neighbors: {e}')
        return jsonify({
            'status': 'fail'
        }), 400
    
    