"""
Database models and session management for EcoTree.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date
import os

Base = declarative_base()


class Species(Base):
    __tablename__ = "species"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    scientific_name = Column(String(150))
    carbon_rate = Column(Float, default=0.25)   # kg CO2 / year / cm DBH (simplified)
    max_height = Column(Float)
    description = Column(Text, nullable=True)

    trees = relationship("Tree", back_populates="species")


class Tree(Base):
    __tablename__ = "trees"

    id = Column(Integer, primary_key=True)
    species_id = Column(Integer, ForeignKey("species.id"))
    common_name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    planting_date = Column(Date)
    dbh_cm = Column(Float)          # Diameter at Breast Height in cm
    height_m = Column(Float)
    health_score = Column(Float)
    health_status = Column(String(30))
    zone = Column(String(50))
    notes = Column(String(300))
    last_inspected = Column(Date, nullable=True)

    species = relationship("Species", back_populates="trees")


def get_engine(db_path="database/trees.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db(db_path="database/trees.db"):
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return engine


def get_session(db_path="database/trees.db"):
    engine = get_engine(db_path)
    Session = sessionmaker(bind=engine)
    return Session()
