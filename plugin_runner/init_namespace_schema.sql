-- Initialize a shared data namespace schema.
-- This is similar to init_plugin_schema.sql but includes the namespace_auth table
-- for authentication and excludes plugin-specific tables like django_content_type.

CREATE SCHEMA IF NOT EXISTS {namespace} AUTHORIZATION canvas_sdk_read_only;

-- Namespace authentication table
-- Stores hashed keys that grant access to this namespace
CREATE TABLE IF NOT EXISTS {namespace}.namespace_auth (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256 hash of the secret key
    access_level VARCHAR(10) NOT NULL CHECK (access_level IN ('read', 'read_write')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT  -- Optional description (e.g., "Plugin X read access")
);

-- Only allow SELECT on namespace_auth for the SDK role
-- Keys must be inserted by admin/owner, not by plugins
REVOKE ALL ON {namespace}.namespace_auth FROM canvas_sdk_read_only;
GRANT SELECT ON {namespace}.namespace_auth TO canvas_sdk_read_only;

-- Custom attribute storage (same as plugin schema)
CREATE TABLE IF NOT EXISTS {namespace}.custom_attribute (
    dbid SERIAL NOT NULL,
    content_type_id INT NOT NULL,
    object_id INT NOT NULL,
    name TEXT NOT NULL,
    text_value TEXT,
    date_value DATE,
    timestamp_value TIMESTAMP WITH TIME ZONE,
    int_value INT,
    decimal_value NUMERIC(20,10),
    bool_value BOOLEAN,
    json_value JSONB,
    PRIMARY KEY (content_type_id, object_id, name)
) PARTITION BY LIST(content_type_id);

CREATE INDEX IF NOT EXISTS custom_attribute_dbid_idx ON {namespace}.custom_attribute (dbid);
CREATE INDEX IF NOT EXISTS custom_attribute_text_idx ON {namespace}.custom_attribute (text_value) WHERE text_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_date_idx ON {namespace}.custom_attribute (date_value) WHERE date_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_timestamp_idx ON {namespace}.custom_attribute (timestamp_value) WHERE timestamp_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_int_idx ON {namespace}.custom_attribute (int_value) WHERE int_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_decimal_idx ON {namespace}.custom_attribute (decimal_value) WHERE decimal_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_bool_idx ON {namespace}.custom_attribute (bool_value) WHERE bool_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_json_idx ON {namespace}.custom_attribute USING GIN (json_value) WHERE json_value IS NOT NULL;

GRANT USAGE ON {namespace}.custom_attribute_dbid_seq TO canvas_sdk_read_only;
GRANT SELECT, INSERT, UPDATE, DELETE ON {namespace}.custom_attribute TO canvas_sdk_read_only;

-- Attribute hub for storing arbitrary key-value data
CREATE TABLE IF NOT EXISTS {namespace}.attribute_hub (
    dbid SERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    externally_exposable_id VARCHAR(100) NOT NULL,
    UNIQUE(type, externally_exposable_id)
);

GRANT USAGE ON {namespace}.attribute_hub_dbid_seq TO canvas_sdk_read_only;
GRANT SELECT, INSERT, UPDATE, DELETE ON {namespace}.attribute_hub TO canvas_sdk_read_only;

-- Django content type table for the namespace
CREATE TABLE IF NOT EXISTS {namespace}.django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE (app_label, model)
);

REVOKE ALL PRIVILEGES ON {namespace}.django_content_type FROM canvas_sdk_read_only;
GRANT SELECT ON {namespace}.django_content_type TO canvas_sdk_read_only;
