"""
Modele ORM : ResultatBac
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ResultatBac(Base):
    __tablename__ = "resultatbac"

    idresultat = Column("idresultat", Integer, primary_key=True, autoincrement=True)
    annee = Column("annee", Integer)
    voie = Column("voie", String(50))
    nbinscrits = Column("nbinscrits", Integer)
    nbadmis = Column("nbadmis", Integer)
    nbmentiontb = Column("nbmentiontb", Integer)
    nbmentionb = Column("nbmentionb", Integer)
    nbmentionab = Column("nbmentionab", Integer)
    nbrefuses = Column("nbrefuses", Integer)
    sexe = Column("sexe", String(1))
    nbadmissansmention = Column("nbadmissansmention", Integer)

    idacademie = Column("idacademie", Integer, ForeignKey("academie.idacademie"))

    academie = relationship("Academie", back_populates="resultats")

    def __repr__(self) -> str:
        return f"<ResultatBac(id={self.idresultat}, annee={self.annee}, voie='{self.voie}')>"