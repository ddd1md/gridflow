CREATE TABLE locations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE substations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    location_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY(location_id) REFERENCES locations (id)
);

CREATE TABLE devices (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    substation_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY(substation_id) REFERENCES substations (id),
    CONSTRAINT type CHECK(type = 'meter'),
    CONSTRAINT status CHECK(status IN ('active', 'inactive'))
);

CREATE INDEX idx_location_id ON substations (location_id);
CREATE INDEX idx_substation_id ON devices (substation_id);