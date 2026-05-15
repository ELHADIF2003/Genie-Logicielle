"""
Modele ORM : Lycee
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Lycee(Base):
    __tablename__ = "lycee"

    idlycee = Column("idlycee", Integer, primary_key=True, autoincrement=True)
    nomlycee = Column("nomlycee", String(255))
    secteur = Column("secteur", String(50))
    typelycee = Column("typelycee", String(100))
    departement = Column("departement", String(5))
    ips = Column("ips", Numeric(5, 2))

    # Cles etrangeres
    idacademie = Column("idacademie", Integer, ForeignKey("academie.idacademie"))
    iddataset = Column("iddataset", Integer, ForeignKey("dataset.iddataset"))

    # Relations
    academie = relationship("Academie", back_populates="lycees")
    dataset = relationship("Dataset", back_populates="lycees")
    indicateurs = relationship("Indicateur", back_populates="lycee")

    def __repr__(self) -> str:
        return f"<Lycee(id={self.idlycee}, nom='{self.nomlycee}')>"