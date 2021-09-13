--Get total miles, total time, and number of runs by week
WITH MILES_BY_WK AS (
    SELECT
      user_id
      , CASE type
          WHEN 'Indoor Running' THEN 'Running'
          WHEN 'Indoor Cycling' THEN 'Cycling'
          ELSE type
        END AS TYPE
      , date_trunc('WEEK',wrkt_dttm) DT_BY_WK
      , count(1) NBR
      --Time data types do not work with sum so convert from time to number of seconds
      , sum(dur_sec) TOT_SEC
      , sum(DIST_mi) TOT_DIST
    FROM fitness.workout
--    WHERE type in ('Running', 'Indoor Running')
    GROUP BY date_trunc('WEEK',wrkt_dttm), user_id
      , CASE type WHEN 'Indoor Running' THEN 'Running' WHEN 'Indoor Cycling' THEN 'Cycling' ELSE type END
)
SELECT CURR_WK.user_id
  , CURR_WK.type
  , curr_wk.dt_by_wk
  , curr_wk.nbr, curr_wk.tot_dist
  , round(((curr_wk.tot_dist / case prev_wk.tot_dist when 0 then 1 else prev_wk.tot_dist end) -1) * 100, 1) dist_delta_pct
  , curr_wk.TOT_SEC
  , round( ( ( (curr_wk.TOT_SEC::numeric / case prev_wk.TOT_SEC when 0 then 1 else prev_wk.TOT_SEC end) -1) * 100), 1) Tm_delta_pct
FROM MILES_BY_WK CURR_WK
LEFT OUTER JOIN MILES_BY_WK PREV_WK
  on CURR_WK.user_id = prev_wk.user_id
  and CURR_WK.type = prev_wk.type
  and CURR_WK.dt_by_wk - '1 weeks'::interval = prev_wk.dt_by_wk
ORDER BY curr_wk.DT_BY_WK desc
;
