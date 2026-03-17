-- Initialize a shared data namespace schema.

CREATE SCHEMA IF NOT EXISTS {namespace};
GRANT USAGE, CREATE ON SCHEMA {namespace} TO canvas_sdk_read_only;

-- Namespace authentication table
-- Stores hashed keys that grant access to this namespace
CREATE TABLE IF NOT EXISTS {namespace}.namespace_auth (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256 hash of the secret key
    access_level VARCHAR(10) NOT NULL CHECK (access_level IN ('read', 'read_write')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT
);

-- Only allow SELECT on namespace_auth for the SDK role
-- Keys must be inserted by admin/owner, not by plugins
GRANT SELECT ON {namespace}.namespace_auth TO canvas_sdk_read_only;

-- Attribute hub for storing arbitrary key-value data
CREATE TABLE IF NOT EXISTS {namespace}.attribute_hub (
    dbid BIGSERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    id VARCHAR(100) NOT NULL,
    UNIQUE(type, id)
);

-- REVOKE ALL PRIVILEGES ON {namespace}.attribute_hub FROM canvas_sdk_read_only;
GRANT USAGE ON {namespace}.attribute_hub_dbid_seq TO canvas_sdk_read_only;
GRANT SELECT, INSERT, UPDATE, DELETE ON {namespace}.attribute_hub TO canvas_sdk_read_only;

-- Custom attribute storage (FK to attribute_hub)
CREATE TABLE IF NOT EXISTS {namespace}.custom_attribute (
    dbid BIGSERIAL NOT NULL,
    hub_id BIGINT NOT NULL REFERENCES {namespace}.attribute_hub(dbid),
    name TEXT NOT NULL,
    text_value TEXT,
    date_value DATE,
    timestamp_value TIMESTAMP WITH TIME ZONE,
    int_value INT,
    decimal_value NUMERIC(20,10),
    bool_value BOOLEAN,
    json_value JSONB,
    PRIMARY KEY (hub_id, name)
);

CREATE INDEX IF NOT EXISTS custom_attribute_dbid_idx ON {namespace}.custom_attribute (dbid);
CREATE INDEX IF NOT EXISTS custom_attribute_text_idx ON {namespace}.custom_attribute (text_value) WHERE text_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_date_idx ON {namespace}.custom_attribute (date_value) WHERE date_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_timestamp_idx ON {namespace}.custom_attribute (timestamp_value) WHERE timestamp_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_int_idx ON {namespace}.custom_attribute (int_value) WHERE int_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_decimal_idx ON {namespace}.custom_attribute (decimal_value) WHERE decimal_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_bool_idx ON {namespace}.custom_attribute (bool_value) WHERE bool_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS custom_attribute_json_idx ON {namespace}.custom_attribute USING GIN (json_value) WHERE json_value IS NOT NULL;

GRANT USAGE ON {namespace}.custom_attribute_dbid_seq TO canvas_sdk_read_only;
-- REVOKE ALL PRIVILEGES ON {namespace}.custom_attribute FROM canvas_sdk_read_only;
GRANT SELECT, INSERT, UPDATE, DELETE ON {namespace}.custom_attribute TO canvas_sdk_read_only;

-- Migration readiness sentinel. The schema manager inserts a row per plugin
-- after all DDL completes; non-schema-manager containers check the
-- (plugin_name, models_hash) pair to verify the namespace is ready for the
-- current version of each plugin's models.
CREATE TABLE IF NOT EXISTS {namespace}.schema_version (
    plugin_name VARCHAR(255) NOT NULL,
    models_hash VARCHAR(64),
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (plugin_name)
);

-- Idempotent migration: add plugin_name column if missing (for namespaces
-- created before this column existed).
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = '{namespace}'
          AND table_name = 'schema_version'
          AND column_name = 'plugin_name'
    ) THEN
        ALTER TABLE {namespace}.schema_version ADD COLUMN plugin_name VARCHAR(255);
        -- Clear old single-row data; the schema manager will re-insert per-plugin rows.
        DELETE FROM {namespace}.schema_version;
        ALTER TABLE {namespace}.schema_version ALTER COLUMN plugin_name SET NOT NULL;
        ALTER TABLE {namespace}.schema_version ADD CONSTRAINT schema_version_plugin_name_key UNIQUE (plugin_name);
    END IF;
END $$;

GRANT SELECT ON {namespace}.schema_version TO canvas_sdk_read_only;
