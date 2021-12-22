--CREATE or replace VIEW fitness.yrly_mileage AS
--Get total miles, total time, and number of workouts by year
WITH MILES_BY_YR AS (
    SELECT
      user_id
      , CASE type
          WHEN 'Indoor Running' THEN 'Running'
          WHEN 'Indoor Cycling' THEN 'Cycling'
          ELSE type
        END AS TYPE
      , date_trunc('YEAR',wrkt_dttm) DT_BY_YR
      , count(1) NBR
      , sum(dur_sec) TOT_SEC
      , sum(DIST_mi) TOT_DIST
    FROM fitness.workout
    GROUP BY date_trunc('YEAR',wrkt_dttm), user_id
      , CASE type WHEN 'Indoor Running' THEN 'Running' WHEN 'Indoor Cycling' THEN 'Cycling' ELSE type END
)
SELECT CURR_YR.user_id
  , CURR_YR.type
  , CURR_YR.dt_by_yr
  , CURR_YR.nbr, CURR_YR.tot_dist
  , round(((CURR_YR.tot_dist / case PREV_YR.tot_dist when 0 then 1 else PREV_YR.tot_dist end) -1) * 100, 1) dist_delta_pct
  , CURR_YR.TOT_SEC
  , round( ( ( (CURR_YR.TOT_SEC::numeric / case PREV_YR.TOT_SEC when 0 then 1 else PREV_YR.TOT_SEC end) -1) * 100), 1) tm_delta_pct
FROM MILES_BY_YR CURR_YR
LEFT OUTER JOIN MILES_BY_YR PREV_YR
  on CURR_YR.user_id = PREV_YR.user_id
  and CURR_YR.type = PREV_YR.type
  and CURR_YR.dt_by_yr - '1 years'::interval = PREV_YR.dt_by_yr
order by CURR_YR.user_id, curr_yr.type, curr_yr.dt_by_yr
;
