# 환경 변수 설정
export FLASK_APP=p2p
export FLASK_DEBUG=True

# 가상환경 활성화
source ./venv/bin/activate

# Flask 서버 실행
flask run -h 0.0.0.0 -p 22901

# 실행 후 종료 방지
read -p "Press Enter to exit..."