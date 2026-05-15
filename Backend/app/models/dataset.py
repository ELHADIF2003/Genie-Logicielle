"""
Modele ORM : Dataset
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Dataset(Base):
    __tablename__ = "dataset"

    iddataset = Column("iddataset", Integer, primary_key=True, autoincrement=True)
    nomdataset = Column("nomdataset", String(255))
    source = Column("source", String(255))
    dateimportation = Column("dateimportation", DateTime, server_default=func.now())
    etat = Column("etat", String(50))

    lycees = relationship("Lycee", back_populates="dataset")
    indicateurs = relationship("Indicateur", back_populates="dataset")

    def __repr__(self) -> str:
        return f"<Dataset(id={self.iddataset}, nom='{self.nomdataset}')>"