SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

DROP SCHEMA IF EXISTS `CleanData` ;
CREATE SCHEMA IF NOT EXISTS `CleanData` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci ;
USE `CleanData`;

-- -----------------------------------------------------
-- Table `CleanData`.`datasets`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `CleanData`.`datasets` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(45) NOT NULL ,
  `dataset_types_id` INT NOT NULL ,
  `channel_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `unique_name` (`name` ASC) ,
  UNIQUE INDEX `channel_id` (`channel_id` ASC) ,
  INDEX `type` (`dataset_types_id` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `CleanData`.`dataset_types`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `CleanData`.`dataset_types` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(45) NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `unique_name` (`name` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `CleanData`.`daily`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `CleanData`.`daily` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `date` DATE NOT NULL ,
  `value` DOUBLE NOT NULL ,
  `datasets_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `datasets_id` (`datasets_id` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `CleanData`.`temp_daily`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `CleanData`.`temp_daily` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `date` DATE NOT NULL ,
  `value` DOUBLE NOT NULL ,
  `datasets_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `datasets_id` (`datasets_id` ASC) )
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
