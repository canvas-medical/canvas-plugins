create schema if not exists {plugin_name} authorization canvas_sdk_read_only;

create table if not exists {plugin_name}.custom_attribute (
    dbid serial not null,
    content_type_id int not null,
    object_id int not null,
    name text not null,
    text_value text,
    timestamp_value timestamp with time zone,
    int_value int,
    decimal_value numeric(20,10),
    bool_value boolean,
    json_value jsonb,
    primary key (content_type_id, object_id, name)
) partition by list(content_type_id);

create index on {plugin_name}.custom_attribute (dbid);
create index on {plugin_name}.custom_attribute (text_value) where text_value is not null;
create index on {plugin_name}.custom_attribute (timestamp_value) where timestamp_value is not null;
create index on {plugin_name}.custom_attribute (int_value) where int_value is not null;
create index on {plugin_name}.custom_attribute (decimal_value) where decimal_value is not null;
create index on {plugin_name}.custom_attribute (bool_value) where bool_value is not null;
create index on {plugin_name}.custom_attribute using gin (json_value) where json_value is not null;

grant usage on {plugin_name}.custom_attribute_dbid_seq to canvas_sdk_read_only;
grant select on {plugin_name}.custom_attribute to canvas_sdk_read_only;
grant insert, update, delete on {plugin_name}.custom_attribute to canvas_sdk_read_only;

create table if not exists {plugin_name}.attribute_hub (
    dbid serial primary key,
    type varchar(100) not null,
    externally_exposable_id varchar(100) not null
);

grant usage on {plugin_name}.attribute_hub_dbid_seq to canvas_sdk_read_only;
grant select on {plugin_name}.attribute_hub to canvas_sdk_read_only;
grant insert, update, delete on {plugin_name}.attribute_hub to canvas_sdk_read_only;


create table {plugin_name}.django_content_type
(
    id serial primary key,
    app_label varchar(100) not null,
    model varchar(100) not null,
    unique (app_label, model)
);

revoke all privileges on {plugin_name}.django_content_type from canvas_sdk_read_only;
grant select on {plugin_name}.django_content_type to canvas_sdk_read_only;
