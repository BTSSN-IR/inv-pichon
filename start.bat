@echo off
waitress-serve --listen=0.0.0.0:5000 wsgi:app
pause