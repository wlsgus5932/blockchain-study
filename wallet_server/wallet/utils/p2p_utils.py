from typing import List, Union
from wallet.models import MiningNode
from wallet import db
import time


def add_new_node(ip: str, port: str) -> None:
    '''새로운 노드를 DB에 추가'''
    node = MiningNode()

    node.ip=ip
    node.port=port
    node.timestamp=time.time()

    db.session.add(node)
    db.session.commit()


def check_node_exist(ip: str, port: str) -> Union[bool, MiningNode]:
    '''IP, PORT가 일치하는 노드가 있는지 확인'''
    print(f"Checking node with IP: {ip}, Port: {port}")
    node = MiningNode.query.filter(
        MiningNode.ip == ip,
        MiningNode.port == port
    ).first()

    if not node:
        return False
    return node


def get_all_nodes() -> List[MiningNode]:
    '''DB에서 최근 업데이트 된 순서대로 정렬된 모든 노드 가져오기'''
    return MiningNode.query.order_by(MiningNode.timestamp.desc()).all()