import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    connection = psycopg2.connect(
        user=os.getenv("postgres"),
        password=os.getenv("azerty"),
        host=os.getenv("localhost"),
        port=os.getenv("5432"),
        database=os.getenv("Projet_GL")
    )
    print("✅ Félicitations ! Python arrive à se connecter à PostgreSQL.")
    connection.close()
except Exception as e:
    print(f"❌ Échec : {e}")