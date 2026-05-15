"""
Modele ORM : Indicateur
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Indicateur(Base):
    __tablename__ = "indicateur"

    idindicateur = Column("idindicateur", Integer, primary_key=True, autoincrement=True)
    nomindicateur = Column("nomindicateur", String(100))
    valeurindicateur = Column("valeurindicateur", Numeric(10, 2))
    annee = Column("annee", Integer)
    typeindicateur = Column("typeindicateur", String(100))

    idlycee = Column("idlycee", Integer, ForeignKey("lycee.idlycee"))
    idacademie = Column("idacademie", Integer, ForeignKey("academie.idacademie"))
    iddataset = Column("iddataset", Integer, ForeignKey("dataset.iddataset"))

    lycee = relationship("Lycee", back_populates="indicateurs")
    academie = relationship("Academie", back_populates="indicateurs")
    dataset = relationship("Dataset", back_populates="indicateurs")

    def __repr__(self) -> str:
        return f"<Indicateur(id={self.idindicateur}, nom='{self.nomindicateur}', valeur={self.valeurindicateur})>"