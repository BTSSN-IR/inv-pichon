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

## Impression des étiquettes

Le logiciel d'impression des étiquiettes est prévu pour une feuille d'étiquettes aux caractéristiques suivantes :
- Marge supérieure : 1cm
- Marge latérale : 0.47cm
- Longueur étiquette : 3.81cm
- Hauteur étiquette : 2.12cm
- Ecart horizontal entre étiquettes : 0.24cm
- Ecart vertical entre étiquettes : 0cm

[Exemple de modèle d'étiquettes](https://www.avery.fr/produit/etiquette-mini-l7651-100)

Pour utiliser le logiciel, il faut également avoir Microsoft Word installé sur le PC.

Pour imprimer les QR Codes sur ces étiquettes, il faut utiliser le logiciel "IT Inventory - QRCode Printer.exe" présent dans le dépôt.

### Aperçu du logiciel

![image](https://github.com/BTSSN-IR/inv-pichon/assets/61947142/fa803c46-c00c-4bab-91d0-03bb2067009f)

On peut choisir le type d'équipement pour lequel les codes seront imprimés, et combien de pages imprimer. Pour l'identifiant de départ, on choisit soit "1" soit la suite de la page précédemment imprimée.

__Note :__ *Lors de l'impression de plusieurs pages, les identifiants sont incrémentés automatiquement entre chaque page.*

Une fois la configuration terminée, le logiciel génère les étiquettes et ouvre le ou les fichiers Word automatiquement. Il ne reste plus qu'a les imprimer.
