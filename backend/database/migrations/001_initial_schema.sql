-- Palete Studio Database Schema
-- Version: 001
-- Description: Initial schema for restaurants, menu items, and photos

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table 1: Restaurants
-- Stores restaurant information and workflow status
CREATE TABLE restaurants (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  owner_user_id   TEXT NOT NULL,
  name            TEXT NOT NULL,
  cuisine_type    TEXT,
  status          TEXT DEFAULT 'draft',  -- draft, processing, ready, exported
  created_at      TIMESTAMP DEFAULT NOW(),
  updated_at      TIMESTAMP DEFAULT NOW()
);

-- Table 2: Photos
-- Stores uploaded and generated food photos
CREATE TABLE photos (
  id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  restaurant_id    UUID REFERENCES restaurants(id) ON DELETE CASCADE,
  filename         TEXT NOT NULL,
  storage_path     TEXT NOT NULL,  -- Supabase Storage URL
  thumbnail_url    TEXT,
  source           TEXT DEFAULT 'uploaded',  -- 'uploaded', 'generated'
  generation_model TEXT,  -- 'dall-e-3' if generated
  uploaded_at      TIMESTAMP DEFAULT NOW()
);

-- Table 3: Menu Items
-- Stores menu items with matching and enhancement data
CREATE TABLE menu_items (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  restaurant_id     UUID REFERENCES restaurants(id) ON DELETE CASCADE,
  name              TEXT NOT NULL,
  description       TEXT,
  price             DECIMAL(10,2),
  category          TEXT,
  matched_photo_id  UUID REFERENCES photos(id),
  match_confidence  INTEGER CHECK (match_confidence >= 0 AND match_confidence <= 100),
  match_reasoning   TEXT,
  photo_source      TEXT DEFAULT 'none',  -- 'uploaded', 'generated', 'none'
  enhanced_photo_url TEXT,  -- Supabase Storage URL for enhanced photo
  quality_score      INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
  quality_details    JSONB,  -- Stores full PhotoQualityAssessment JSON
  needs_review       BOOLEAN DEFAULT FALSE,
  created_at         TIMESTAMP DEFAULT NOW(),
  updated_at         TIMESTAMP DEFAULT NOW()
);

-- Indexes for query performance
CREATE INDEX idx_restaurants_owner ON restaurants(owner_user_id);
CREATE INDEX idx_restaurants_status ON restaurants(status);
CREATE INDEX idx_photos_restaurant ON photos(restaurant_id);
CREATE INDEX idx_photos_source ON photos(source);
CREATE INDEX idx_menu_items_restaurant ON menu_items(restaurant_id);
CREATE INDEX idx_menu_items_needs_review ON menu_items(needs_review);
CREATE INDEX idx_menu_items_photo_source ON menu_items(photo_source);

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;
ALTER TABLE photos ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_items ENABLE ROW LEVEL SECURITY;

-- Restaurants: Users can only access their own restaurants
CREATE POLICY "Users can view own restaurants"
  ON restaurants FOR SELECT
  USING (auth.uid()::text = owner_user_id);

CREATE POLICY "Users can insert own restaurants"
  ON restaurants FOR INSERT
  WITH CHECK (auth.uid()::text = owner_user_id);

CREATE POLICY "Users can update own restaurants"
  ON restaurants FOR UPDATE
  USING (auth.uid()::text = owner_user_id);

CREATE POLICY "Users can delete own restaurants"
  ON restaurants FOR DELETE
  USING (auth.uid()::text = owner_user_id);

-- Photos: Users can access photos for their own restaurants
CREATE POLICY "Users can view own photos"
  ON photos FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM restaurants
      WHERE restaurants.id = photos.restaurant_id
      AND restaurants.owner_user_id = auth.uid()::text
    )
  );

CREATE POLICY "Users can insert own photos"
  ON photos FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM restaurants
      WHERE restaurants.id = photos.restaurant_id
      AND restaurants.owner_user_id = auth.uid()::text
    )
  );

CREATE POLICY "Users can update own photos"
  ON photos FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM restaurants
      WHERE restaurants.id = photos.restaurant_id
      AND restaurants.owner_user_id = auth.uid()::text
    )
  );

CREATE POLICY "Users can delete own photos"
  ON photos FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM restaurants
      WHERE restaurants.id = photos.restaurant_id
      AND restaurants.owner_user_id = auth.uid()::text
    )
  );

-- Menu Items: Users can access menu items for their own restaurants
CREATE POLICY "Users can view own menu items"
  ON menu_items FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM restaurants
      WHERE restaurants.id = menu_items.restaurant_id
      AND restaurants.owner_user_id = auth.uid()::text
    )
  );

CREATE POLICY "Users can insert own menu items"
  ON menu_items FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM restaurants
      WHERE restaurants.id = menu_items.restaurant_id
      AND restaurants.owner_user_id = auth.uid()::text
    )
  );

CREATE POLICY "Users can update own menu items"
  ON menu_items FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM restaurants
      WHERE restaurants.id = menu_items.restaurant_id
      AND restaurants.owner_user_id = auth.uid()::text
    )
  );

CREATE POLICY "Users can delete own menu items"
  ON menu_items FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM restaurants
      WHERE restaurants.id = menu_items.restaurant_id
      AND restaurants.owner_user_id = auth.uid()::text
    )
  );

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to automatically update updated_at
CREATE TRIGGER update_restaurants_updated_at
  BEFORE UPDATE ON restaurants
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_menu_items_updated_at
  BEFORE UPDATE ON menu_items
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE restaurants IS 'Stores restaurant information and workflow status';
COMMENT ON TABLE photos IS 'Stores uploaded and AI-generated food photos';
COMMENT ON TABLE menu_items IS 'Stores menu items with AI matching and enhancement data';
COMMENT ON COLUMN restaurants.status IS 'Workflow status: draft, processing, ready, exported';
COMMENT ON COLUMN photos.source IS 'Photo origin: uploaded, generated';
COMMENT ON COLUMN menu_items.photo_source IS 'Where the photo came from: uploaded, generated, none';
COMMENT ON COLUMN menu_items.quality_details IS 'Full PhotoQualityAssessment JSON from vision service';
