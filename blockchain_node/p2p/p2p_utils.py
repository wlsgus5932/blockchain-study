from typing import Union
from p2p.models import MiningNode
from p2p import db
import time


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


def add_new_node(ip: str, port: str) -> None:
    '''새로운 노드를 DB에 추가'''
    node = MiningNode()

    node.ip=ip
    node.port=port
    node.timestamp=time.time()

    db.session.add(node)
    db.session.commit()