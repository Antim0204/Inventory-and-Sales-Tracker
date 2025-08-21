-- sql/001_init.sql
-- Fuel types: current price + current stock (fast reads)
CREATE TABLE IF NOT EXISTS fuel_types (
  id               BIGSERIAL PRIMARY KEY,
  name             TEXT NOT NULL UNIQUE,
  price_per_litre  NUMERIC(10,3) NOT NULL CHECK (price_per_litre >= 0),
  stock_litres     NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK (stock_litres >= 0),
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Price history (optional audit, helpful for reporting)
CREATE TABLE IF NOT EXISTS fuel_price_history (
  id               BIGSERIAL PRIMARY KEY,
  fuel_type_id     BIGINT NOT NULL REFERENCES fuel_types(id) ON DELETE CASCADE,
  price_per_litre  NUMERIC(10,3) NOT NULL CHECK (price_per_litre >= 0),
  valid_from       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  valid_to         TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_price_hist_fuel_type_id ON fuel_price_history(fuel_type_id);

-- Sales (immutable facts)
CREATE TABLE IF NOT EXISTS sales (
  id               BIGSERIAL PRIMARY KEY,
  fuel_type_id     BIGINT NOT NULL REFERENCES fuel_types(id),
  litres           NUMERIC(14,3) NOT NULL CHECK (litres > 0),
  price_at_sale    NUMERIC(10,3) NOT NULL CHECK (price_at_sale >= 0),
  amount           NUMERIC(14,2) NOT NULL CHECK (amount >= 0),
  sold_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sales_sold_at ON sales(sold_at);
CREATE INDEX IF NOT EXISTS idx_sales_fuel_type_id ON sales(fuel_type_id);
