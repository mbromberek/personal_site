create sequence fitness.workout_id_point_seq start 1;

CREATE TABLE fitness.workout_point (
    id integer DEFAULT nextval('fitness.workout_id_point_seq'::regclass) PRIMARY KEY,
    user_id integer REFERENCES fitness."user"(id),
    workout_id integer REFERENCES fitness.workout(id),
	lat numeric,
	lon numeric,
	ts timestamp without time zone NOT NULL,
	delta_ts_sec numeric,
	dur_sec integer,
	hr numeric(8,2),
	cadence numeric,
	speed numeric,
	dist_m numeric,
	dist_mi numeric,
	dist_km numeric,
	delta_dist_mi numeric,
	delta_dist_km numeric,
	ele_up numeric,
	ele_down numeric,
	delta_ele_ft numeric,
	altitude_m numeric,
	altitude_ft numeric,
	lap integer NOT NULL,
	mile integer NOT NULL,
	kilometer integer NOT NULL,
	resume integer NOT NULL,
    isrt_ts timestamp without time zone NOT NULL DEFAULT now()
);

-- Indices -------------------------------------------------------

CREATE UNIQUE INDEX workout_point_pkey ON fitness.workout_point(id int4_ops);
CREATE INDEX wrkt_point_indx ON fitness.workout_point(user_id int4_ops,workout_id int4_ops);

GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA fitness TO app_role;
GRANT USAGE on SCHEMA fitness to app_role;
GRANT USAGE, SELECT ON ALL SEQUENCES in SCHEMA fitness TO app_role;
GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA fitness TO adm_role;
GRANT USAGE,CREATE on SCHEMA fitness to adm_role;
GRANT USAGE, SELECT ON ALL SEQUENCES in SCHEMA fitness TO adm_role;
