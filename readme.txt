# Système d'Analyse de Données

Application web Django pour l'analyse et la visualisation de données CSV.

## Applications

- `upload` : Gestion du téléchargement des fichiers CSV
- `data_preview` : Affichage et exploration des données
- `statistics` : Analyse statistique des données
- `visualization` : Création de graphiques avec Plotly Express

## Installation

1. Cloner le projet

git clone <url-du-projet>


2. Installer les dépendances

pip install -r requirements.txt


3. Lancer les migrations

python manage.py makemigrations
python manage.py migrate


4. Démarrer le serveur



## Fonctionnalités

- Téléchargement et lecture de fichiers CSV
- Affichage des données par ligne et colonne
- Calculs statistiques sur les données
- Visualisation interactive avec Plotly Express
  (Note : on a utiliser Plotly Express)

## Dépendances principales

- Django
- Pandas
- Plotly Express