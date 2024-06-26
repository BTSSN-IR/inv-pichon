@echo off
echo --- Inventaire IT Pichon ---
echo NE PAS FERMER CETTE FENETRE
flask run --host=0.0.0.0 --port=443 --cert=cert.pem --key=key.pem
pause
