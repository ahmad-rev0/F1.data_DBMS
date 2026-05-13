-- Stored procedures (course bonus). Apply after schema.sql:
--   mysql ... formula1 < database/procedures.sql

DROP PROCEDURE IF EXISTS sp_driver_standings_end_of_year;

DELIMITER //
CREATE PROCEDURE sp_driver_standings_end_of_year(IN p_year SMALLINT)
BEGIN
  DECLARE v_last_race INT;

  SELECT MAX(race_id)
    INTO v_last_race
    FROM race
   WHERE year = p_year;

  SELECT
    ds.championship_position AS pos,
    d.driver_id,
    d.forename,
    d.surname,
    ds.points,
    ds.wins,
    r.name AS after_race
  FROM driver_standing ds
  JOIN driver d ON d.driver_id = ds.driver_id
  JOIN race r ON r.race_id = ds.race_id
 WHERE ds.race_id = v_last_race
 ORDER BY ds.championship_position ASC, d.surname ASC;
END//
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_constructor_points_by_year;

DELIMITER //
CREATE PROCEDURE sp_constructor_points_by_year(IN p_year SMALLINT)
BEGIN
  SELECT
    c.constructor_id,
    c.name,
    SUM(rr.points) AS total_points,
    COUNT(*) AS starts
  FROM race_result rr
  JOIN race ra ON ra.race_id = rr.race_id
  JOIN constructor c ON c.constructor_id = rr.constructor_id
 WHERE ra.year = p_year
 GROUP BY c.constructor_id, c.name
 ORDER BY total_points DESC;
END//
DELIMITER ;
