CREATE SEQUENCE fitness.tag_id_seq START 1;

CREATE TABLE fitness.tag (
    id integer DEFAULT nextval('fitness.tag_id_seq'::regclass) PRIMARY KEY,
    user_id integer REFERENCES fitness."user"(id),
    nm character varying(50) NOT NULL,
    isrt_ts timestamp without time zone DEFAULT now()
);

-- Indices -------------------------------------------------------
CREATE UNIQUE INDEX tag_nm_idx ON fitness.tag(user_id int4_ops, nm text_ops);

CREATE TABLE fitness.workout_tag (
  workout_id integer REFERENCES fitness.workout(id),
  user_id integer REFERENCES fitness."user"(id),
  tag_id integer REFERENCES fitness.tag(id),
  isrt_ts timestamp without time zone DEFAULT now()
);

CREATE UNIQUE INDEX workout_tag_unique ON fitness.workout_tag(workout_id int4_ops, tag_id int4_ops);

insert into fitness.tag (user_id, nm) values (1, 'Negative Splits ✅');
insert into fitness.tag (user_id, nm) values (1, 'Positive Splits 👍');
insert into fitness.tag (user_id, nm) values (1, 'Even Splits 😮');

