#!/bin/bash

# Script pour configurer un environnement virtuel Python (utile pour manipuler django)

# Vérifie si Python est installé
if ! command -v python &> /dev/null; then
    echo "Python 3 n'est pas installé. Veuillez l'installer avant d'exécuter ce script."
    exit 1
fi

# Nom de l'environnement virtuel
VENV_NAME="venv"

# Vérifie si un fichier requirements.txt existe
if [ ! -f requirements.txt ]; then
    echo "Erreur : Le fichier requirements.txt est introuvable."
    exit 1
fi

echo "Création de l'environnement virtuel..."
python -m venv $VENV_NAME

if [ $? -ne 0 ]; then
    echo "Échec de la création de l'environnement virtuel."
    exit 1
fi

echo "Activation de l'environnement virtuel..."
# Activer l'environnement virtuel (dépend de la plateforme)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source $VENV_NAME/Scripts/activate
else
    source $VENV_NAME/bin/activate
fi

if [ $? -ne 0 ]; then
    echo "Échec de l'activation de l'environnement virtuel."
    exit 1
fi

echo "Installation des dépendances depuis requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Échec de l'installation des dépendances."
    deactivate
    exit 1
fi

echo "Vérification des dépendances installées..."
pip freeze

echo "Ajout de $VENV_NAME au fichier .gitignore..."
if [ ! -f .gitignore ]; then
    touch .gitignore
fi

if ! grep -q "^$VENV_NAME/$" .gitignore; then
    echo "$VENV_NAME/" >> .gitignore
    echo "Dossier $VENV_NAME ajouté à .gitignore."
else
    echo "Dossier $VENV_NAME est déjà dans .gitignore."
fi

echo "Désactivation de l'environnement virtuel..."
deactivate

echo "Configuration terminée avec succès !"
echo "Pour activer l'environnement virtuel, exécutez :"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "    source $VENV_NAME/Scripts/activate"
else
    echo "    source $VENV_NAME/bin/activate"
fi
echo "Pour désactiver, exécutez : deactivate"
