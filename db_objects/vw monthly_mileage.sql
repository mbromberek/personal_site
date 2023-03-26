--CREATE or replace VIEW fitness.moly_mileage AS
--Get total miles, total time, and number of runs by month
WITH MILES_BY_MO AS (
    SELECT
      user_id
      , CASE wrkt_type.nm
          WHEN 'Indoor Running' THEN 'Running'
          WHEN 'Indoor Cycling' THEN 'Cycling'
          ELSE wrkt_type.nm
        END AS TYPE
      , date_trunc('MONTH',wrkt_dttm) DT_BY_MO
      , count(1) NBR
      --Time data types do not work with sum so convert from time to number of seconds
      , sum(dur_sec) TOT_SEC
      , sum(DIST_mi) TOT_DIST
    FROM fitness.workout
    inner join fitness.workout_type wrkt_type
      on workout.type_id = wrkt_type.id
    GROUP BY date_trunc('MONTH',wrkt_dttm), user_id
      , CASE wrkt_type.nm WHEN 'Indoor Running' THEN 'Running' WHEN 'Indoor Cycling' THEN 'Cycling' ELSE wrkt_type.nm END
)
SELECT CURR_MO.user_id
  , CURR_MO.type
  , CURR_MO.dt_by_mo
  , CURR_MO.nbr, CURR_MO.tot_dist
  , round(((CURR_MO.tot_dist / case PREV_MO.tot_dist when 0 then 1 else PREV_MO.tot_dist end) -1) * 100, 1) dist_delta_pct
  , CURR_MO.TOT_SEC
  , round( ( ( (CURR_MO.TOT_SEC::numeric / case PREV_MO.TOT_SEC when 0 then 1 else PREV_MO.TOT_SEC end) -1) * 100), 1) tm_delta_pct
FROM MILES_BY_MO CURR_MO
LEFT OUTER JOIN MILES_BY_MO PREV_MO
  on CURR_MO.user_id = PREV_MO.user_id
  and CURR_MO.type = PREV_MO.type
  and CURR_MO.dt_by_mo - '1 months'::interval = PREV_MO.dt_by_mo
;
