insert into {namespace}.django_content_type (app_label, model) values
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
('v1', 'eligibilitysummary'),
('v1', 'encounter'),
('v1', 'externalevent'),
('v1', 'facility'),
('v1', 'goal'),
('v1', 'imagingorder'),
('v1', 'imagingreport'),
('v1', 'imagingreview'),
('v1', 'immunization'),
('v1', 'installmentplan'),
('v1', 'integrationtask'),
('v1', 'interview'),
('v1', 'invoice'),
('v1', 'laborder'),
('v1', 'labreport'),
('v1', 'labreview'),
('v1', 'labtest'),
('v1', 'labvalue'),
('v1', 'letter'),
('v1', 'medication'),
('v1', 'medicationstatement'),
('v1', 'message'),
('v1', 'note'),
('v1', 'notetype'),
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
('v1', 'referralreport'),
('v1', 'referralreview'),
('v1', 'serviceprovider'),
('v1', 'staff'),
('v1', 'stopmedicationevent'),
('v1', 'task'),
('v1', 'team'),
('v1', 'transactor'),
('v1', 'uncategorizedclinicaldocument')
on conflict do nothing
;


 do $$
  declare
      content_type_record record;
      partition_name text;
  begin
      -- loop through content types and create partitions
      for content_type_record in
          select id, app_label, model from {namespace}.django_content_type
      loop
          execute('set search_path to {namespace};');
          partition_name := '{namespace}.custom_attribute_' ||  content_type_record.app_label || '_' || content_type_record.model;
          execute format(
              'create table if not exists %I partition of {namespace}.custom_attribute for values in (%L)',
              partition_name,
              content_type_record.id
          );
          execute('set search_path to public;');
      end loop;
  end
$$;
