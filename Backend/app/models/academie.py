"""
Modele ORM : Academie
"""
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from app.database import Base


class Academie(Base):
    __tablename__ = "academie"

    idacademie = Column("idacademie", Integer, primary_key=True, autoincrement=True)
    nomacademie = Column("nomacademie", String(100))
    regionacademie = Column("regionacademie", String(100))
    ipsmoyen = Column("ipsmoyen", Numeric(5, 2))

    # Relations inverses (un academie -> plusieurs lycees / resultats / indicateurs)
    lycees = relationship("Lycee", back_populates="academie")
    resultats = relationship("ResultatBac", back_populates="academie")
    indicateurs = relationship("Indicateur", back_populates="academie")

    def __repr__(self) -> str:
        return f"<Academie(id={self.idacademie}, nom='{self.nomacademie}')>"