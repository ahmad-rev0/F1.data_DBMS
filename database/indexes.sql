-- Extra covering indexes for search / join workloads (course performance section).

CREATE INDEX idx_race_year_round ON race (year, round_num);
CREATE INDEX idx_rr_race_position ON race_result (race_id, position_order);
CREATE INDEX idx_lap_race_lap ON lap_time (race_id, lap_num);
