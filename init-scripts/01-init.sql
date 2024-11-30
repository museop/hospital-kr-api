-- Switch to the target database
\c mydb;

-- Enable PostGIS extension
CREATE EXTENSION postgis;

-- Create the table
CREATE TABLE medical_institutions (
    id SERIAL PRIMARY KEY,
    address VARCHAR(255),          -- Address
    zipcode VARCHAR(20),           -- Zip code
    name VARCHAR(255),             -- Institution name
    last_modified_date DATE,       -- Last modified date
    updated_date DATE,             -- Updated date
    department_content TEXT,       -- Department description
    geom GEOMETRY(Point, 4326)     -- Longitude/Latitude in WGS 84
);

-- Enable trgm extension
CREATE EXTENSION pg_trgm;

-- Create GIN index
CREATE INDEX idx_trgm_medical_institutions ON medical_institutions USING gin (
    (name || ' ' || address || ' ' || department_content) gin_trgm_ops
);

