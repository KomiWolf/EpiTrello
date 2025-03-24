# EpiTrello

EpiTrello est un projet web visant à recréer les fonctionnalités principales de Trello, une application de gestion de tâches en mode Kanban. Il permet aux utilisateurs de créer des tableaux, des listes et des cartes, ainsi que d'organiser leurs tâches de manière intuitive.

## ✨ Fonctionnalités

- Création et gestion de tableaux
- Ajout et organisation de listes sur un tableau
- Création et déplacement de cartes entre les listes
- Attribution d'étiquettes, de descriptions et de dates de fin aux cartes
- Authentification via OAuth2
- Sauvegarde des données dans une base MariaDB
- Déploiement via Docker

## 🛠️ Technologies utilisées

- **Frontend** : ReactJS
- **Backend** : Python avec FastAPI et Uvicorn
- **Base de données** : MySQL avec MariaDB
- **Authentification** : OAuth2
- **Déploiement** : Docker

## 🚀 Installation et utilisation

### Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Node.js** (LTS)
- **npm** (fourni avec Node.js)
- **Python 3**
- **MySQL / MariaDB** (avec un utilisateur et une base de données prêts)
- **Docker** (si vous souhaitez l'utiliser pour exécuter les services)

### Installation

#### 1️⃣ Cloner le projet
```bash
git clone https://github.com/KomiWolf/epitrello.git
cd epitrello
```

#### 2️⃣ Configuration du Backend
```bash
cd server
pip install -r requirements.txt
```

Configuration du .env de la base de donnée:
```ìni
MYSQL_USER=[non-root-user]
MYSQL_DATABASE=[database-to-create]
MYSQL_PASSWORD=[password-for-non-root-user]
MYSQL_ROOT_PASSWORD=[password-for-root-account]
```

Configuration du .env du MinIO S3:
```ini
MINIO_ROOT_USER=[username-for-the-account]
MINIO_ROOT_PASSWORD=[password-for-the-account]
```

Configuration du serveur:
```ini
# Database login details
DB_HOST=[host]
DB_PORT=[port]
DB_USER=[non-root-user]
DB_PASSWORD=[non-root-user-passwd]
DB_DATABASE=[database-of-interest]

# Bucket login details
MINIO_HOST=[the-url-to-the-minio-instance]
MINIO_PORT=[the-port-to-the-minio-instance]
MINIO_ROOT_USER=[username-for-the-account]
MINIO_ROOT_PASSWORD=[password-for-the-account]

# Docker settings (Optional, this will only override the default container settings) (These are only updated when the docker compose is building)
LAUNCH_SERVER_ON_BOOT=[boolean-value-if-you-wish-to-start-the-server-when-the-container-starts] # default: True
DEBUG=[boolean-value-if-you-wish-to-start-the-server-in-debug-mode]                             #default: False
PORT=[the-port-you-wish-the-server-will-listen-on]                                              # default: 5000, please update rebind in the docker compose if you change this value
HOST=[the-range-of-ip-s-the-server-is-listening-on]                                             #The default is '0.0.0.0' meaning all ip's

# Server Oauth variables
REDIRECT_URI=[the-redirect-url-once-the-user-is-connected]
```

#### 3️⃣ Configuration du Frontend
```bash
cd web
npm install
```

Configuration du frontend web:
```ini
REACT_APP_UNSPLASH_ACCESS_KEY="The access key to be able to use Unsplash"
```

#### 4️⃣ Déploiement du projet
Si le projet n'a jamais été lancé en local:
```bash
sudo docker compose up --build
```

Si le projet a déjà été lancé en local:
```bash
sudo docker compose up
```
