@echo off
waitress-serve --listen=0.0.0.0:5000 --url_scheme:'https' wsgi:app 
pause