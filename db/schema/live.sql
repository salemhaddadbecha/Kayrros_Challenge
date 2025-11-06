CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA IF NOT EXISTS live;

CREATE TYPE live.cluster_status AS ENUM (
    'DETECTED',
    'CONFIRMED',
    'FALSE_POSITIVE'
);

CREATE TABLE live.cluster (
    id SERIAL,
    status live.CLUSTER_STATUS NOT NULL DEFAULT 'DETECTED',
    PRIMARY KEY (id)
);
CREATE INDEX ON live.cluster (status);

CREATE TABLE live.hotspot (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensing_time TIMESTAMPTZ NOT NULL,
    geometry GEOMETRY (POINT, 4326) NOT NULL,
    source TEXT NOT NULL,
    cluster_id INTEGER,
    UNIQUE (sensing_time, geometry, source),
    FOREIGN KEY (cluster_id) REFERENCES live.cluster (
        id
    ) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX ON live.hotspot USING gist (geometry);
