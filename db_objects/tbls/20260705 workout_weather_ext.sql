ALTER TABLE fitness.workout
    ADD COLUMN wind_direction_strt character varying(50),
    ADD COLUMN uv_index_strt integer,
    ADD COLUMN cloud_cover_strt numeric(8,2),
    ADD COLUMN weather_symbol_strt character varying(50),
    ADD COLUMN wind_direction_end character varying(50),
    ADD COLUMN uv_index_end integer,
    ADD COLUMN cloud_cover_end numeric(8,2),
    ADD COLUMN weather_symbol_end character varying(50)
;