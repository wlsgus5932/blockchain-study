# 환경 변수 설정
export FLASK_APP=wallet
export FLASK_DEBUG=True

# 가상환경 활성화
source ./venv/bin/activate

# Flask 서버 실행
flask run -h 0.0.0.0 -p 8080

# 실행 후 대기 (원래 pause 역할)
read -p "Press Enter to exit..."