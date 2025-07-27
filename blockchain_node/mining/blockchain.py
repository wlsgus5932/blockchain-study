import time

from mining import db
from mining.models import Block
from mining.utils import blockchain_utils

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
        