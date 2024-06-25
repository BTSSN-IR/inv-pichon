# Inventaire IT Pichon / SAMSON

## A propos

Nous avons développé ce projet dans le cadre de nos études en BTS SN pour l'année 2023-2024. Ce projet a pour but de permettre au service informatique de l'entreprise de recenser facilement et rapidement les différents équipements informatiques présents au sein de l'entreprise. Voici une liste des fonctionnalités présentes :

* Ajout, modification et suppression des éléments du système
* Affichage de tous les équipements reliés à un utilisateur
* Etiquettes apposées sur les équipements pour leur identification
* Modification rapide par scan de QR Code sur l'étiquette

## Notice d'installation

### Etape 1
Installer la dernière version de Python à l’aide du site web [https://www.python.org/downloads/](https://www.python.org/downloads/). A l’installation, ne pas oublier de cocher la case permettant d’ajouter python au PATH de Windows. 
![image](https://github.com/BTSSN-IR/inv-pichon/assets/61947142/bb4b4ae5-dc5b-47cd-b8f2-521c9b1225b8)

### Etape 2 
Sur le serveur, cloner le dépôt Github à l’aide de la commande « git clone https://github.com/BTSSN-IR/inv-pichon.git ». 

### Etape 3 
Installer les bibliothèques nécessaires au fonctionnement du programme à l’aide du fichier requirements.txt. 
Pour cela, exécuter la commande « pip install -r requirements.txt »  

### Etape 4 
Si le serveur est sous Windows, lancer le script « start.bat » En double-cliquant dessus depuis l’explorateur de fichiers. 
Si le serveur est sous Linux, ajouter les droits d’exécution au script « run.sh » grâce à la commande « chmod +x run.sh ». Puis lancer le script à l’aide de la commande « ./run.sh ». 

### Lancement automatique au démarrage du serveur

#### Serveur Windows

Créer un raccourci du fichier "start.bat" et le déplacer vers le dossier "C:\Users\\%username%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup". Le programme se lancera automatiquement au démarrage du serveur, au moment de la connexion utilisateur.
