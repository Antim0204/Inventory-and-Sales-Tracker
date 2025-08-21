from sqlalchemy import (
    BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Numeric, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base

class FuelType(Base):
    __tablename__ = "fuel_types"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    price_per_litre: Mapped[str] = mapped_column(Numeric(10, 3), nullable=False)
    stock_litres: Mapped[str] = mapped_column(Numeric(14, 3), nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("price_per_litre >= 0", name="ck_ft_price_ge_0"),
        CheckConstraint("stock_litres >= 0", name="ck_ft_stock_ge_0"),
    )

    price_history: Mapped[list["FuelPriceHistory"]] = relationship(back_populates="fuel_type")
    sales: Mapped[list["Sale"]] = relationship(back_populates="fuel_type")


class FuelPriceHistory(Base):
    __tablename__ = "fuel_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fuel_type_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fuel_types.id", ondelete="CASCADE"), nullable=False)
    price_per_litre: Mapped[str] = mapped_column(Numeric(10, 3), nullable=False)
    valid_from: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    valid_to: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    fuel_type: Mapped[FuelType] = relationship(back_populates="price_history")

    __table_args__ = (
        CheckConstraint("price_per_litre >= 0", name="ck_fph_price_ge_0"),
        Index("idx_price_hist_fuel_type_id", "fuel_type_id"),
    )


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fuel_type_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fuel_types.id"), nullable=False)
    litres: Mapped[str] = mapped_column(Numeric(14, 3), nullable=False)
    price_at_sale: Mapped[str] = mapped_column(Numeric(10, 3), nullable=False)
    amount: Mapped[str] = mapped_column(Numeric(14, 2), nullable=False)
    sold_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    fuel_type: Mapped[FuelType] = relationship(back_populates="sales")

    __table_args__ = (
        CheckConstraint("litres > 0", name="ck_sales_litres_gt_0"),
        CheckConstraint("price_at_sale >= 0", name="ck_sales_price_ge_0"),
        CheckConstraint("amount >= 0", name="ck_sales_amount_ge_0"),
        Index("idx_sales_sold_at", "sold_at"),
        Index("idx_sales_fuel_type_id", "fuel_type_id"),
    )
