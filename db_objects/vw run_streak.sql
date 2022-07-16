--CREATE or replace VIEW fitness.run_streak AS
WITH workout_streaks as (
select distinct
  workout_curr.user_id
  , wrkt_type.nm type
  , workout_curr.wrkt_dttm::date as wrkt_dt
  , case
      when workout_prev_day.id is not null then 'Y'
      else 'N'
    end ran_prev_day
  , case
      when workout_next_day.id is not null then 'Y'
      else 'N'
    end ran_next_day
from fitness.workout workout_curr
inner join fitness.workout_type wrkt_type
  on workout_curr.type_id = wrkt_type.id
left outer join fitness.workout workout_prev_day
  on workout_curr.user_id = workout_prev_day.user_id
  and workout_curr.type_id = workout_prev_day.type_id
  and workout_curr.wrkt_dttm::date - INTERVAL '1 DAY' = workout_prev_day.wrkt_dttm::date
  and workout_prev_day.dist_mi >2
left outer join fitness.workout workout_next_day
  on workout_curr.user_id = workout_next_day.user_id
  and workout_curr.type_id = workout_next_day.type_id
  and workout_curr.wrkt_dttm::date + INTERVAL '1 DAY' = workout_next_day.wrkt_dttm::date
  and workout_next_day.dist_mi >2
where workout_curr.dist_mi >2
  and wrkt_type.grp = 'run'
)
select
  workout_streaks_start.user_id, workout_streaks_start.type
  , workout_streaks_start.wrkt_dt streak_start_dt
  , min(workout_streaks_end.wrkt_dt) streak_end_dt
  , min(workout_streaks_end.wrkt_dt) - workout_streaks_start.wrkt_dt +1 streak_days
from workout_streaks workout_streaks_start
left outer join (
  select user_id, type, wrkt_dt
  from workout_streaks
  where workout_streaks.ran_prev_day = 'Y'
    and workout_streaks.ran_next_day = 'N'
) workout_streaks_end
  on workout_streaks_start.user_id = workout_streaks_end.user_id
  and workout_streaks_start.type = workout_streaks_end.type
  and workout_streaks_end.wrkt_dt > workout_streaks_start.wrkt_dt
where workout_streaks_start.ran_prev_day = 'N'
  and workout_streaks_start.ran_next_day = 'Y'
group by workout_streaks_start.user_id, workout_streaks_start.type, workout_streaks_start.wrkt_dt
;
