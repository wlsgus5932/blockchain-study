rem 환경 변수 설정
set FLASK_APP=wallet
set FLASK_DEBUG=True

rem 가상 환경 활성화 (현재 디렉토리 기준으로 venv 폴더 안에 Scripts 폴더가 있다고 가정)
call .\venv\Scripts\activate.bat

rem Flask 서버 실행
flask run -h 0.0.0.0 -p 8080

rem 실행 후 창이 바로 닫히는 것을 방지
pause