import time
import requests
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
)
from flask_wtf.csrf import generate_csrf
from wallet.wallet import Wallet
from wallet.forms import TransferForm
from wallet.config import (SEED_NODE_IP, PORT_MINIG, PORT_P2P)
from wallet.utils import p2p_utils
from wallet import db

bp = Blueprint('transfer', __name__, url_prefix='/')

@bp.route('/transfer/', methods=['GET', 'POST'])
def transfer():
    '''코인 지갑 화면'''
    form = TransferForm()
    
    if request.method=='POST':
        data_dic = request.form.to_dict()
        print(f'data_dic: {data_dic}')

        send_blockchain_addr = data_dic.get('send_addr')
        amount = data_dic.get('amount')
        if not amount: 
            return jsonify({
                'status': 'fail',
                'reason': '이체할 코인 수량을 입력해 주세요.',
            })
        
        send_private_key = data_dic.get('private_key')
        if not send_private_key:
            return jsonify({
                'status': 'fail',
                'reason': '지갑 비밀키를 입력해 주세요.',
            })
        
        send_public_key = data_dic.get('public_key')
        if not send_public_key:
            return jsonify({
                'status': 'fail',
                'reason': '지갑 공개키를 입력해 주세요.',
            })
        
        recv_blockchain_addr = data_dic.get('recv_addr')
        if not recv_blockchain_addr:
            return jsonify({
                'status': 'fail',
                'reason': '받는 사람의 지갑 주소를 입력해 주세요.',
            })
        
        # 잔액 확인 수행
        blockchain_seed_node = f'http://{SEED_NODE_IP}:{PORT_MINIG}/coin_amount'
        json_data = {
            'blockchain_addr': send_blockchain_addr,
        }
        response = requests.post(blockchain_seed_node, json=json_data)
        data = response.json()
        current_amount = float(data['content'])
        print(f'transaction_amount: {amount}')
        print(f'current_amount: {current_amount}')

        if float(amount) > current_amount:
            return jsonify({
                'status': 'fail',
                'reason': '잔액이 부족합니다.',
            })


        # signature 생성
        signature = Wallet.generate_signature(
            send_blockchain_addr=send_blockchain_addr,
            recv_blockchain_addr=recv_blockchain_addr,
            send_private_key=send_private_key,
            amount=float(amount)
        )

        # 보낼 정보 만들어서 blockchain node에 전송
        json_data = {
            'send_blockchain_addr': send_blockchain_addr,
            'recv_blockchain_addr': recv_blockchain_addr,
            'amount': float(amount),
            'send_public_key': send_public_key,
            'signature': signature,
        }

        headers = {
            'X-CSRFToken': generate_csrf(),
        }

        # Seed Node에게 이웃들 정보 요청
        blockchain_seed_node = f'http://{SEED_NODE_IP}:{PORT_P2P}/neighbors'
        resp = requests.get(blockchain_seed_node)
        neighbors_dic = resp.json()
        print(f'neighbors_dic: {neighbors_dic}')

        for neighbor in neighbors_dic.values():
            ip, port = neighbor['ip'], neighbor['port']
            node = p2p_utils.check_node_exist(ip=ip, port=port)

            if not node:
                p2p_utils.add_new_node(ip, port)
            else:
                node.timestamp = time.time()
        
        # 활성화 된 blockchain node(mining node)를 찾아서 transaction 반영 요청
        neighbors_in_db = p2p_utils.get_all_nodes()
        for neighbor in neighbors_in_db:
            # 채굴 중인 노드인지 확인
            resp = requests.get(
                f'http://{neighbor.ip}:{PORT_MINIG}/is_mining_active'
            )
            resp_dic = resp.json()
            if resp_dic['status'] == 'mining_active':
                # 트랜잭션 반영 요청
                neighbor_url = f'http://{neighbor.ip}:{PORT_MINIG}/transactions/'
                response = requests.post(
                    url=neighbor_url,
                    json=json_data,
                    headers=headers
                )

                if response.status_code == 201:
                    # update timestamp of this node
                    neighbor.timestamp = time.time()
                    db.session.commit()
                    return jsonify({
                        'status': 'success',
                        'amount': amount,
                    }), 201
        return jsonify({
            'status': 'fail',
            'reason': '채굴 중인 노드가 없습니다.'
        }), 400

    return render_template(
        'transfer.html',
        form=form,
    )


@bp.route('/get_coin_amount/', methods=['GET'])
def get_coin_amount():
    blockchain_addr = request.args.get('blockchain_addr')

    if not blockchain_addr:
        return jsonify({
            'status': 'fail',
            'reason': '지갑 주소를 입력해 주세요.'
        }), 400
    
    seed_node_url = f'http://{SEED_NODE_IP}:{PORT_MINIG}/coin_amount'
    response = requests.post(url=seed_node_url, json={'blockchain_addr': blockchain_addr})
    data = response.json()
    if response.status_code == 201:
        return jsonify({
            'status': 'success',
            'amount': data.get('content')
        })
    # Seed Node로부터 정보를 받을 수 없는 경우
    else: 
        neighbor_in_db = p2p_utils.get_all_nodes()
        for neighbor in neighbor_in_db:
            if neighbor.ip == SEED_NODE_IP:
                continue
            # 채굴을 수행하고 있는 노드인지 확인하기
            resp = requests.get(
                f'http://{neighbor.ip}:{PORT_MINIG}/is_mining_active'
            )

            resp_dic = resp.json()

            if resp_dic['status'] == 'mining_active':
                neighbor_url = f'{neighbor.ip}:{PORT_MINIG}/coin_amount'
                response = requests.post(url=neighbor_url, json={'blockchain_addr': blockchain_addr})
                
                if response.status_code == 201:
                    data = response.json()
                    neighbor.timestamp = time.time()
                    db.session.commit()

                return jsonify({
                    'status': 'success',
                    'amount': data.get('content')
                }), 201
        return jsonify({
            'status': 'fail',
            'reason': '블록체인 서버와 연결에 실패했습니다.'
        }), 400