create schema if not exists {plugin_name} authorization canvas_sdk_read_only;

create table if not exists {plugin_name}.custom_attribute (
    dbid serial primary key,
    content_type_id int,
    object_id int,
    name text,
    text_value text,
    timestamp_value timestamp with time zone,
    int_value int,
    float_value double precision,
    bool_value boolean,
    json_value jsonb,
    unique (content_type_id, object_id, name)
);

grant usage on {plugin_name}.custom_attribute_dbid_seq to canvas_sdk_read_only;
grant select on {plugin_name}.custom_attribute to canvas_sdk_read_only;
grant insert, update, delete on {plugin_name}.custom_attribute to canvas_sdk_read_only;

create table if not exists {plugin_name}.attribute_hub (
    dbid serial primary key,
    type varchar(255) not null
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

insert into {plugin_name}.django_content_type (app_label, model) values
('v1', 'allergyintolerance'),
('v1', 'appointment'),
('v1', 'assessment'),
('v1', 'attributehub'),
('v1', 'banneralert'),
('v1', 'billinglineitem'),
('v1', 'businessline'),
('v1', 'calendar'),
('v1', 'canvasuser'),
('v1', 'careteammembership'),
('v1', 'careteamrole'),
('v1', 'chargedescriptionmaster'),
('v1', 'claim'),
('v1', 'claimdiagnosiscode'),
('v1', 'claimlineitem'),
('v1', 'command'),
('v1', 'compoundmedication'),
('v1', 'condition'),
('v1', 'coverage'),
('v1', 'customattribute'),
('v1', 'detectedissue'),
('v1', 'device'),
('v1', 'discount'),
('v1', 'encounter'),
('v1', 'facility'),
('v1', 'goal'),
('v1', 'imagingorder'),
('v1', 'immunization'),
('v1', 'invoice'),
('v1', 'laborder'),
('v1', 'medication'),
('v1', 'medicationstatement'),
('v1', 'message'),
('v1', 'note'),
('v1', 'observation'),
('v1', 'organization'),
('v1', 'patient'),
('v1', 'patientconsent'),
('v1', 'paymentcollection'),
('v1', 'payorspecificcharge'),
('v1', 'practicelocation'),
('v1', 'protocolcurrent'),
('v1', 'protocoloverride'),
('v1', 'questionnaire'),
('v1', 'referral'),
('v1', 'serviceprovider'),
('v1', 'staff'),
('v1', 'stopmedicationevent'),
('v1', 'task'),
('v1', 'team')
;

grant select on {plugin_name}.django_content_type to canvas_sdk_read_only;
