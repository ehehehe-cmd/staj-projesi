from sqlalchemy import Column, Integer, Numeric, String, Date, TIMESTAMP, CheckConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class Slab(Base):
    __tablename__ = "slab"

    slab_id = Column(Integer, primary_key=True, autoincrement=True)
    kalinlik = Column(Numeric, nullable=False)
    genislik = Column(Numeric, nullable=False)
    sertlik = Column(Numeric, nullable=False)
    kalite_sinifi = Column(String, nullable=False)
    teslim_tarihi = Column(Date, nullable=False)
    sicaklik = Column(Numeric, nullable=False)
    durum = Column(String, nullable=False)
    olusturma_tarihi = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "durum IN ('depoda','sarj_oluyor','haddelemede','tamamlandi')",
            name="chk_slab_durum",
        ),
    )
