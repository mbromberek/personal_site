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
    start_dt date NOT NULL,
    end_dt date NOT NULL,
    workout_type_id integer REFERENCES fitness.workout_type(id),
    goal_type_id integer NOT NULL REFERENCES fitness.goal_type(id),
    goal_total numeric(8,2) NOT NULL,
    ordr integer,
    is_active boolean NOT NULL DEFAULT true,
    isrt_ts timestamp without time zone DEFAULT now() NOT NULL
);

CREATE UNIQUE INDEX goal_description_idx ON fitness.goal(user_id int4_ops, description text_ops);
CREATE INDEX goal_order_idx ON fitness.goal(user_id int4_ops, ordr int4_ops);

insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr) values (1, 'Total 2025 miles', to_date('2025-01-01','yyyy-mm-dd'), to_date('2025-12-31 23:59:59','yyyy-mm-dd hh24:mi:ss'), null, 1, 2025.0, 0);

create or replace view fitness.goal_results as
  SELECT goal.id, goal.user_id, goal.description, goal.start_dt, goal.end_dt
    , goal.workout_type_id, workout_type_grp.grp
    , goal_type.nm, goal.goal_total
    , sum(workout.dist_mi) total_distance_miles
    , count(workout.id) total_workouts
    , sum(workout.dur_sec) total_duration_seconds
    , goal.ordr
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
    , goal.workout_type_id, workout_type_grp.grp
    , goal_type.nm, goal.goal_total
    , goal.ordr
;


GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA FITNESS TO app_role;
GRANT USAGE on SCHEMA FITNESS to app_role;
GRANT USAGE, SELECT ON ALL SEQUENCES in SCHEMA FITNESS TO app_role;

insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr) values (1, 'Run 130 miles in March', to_date('2025-03-01','yyyy-mm-dd'), to_date('2025-31-31','yyyy-mm-dd hh24:mi:ss'), 1, 1, 130.0, 1);
insert into fitness.goal(user_id, description, start_dt, end_dt, workout_type_id, goal_type_id, goal_total, ordr) values (1, 'Strength 3 times per week', to_date('2025-01-01','yyyy-mm-dd'), to_date('2025-12-31','yyyy-mm-dd hh24:mi:ss'), 1, 7, 156, 4);


"Strength 3 times per week", dateStart: yearStart, dateEnd: yearEnd, workoutType: .strength, goalType: .count, goalTotal: 156, order:4

