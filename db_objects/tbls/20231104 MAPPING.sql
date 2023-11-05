-- Create Schema
CREATE SCHEMA MAPPING;

-- Create Sequences
CREATE SEQUENCE mapping.route_id_seq START 1;

CREATE TABLE mapping.route (
  id integer DEFAULT nextval('mapping.route_id_seq'::regclass) PRIMARY KEY,
  user_id integer REFERENCES fitness."user"(id),
  name character varying(255) NOT NULL,
  dist numeric,
  dist_uom character varying(50) NOT NULL,
  public boolean default False,
  lat_start numeric,
  lon_start numeric,
  lat_end numeric,
  lon_end numeric,
  isrt_ts  timestamp without time zone DEFAULT now(),
  updt_ts  timestamp without time zone
); 
CREATE INDEX user_id_idx ON mapping.route(user_id int4_ops);

CREATE TABLE mapping.route_coord (
  route_id integer REFERENCES mapping."route"(id) NOT NULL,
  step integer NOT NULL, 
  user_id integer REFERENCES fitness."user"(id) NOT NULL,
  coordinates character varying(10485760) NOT NULL 
)
;
ALTER TABLE mapping.route_coord add primary key (route_id, step);
CREATE INDEX route_id_idx on mapping.route_coord(route_id);

GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA MAPPING TO app_role;
GRANT USAGE on SCHEMA MAPPING to app_role;
GRANT USAGE, SELECT ON ALL SEQUENCES in SCHEMA MAPPING TO app_role;


