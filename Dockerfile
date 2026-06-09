# 1. Image de base légère avec Python 3.11
FROM python:3.11-slim

# 2. Définition du répertoire de travail dans le conteneur
WORKDIR /app

# 3. Installation des dépendances système (SQLite3 nécessaire pour ton DataLoader)
RUN apt-get update && apt-get install -y \
    build-essential \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 4. Copie et installation des requirements (optimisation du cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copie de l'intégralité des fichiers du projet
COPY . .

# 6. Rendre le script de démarrage exécutable
RUN chmod +x start.sh

# 7. Exposition du port Streamlit
EXPOSE 8501

# 8. Commande de lancement
CMD ["./start.sh"]