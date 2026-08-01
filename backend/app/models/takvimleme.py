from sqlalchemy import Column, Integer, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class Takvimleme(Base):
    __tablename__ = "takvimleme"

    takvimleme_id = Column(Integer, primary_key=True, autoincrement=True)
    olusturma_tarihi = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    aktif_mi = Column(Boolean, nullable=False, default=False)
