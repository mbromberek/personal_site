create table fitness.user_setting (
	user_id integer REFERENCES fitness."user"(id) PRIMARY KEY,
	shoe_mile_warning numeric(8),
	shoe_mile_max numeric(8),
	shoe_min_brkin_ct numeric(8),
	updt_ts timestamp without time zone default now(),
	isrt_ts timestamp without time zone default now()
)
;

GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA fitness TO app_role;
GRANT USAGE on SCHEMA fitness to app_role;
GRANT USAGE, SELECT ON ALL SEQUENCES in SCHEMA fitness TO app_role;
GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA fitness TO adm_role;
GRANT USAGE,CREATE on SCHEMA fitness to adm_role;
GRANT USAGE, SELECT ON ALL SEQUENCES in SCHEMA fitness TO adm_role;

commit;