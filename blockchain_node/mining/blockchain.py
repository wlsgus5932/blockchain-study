import time, requests
from typing import List

from mining import db
from mining.models import Block, Transaction
from mining.utils import blockchain_utils
from . import config

class BlockChain():
    # blockchain class
    def __init__(self) -> None:
        pass

    def create_genesis_block(self) -> bool:
        # genesis block creation
        block_exist = Block.query.all()
        if block_exist:
            print({
                'status': 'Falied to create genesis block',
                'error': 'Block(s) already exist'
            })
            return False
        
        genesis_block = Block(
            prev_hash=blockchain_utils.hash({}),
            nonce=0,
            timestamp=time.time(),
        )
        db.session.add(genesis_block)
        db.session.commit()

        return True
    

    def create_block(self, nonce: int, prev_hash: str = None) -> bool:
        # create a new block
        try:
            db.session.add(
                Block(
                    prev_hash=prev_hash,
                    nonce=nonce,
                    timestamp=time.time(),
                )
            )
            db.session.commit()
        except Exception as e:
            print('Failed to create block:', e)
            return False
    
        return True
        
    
    def valid_chain(self, chain: List[dict]) -> bool:
        ''' 블록체인 전체가 올바른지 검증하고 bool 리턴 '''
        prev_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            # prev_hash 검증
            if block['prev_hash'] != blockchain_utils.hash(prev_block):
                return False

            # nonce 검증
            if not blockchain_utils.valid_proof(
                challenge=int(block['nonce']), 
                prev_hash=prev_block['prev_hash'],
                transactions=prev_block['transactions']
            ):
                return False
            
            prev_block = block
            current_index += 1

        return True

    def resolve_conflict(self, ) -> bool:
        '''블록체인의 길이를 비교하여 업데이트'''
        longest_chain = None
        
        # 자신의 체인을 가장 긴 체인으로 설정
        my_chain = blockchain_utils.get_blockchain()['chain']
        max_length = len(my_chain)

        # 이웃 노드 확인
        url = f'http://{config.MY_PUBLIC_IP}:{config.PORT_P2P}/neighbors'
        resp = requests.get(url)
        neighbor_dic = resp.json()

        # 모든 이웃 노드들에게 blockchain 요청
        for neighbor in neighbor_dic.values():
            ip = neighbor['ip']

            if ip == config.MY_PUBLIC_IP:
                print('Not to resolve conflicts for self_node')
                continue

            neighbor_url = f'http://{ip}:{config.PORT_MINING}/get_chain'
            
            try:
                resp_get_chain = requests.get(neighbor_url)
                
                if resp_get_chain.status_code == 200:
                    blockchain = resp_get_chain.json()
                    chain = blockchain['chain']
                    chain_length = len(chain)
                    if chain_length > max_length and self.valid_chain(chain):
                        max_length = chain_length
                        longest_chain = chain
            except:
                print(f'Cannot connect to {neighbor_url}')

        # longest chain 존재하면 내 blockchain을 대체하고 True 리턴
        # 없다면 아무것도 하지않고 False
        if longest_chain:
            # 내 블록체인을 longest_chain으로 변경
            # 나의 모든 block 삭제
            blocks = Block.query.all()
            for block in blocks:
                db.session.delete(block)
                db.session.commit()
            
            # 나의 모든 transaction 삭제
            transactions = Transaction.query.all()
            for transaction in transactions:
                db.session.delete(transaction)
                db.session.commit()

            
            for block_in_chain in longest_chain:
                # 블록 생성
                block = Block()
                block.prev_hash = block_in_chain['prev_hash']
                block.nonce = block_in_chain['nonce']
                block.timestamp = block_in_chain['timestamp']

                db.session.add(block)
                db.session.commit()

                # 해당 블록의 transaction 정보 생성
                for transaction_in_block in block_in_chain['transactions']:
                    transaction = Transaction()
                    transaction.block_id = block.id
                    transaction.send_addr = transaction_in_block['send_addr']
                    transaction.recv_addr = transaction_in_block['recv_addr']
                    transaction.amount = transaction_in_block['amount']

                    db.session.add(transaction)
                    db.session.commit()
            print('resolve_conflict: chain replaced!!')
            return True
        
        return False
