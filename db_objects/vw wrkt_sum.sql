-- CREATE or replace VIEW fitness.wrkt_sum AS
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
SELECT workout.user_id
   , 'Current Week'::text AS rng
   , workout.type
   , sum(workout.dur_sec) AS tot_sec
   , sum(workout.dist_mi) AS tot_dist
   , count(workout.id) AS nbr
   , min(workout.wrkt_dttm) as oldest_workout
   , max(workout.wrkt_dttm) as newest_workout
 FROM fitness.workout
 WHERE workout.wrkt_dttm::date >= date_trunc('week'::text, (current_date at time zone 'America/Chicago'))
   AND workout.wrkt_dttm::date < (date_trunc('week'::text, (current_date at time zone 'America/Chicago')) + '1 weeks'::interval)
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
 WHERE workout.wrkt_dttm::date > ((current_date at time zone 'America/Chicago') - '7 days'::interval)
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
 WHERE workout.wrkt_dttm::date > ((current_date at time zone 'America/Chicago') - '30 days'::interval)
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
 WHERE workout.wrkt_dttm::date >= date_trunc('month', (current_date at time zone 'America/Chicago'))
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
 WHERE workout.wrkt_dttm::date > ((current_date at time zone 'America/Chicago') - '365 days'::interval)
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
 WHERE workout.wrkt_dttm::date >= date_trunc('year', (current_date at time zone 'America/Chicago'))
 GROUP BY workout.user_id, workout.type
)wrkt_sum
GROUP BY rng, wrkt_sum.user_id
  , CASE wrkt_sum.type WHEN 'Indoor Running' THEN 'Running' WHEN 'Indoor Cycling' THEN 'Cycling' ELSE wrkt_sum.type END
;
