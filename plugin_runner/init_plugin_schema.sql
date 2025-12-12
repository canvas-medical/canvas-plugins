create schema if not exists {plugin_name} authorization canvas_sdk_read_only;

create table if not exists {plugin_name}.custom_attribute (
    dbid serial not null,
    content_type_id int not null,
    object_id int not null,
    name varchar(256) not null,
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
    type varchar(100) not null
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

grant select on {plugin_name}.django_content_type to canvas_sdk_read_only;

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


 do $$
  declare
      content_type_record record;
      partition_name text;
  begin
      -- loop through content types and create partitions
      for content_type_record in
          select id, app_label, model from {plugin_name}.django_content_type
      loop
          partition_name := '{plugin_name}.custom_attribute_' ||  content_type_record.app_label || '_' || content_type_record.model;
          execute format(
              'create table if not exists %I partition of {plugin_name}.custom_attribute for values in (%L)',
              partition_name,
              content_type_record.id
          );
      end loop;
  end
$$;
