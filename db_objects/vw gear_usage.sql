CREATE or replace VIEW fitness.gear_usage AS
SELECT gear.nm,
    count(wrkt.id) AS usage_count,
    coalesce(sum(wrkt.dist_mi),0) AS tot_dist,
    coalesce(sum(wrkt.dur_sec),0) AS tot_dur_sec,
    max(wrkt.wrkt_dttm) AS latest_workout,
    min(wrkt.wrkt_dttm) AS first_workout,
    gear.prchse_dt,
    gear.price,
    gear.retired,
    gear.confirmed,
    gear.type,
    gear.company,
    gear.id AS gear_id,
    gear.user_id
FROM fitness.gear gear
LEFT JOIN fitness.workout wrkt
  ON gear.id = wrkt.gear_id AND gear.user_id = wrkt.user_id
WHERE gear.type::text = ANY (ARRAY['Shoe'::character varying::text, 'Bike'::character varying::text])
GROUP BY wrkt.user_id, gear.nm, gear.id, gear.prchse_dt, gear.price, gear.retired, gear.confirmed, gear.type, gear.company
;

GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA fitness TO app_role;
GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA fitness TO adm_role;
