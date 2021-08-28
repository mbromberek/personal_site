--CREATE or replace VIEW fitness.wrkt_sum AS
SELECT
  rng
  , CASE wrkt_sum.type
      WHEN 'Indoor Running' THEN 'Running'
      WHEN 'Indoor Cycling' THEN 'Cycling'
      ELSE wrkt_sum.type
    END AS TYPE
  , wrkt_sum.user_id
  , sum(tot_sec) as tot_sec
  , sum(tot_dist) as tot_dist
  , sum(nbr) AS nbr
  , min(oldest_workout) AS oldest_workout
  , max(newest_workout) AS newest_workout
FROM (
SELECT workout.user_id,
   'Current Week'::text AS rng,
   workout.type
   , sum(workout.dur_sec) AS tot_sec
   , sum(workout.dist_mi) AS tot_dist
   , count(workout.id) AS nbr
   , min(workout.wrkt_dttm) as oldest_workout
   , max(workout.wrkt_dttm) as newest_workout
 FROM fitness.workout
 WHERE workout.wrkt_dttm >= date_trunc('week'::text, 'now'::text::date::timestamp with time zone) AND workout.wrkt_dttm <= (date_trunc('week'::text, 'now'::text::date::timestamp with time zone) + '6 days'::interval)
 GROUP BY workout.user_id, workout.type
UNION ALL
 SELECT workout.user_id,
    'Past 7 days'::text AS rng,
    workout.type
   , sum(workout.dur_sec) AS tot_sec
   , sum(workout.dist_mi) AS tot_dist
   , count(workout.id) AS nbr
   , min(workout.wrkt_dttm) as oldest_workout
   , max(workout.wrkt_dttm) as newest_workout
 FROM fitness.workout
 WHERE workout.wrkt_dttm > ('now'::text::date - 7)
 GROUP BY workout.user_id, workout.type
UNION ALL
 SELECT workout.user_id,
   'Past 30 days'::text AS rng,
   workout.type
   , sum(workout.dur_sec) AS tot_sec
   , sum(workout.dist_mi) AS tot_dist
   , count(workout.id) AS nbr
   , min(workout.wrkt_dttm) as oldest_workout
   , max(workout.wrkt_dttm) as newest_workout
 FROM fitness.workout
 WHERE workout.wrkt_dttm > ('now'::text::date - 30)
 GROUP BY workout.user_id, workout.type
UNION ALL
 SELECT workout.user_id,
   'Current Month'::text AS rng
   , workout.type
   , sum(workout.dur_sec) AS tot_sec
   , sum(workout.dist_mi) AS tot_dist
   , count(workout.id) AS nbr
   , min(workout.wrkt_dttm) as oldest_workout
   , max(workout.wrkt_dttm) as newest_workout
 FROM fitness.workout
 WHERE workout.wrkt_dttm >= date_trunc('month'::text, 'now'::text::date::timestamp with time zone)
 GROUP BY workout.user_id, workout.type

UNION ALL
 SELECT workout.user_id,
   'Past 365 days'::text AS rng
   , workout.type
   , sum(workout.dur_sec) AS tot_sec
   , sum(workout.dist_mi) AS tot_dist
   , count(workout.id) AS nbr
   , min(workout.wrkt_dttm) as oldest_workout
   , max(workout.wrkt_dttm) as newest_workout
 FROM fitness.workout
 WHERE workout.wrkt_dttm > ('now'::text::date - 365)
 GROUP BY workout.user_id, workout.type

UNION ALL
 SELECT workout.user_id,
   'Current Year'::text AS rng
   , workout.type
   , sum(workout.dur_sec) AS tot_sec
   , sum(workout.dist_mi) AS tot_dist
   , count(workout.id) AS nbr
   , min(workout.wrkt_dttm) as oldest_workout
   , max(workout.wrkt_dttm) as newest_workout
 FROM fitness.workout
 WHERE workout.wrkt_dttm >= date_trunc('year'::text, 'now'::text::date::timestamp without time zone)
 GROUP BY workout.user_id, workout.type
)wrkt_sum
GROUP BY rng, wrkt_sum.user_id
  , CASE wrkt_sum.type WHEN 'Indoor Running' THEN 'Running' WHEN 'Indoor Cycling' THEN 'Cycling' ELSE wrkt_sum.type END
;
