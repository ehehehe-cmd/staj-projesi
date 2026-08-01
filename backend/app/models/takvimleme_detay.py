from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.core.database import Base


class TakvimlemeDetay(Base):
    __tablename__ = "takvimleme_detay"

    takvimleme_detay_id = Column(Integer, primary_key=True, autoincrement=True)
    takvimleme_id = Column(Integer, ForeignKey("takvimleme.takvimleme_id"), nullable=False)
    slab_id = Column(Integer, ForeignKey("slab.slab_id"), nullable=False)
    sira_no = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("takvimleme_id", "sira_no", name="uq_takvimleme_slab_sira"),
    )
