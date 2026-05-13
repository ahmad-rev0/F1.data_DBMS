-- Apply on existing `formula1` databases that were created before `lap_reporting_fact` existed.
-- Run: mysql -u ... formula1 < database/patch_lap_reporting_fact.sql
-- Then re-run `python scripts/load_f1_csv.py` (or only the INSERT…SELECT section from that script).

CREATE TABLE IF NOT EXISTS lap_reporting_fact (
  fact_id BIGINT NOT NULL AUTO_INCREMENT,
  race_id INT NOT NULL,
  driver_id INT NOT NULL,
  lap_num SMALLINT NOT NULL,
  lap_position SMALLINT NOT NULL,
  lap_time VARCHAR(32) NOT NULL,
  milliseconds INT NOT NULL,
  season_year SMALLINT NOT NULL,
  grand_prix VARCHAR(256) NOT NULL,
  circuit_country VARCHAR(128) NOT NULL,
  driver_code VARCHAR(8) NULL,
  driver_surname VARCHAR(64) NOT NULL,
  PRIMARY KEY (fact_id),
  UNIQUE KEY uq_lap_reporting_lap (race_id, driver_id, lap_num),
  KEY idx_lrf_year_driver (season_year, driver_id),
  KEY idx_lrf_race_lap (race_id, lap_num),
  CONSTRAINT fk_lrf_race FOREIGN KEY (race_id) REFERENCES race (race_id),
  CONSTRAINT fk_lrf_driver FOREIGN KEY (driver_id) REFERENCES driver (driver_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
