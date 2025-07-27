import collections
import json
import hashlib

from mining.blockchain import BlockChain
from mining.models import Block,Transaction
from mining.config import MINING_DIFFICULTY

def sorted_dict_by_key(unsorted_dict: dict):
    # 메모리 키 값이 달라서 signature 검증 실패
    # return collections.OrderedDict(
    #         sorted(unsorted_dict.items()), key=lambda keys: keys[0]
    # )
    return dict(sorted(unsorted_dict.items()))


def get_blockchain():
    '''데이터베이스로부터 블록체인 정보 가져오기'''
    blockchain_exist = Block.query.all()
    if not blockchain_exist:
        blockchain = BlockChain()
        blockchain.create_genesis_block()
    
    return build_blockchain_json()


def build_blockchain_json() -> dict:
    '''DB로부터 모든 데이터를 추출'''
    blocks = Block.query.filter(
        Block.timestamp
    ).order_by(Block.timestamp)
    
    result_dic = {
        'chain': [],
        'transaction_pool': [],
    }

    for block in blocks:
        result_dic['chain'].append({
            'nonce': block.nonce,
            'prev_hash': block.prev_hash,
            'timestamp': block.timestamp,
            'transactions': get_transaction_list(block)
        })
    
        # 가장 최근(마지막) 생성된 블록일 경우 -> transaction_pool 생성
        last_block = Block.query.filter(
            Block.timestamp,
        ).order_by(Block.timestamp.desc()).first()
        result_dic['transaction_pool'] = get_transaction_list(last_block)

    return result_dic


def get_transaction_list(block: Block) -> list:
    # Block에 포함된 트랜잭션 리스트를 반환
    transaction_exist = Transaction.query.all()
    if not transaction_exist:
        return []
    
    transaction_list = []
    transactions = block.transactions

    for transaction in transactions:
        transaction_list.append({
            'send_blockchain_addr': transaction.send_addr,
            'recv_blockchain_addr': transaction.recv_addr,
            'amount': transaction.amount
        })
    return transaction_list


def hash(block: dict) -> str:
    sorted_block = json.dumps(block, sort_keys=True)
    return hashlib.sha256(sorted_block.encode()).hexdigest()


def calculate_total_amount(blockchain_addr: str) -> float:
    # 블록체인에 해당하는 계좌 총액 구하기
    total_amount = 0.0
    chain = get_blockchain()

    for block in chain.get('chain'):
        #체인으로 연결된 모든 블록 조사
        for transaction in block.get('transactions'):
            value = float(transaction.get('amount'))
            if blockchain_addr == transaction.get('send_blockchain_addr'):
                # 보낸 계좌
                total_amount -= value
            elif blockchain_addr == transaction.get('recv_blockchain_addr'):
                # 받은 계좌
                total_amount += value

    return total_amount
    

def get_prev_hash() -> str:
    '''DB에서 마지막 블록의 prev_hash를 찾아서 리턴'''
    prev_hash = Block.query.filter(
        Block.timestamp
    ).order_by(Block.timestamp.desc()).first().prev_hash

    return prev_hash


def valid_proof(
        challenge: int,
        prev_hash: str,
        transactions: list,
    ) -> bool:
    '''difficulty 개수만큼 일치하는지 확인하여 True/False 리턴'''
    # challenge + prev_hash + transaction_pool
    guess_block = sorted_dict_by_key(
        {
            'transactions': transactions,
            'nonce': challenge,
            'prev_hash': prev_hash
        }
    )

    guess_block_hash = hash(guess_block)
    print(f'guess_block_hash: {guess_block_hash}')
    result = guess_block_hash[:MINING_DIFFICULTY] == '0'*MINING_DIFFICULTY
    return result