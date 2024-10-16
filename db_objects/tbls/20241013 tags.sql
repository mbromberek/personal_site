CREATE SEQUENCE fitness.tag_id_seq START 1;

CREATE TABLE fitness.tag (
    id integer DEFAULT nextval('fitness.tag_id_seq'::regclass) PRIMARY KEY,
    user_id integer REFERENCES fitness."user"(id) NOT NULL,
    nm character varying(50) NOT NULL,
    isrt_ts timestamp without time zone DEFAULT now() NOT NULL
);

-- Indices -------------------------------------------------------
CREATE UNIQUE INDEX tag_nm_idx ON fitness.tag(user_id int4_ops, nm text_ops);

CREATE TABLE fitness.workout_tag (
  workout_id integer REFERENCES fitness.workout(id) NOT NULL,
  user_id integer REFERENCES fitness."user"(id) NOT NULL,
  tag_id integer REFERENCES fitness.tag(id) NOT NULL,
  isrt_ts timestamp without time zone DEFAULT now() NOT NULL
);

CREATE UNIQUE INDEX workout_tag_unique ON fitness.workout_tag(workout_id int4_ops, tag_id int4_ops);

insert into fitness.tag (user_id, nm) values (1, 'Negative Splits ✅');
insert into fitness.tag (user_id, nm) values (1, 'Positive Splits 👍');
insert into fitness.tag (user_id, nm) values (1, 'Even Splits 😮');


GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA FITNESS TO app_role;
GRANT USAGE on SCHEMA FITNESS to app_role;
GRANT USAGE, SELECT ON ALL SEQUENCES in SCHEMA FITNESS TO app_role;


