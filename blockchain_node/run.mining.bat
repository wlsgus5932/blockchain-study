rem 환경 변수 설정
set FLASK_APP=mining
set FLASK_DEBUG=True

rem 가상 환경 활성화
call .\venv\Scripts\activate.bat

rem Flask 서버 실행
flask run -h 0.0.0.0 -p 7001

rem 실행 후 창이 바로 닫히는 것을 방지
pause