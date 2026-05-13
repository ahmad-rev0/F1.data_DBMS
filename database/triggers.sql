-- Triggers (course bonus). Apply after schema.sql:
--   mysql ... formula1 < database/triggers.sql

DROP TRIGGER IF EXISTS trg_race_result_points_before_update;

DELIMITER //
CREATE TRIGGER trg_race_result_points_before_update
BEFORE UPDATE ON race_result
FOR EACH ROW
BEGIN
  IF NEW.points < 0 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'race_result.points must be >= 0';
  END IF;
END//
DELIMITER ;

DROP TRIGGER IF EXISTS trg_race_result_points_before_insert;

DELIMITER //
CREATE TRIGGER trg_race_result_points_before_insert
BEFORE INSERT ON race_result
FOR EACH ROW
BEGIN
  IF NEW.points < 0 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'race_result.points must be >= 0';
  END IF;
END//
DELIMITER ;
