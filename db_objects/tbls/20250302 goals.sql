CREATE SEQUENCE fitness.goal_id_seq START 1;
CREATE SEQUENCE fitness.goal_type_id_seq START 1;

CREATE TABLE fitness.goal_type (
    id integer DEFAULT nextval('fitness.goal_type_id_seq'::regclass) PRIMARY KEY,
    nm character varying(50) NOT NULL,
    isrt_ts timestamp without time zone DEFAULT now()
);
CREATE UNIQUE INDEX goal_type_nm_idx ON fitness.tag(nm text_ops);

insert into fitness.goal_type(nm) values ('distance');
insert into fitness.goal_type(nm) values ('count');
insert into fitness.goal_type(nm) values ('time');

CREATE TABLE fitness.goal (
    id integer DEFAULT nextval('fitness.goal_id_seq'::regclass) PRIMARY KEY,
    user_id integer REFERENCES fitness."user"(id) NOT NULL,
    description character varying(100) NOT NULL,
    start_dt timestamp without time zone NOT NULL,
    end_dt timestamp without time zone NOT NULL,
    workout_type_id integer REFERENCES fitness.workout_type(id),
    goal_type_id integer NOT NULL REFERENCES fitness.goal_type(id),
    goal_total numeric(8,2) NOT NULL,
    ordr integer,
    is_active boolean NOT NULL DEFAULT true,
    isrt_ts timestamp without time zone DEFAULT now() NOT NULL
);

CREATE UNIQUE INDEX goal_description_idx ON fitness.goal(user_id int4_ops, description text_ops);
CREATE INDEX goal_order_idx ON fitness.goal(user_id int4_ops, ordr int4_ops);

create or replace view fitness.goal_results as
  SELECT goal.id, goal.user_id, goal.description, goal.start_dt, goal.end_dt
--    , goal.workout_type_id
    , workout_type_grp.grp as workout_type_grp
    , goal_type.nm as goal_type_nm, goal.goal_total
    , sum(workout.dist_mi) total_distance_miles
    , count(workout.id) total_workouts
    , sum(workout.dur_sec) total_duration_seconds
    , goal.ordr, goal.is_active
  FROM fitness.goal
  INNER JOIN fitness.goal_type
    on goal.goal_type_id = goal_type.id
  LEFT JOIN (
    select min(id) min_id, grp
    from fitness.workout_type
    group by grp
  ) workout_type_grp
    on goal.workout_type_id = workout_type_grp.min_id
  LEFT join fitness.workout_type
    on workout_type_grp.grp = workout_type.grp
  left join fitness.workout
    on (workout_type.id is null or workout_type.id = workout.type_id)
    and workout.user_id = goal.user_id
    and workout.wrkt_dttm between goal.start_dt and goal.end_dt
  group by goal.id, goal.user_id, goal.description, goal.start_dt, goal.end_dt
    , workout_type_grp.grp
    , goal_type.nm, goal.goal_total
    , goal.ordr
 ;


GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA FITNESS TO app_role;
GRANT USAGE on SCHEMA FITNESS to app_role;
GRANT USAGE, SELECT ON ALL SEQUENCES in SCHEMA FITNESS TO app_role;

insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr) values (1, 'Total 2025 miles', to_timestamp('2025-01-01','yyyy-mm-dd'), to_timestamp('2025-12-31 23:59:59','yyyy-mm-dd hh24:mi:ss'), null, 1, 2025.0, 0);

insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr) values (1, 'Run 130 miles in March', to_timestamp('2025-03-01','yyyy-mm-dd'), to_timestamp('2025-03-31 23:59:59','yyyy-mm-dd hh24:mi:ss'), 1, 1, 130.0, 1);
insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr) values (1, 'Strength 3 times per week', to_timestamp('2025-01-01','yyyy-mm-dd'), to_timestamp('2025-12-31 23:59:59','yyyy-mm-dd hh24:mi:ss'), 7, 2, 156, 4);
insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr, is_active) values (1, 'Run 100 miles in January', to_timestamp('2025-01-01','yyyy-mm-dd'), to_timestamp('2025-01-31 23:59:59','yyyy-mm-dd hh24:mi:ss'), 1, 1, 100, 2, false);
insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr) values (1, 'Run 1300 miles Mar to Dec', to_timestamp('2025-03-01','yyyy-mm-dd'), to_timestamp('2025-12-31 23:59:59','yyyy-mm-dd hh24:mi:ss'), 1, 1, 1300, 3);
insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr) values (1, 'Cycle 300 miles', to_timestamp('2025-01-01','yyyy-mm-dd'), to_timestamp('2025-12-31 23:59:59','yyyy-mm-dd hh24:mi:ss'), 3, 1, 300, 5);
insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr) values (1, 'Cycle 25 times', to_timestamp('2025-01-01','yyyy-mm-dd'), to_timestamp('2025-12-31 23:59:59','yyyy-mm-dd hh24:mi:ss'), 3, 2, 25, 6);
insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr) values (1, 'Cycle 40 miles in March', to_timestamp('2025-03-01','yyyy-mm-dd'), to_timestamp('2025-03-31 23:59:59','yyyy-mm-dd hh24:mi:ss'), 3, 1, 40, 7);
insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr) values (1, 'Run 1779 miles', to_timestamp('2025-01-01','yyyy-mm-dd'), to_timestamp('2025-12-31 23:59:59','yyyy-mm-dd hh24:mi:ss'), 1, 1, 1779.0, 9);

