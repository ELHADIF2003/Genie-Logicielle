"""
Modele ORM : Utilisateur
"""
from sqlalchemy import Column, Integer, String
from app.database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    idutilisateur = Column("idutilisateur", Integer, primary_key=True, autoincrement=True)
    nomutilisateur = Column("nomutilisateur", String(100))
    emailutilisateur = Column("emailutilisateur", String(150), unique=True)
    motdepassehash = Column("motdepassehash", String(255))
    role = Column("role", String(20), default="utilisateur")

    def __repr__(self) -> str:
        return f"<Utilisateur(id={self.idutilisateur}, email='{self.emailutilisateur}', role='{self.role}')>"