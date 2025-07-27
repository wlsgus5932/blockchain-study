import os
import requests

from p2p.secret import CSRF_TOKEN_SECRET

BASE_DIR = os.path.dirname(__file__)

# SQLALCHEMY가 사용할 DB 주소
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'p2p.db')

# CSRF TOKEN SECRET KEY
SECRET_KEY = CSRF_TOKEN_SECRET

# 자신의 공인 IP를 확인하기 위해 사용하는 SERVICE PROVIDER
IP_CHECK_SERVICE_PROVIDER = 'https://checkip.amazonaws.com'

MY_PUBLIC_IP = requests.get(IP_CHECK_SERVICE_PROVIDER)

SEED_NODE_IP = MY_PUBLIC_IP.text.strip()

# P2P NETWORK PORT
PORT_P2P = '22901'