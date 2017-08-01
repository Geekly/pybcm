CREATE TABLE `set` (
	`itemid`	TEXT,
	`description`	INTEGER,
	`est_price`	NUMERIC,
	PRIMARY KEY(`itemid`)
);
SELECT type,name,sql,tbl_name FROM sqlite_master UNION SELECT type,name,sql,tbl_name FROM sqlite_temp_master;
SELECT COUNT(*) FROM (SELECT `_rowid_`,* FROM `set` ORDER BY `_rowid_` ASC);
SELECT `_rowid_`,* FROM `set` ORDER BY `_rowid_` ASC LIMIT 0, 50000;
CREATE TABLE `part` (
	`itemid`	TEXT NOT NULL,
	`name`	TEXT,
	PRIMARY KEY(`itemid`)
);
SELECT type,name,sql,tbl_name FROM sqlite_master UNION SELECT type,name,sql,tbl_name FROM sqlite_temp_master;
SELECT COUNT(*) FROM (SELECT `_rowid_`,* FROM `part` ORDER BY `_rowid_` ASC);
SELECT `_rowid_`,* FROM `part` ORDER BY `_rowid_` ASC LIMIT 0, 50000;
CREATE TABLE `part_price` (
	`itemid`	TEXT,
	`color`	TEXT,
	`new_or_used`	TEXT,
	`avg_price`	REAL,
	`max_price`	REAL,
	`min_price`	REAL,
	`qty_avg_price`	REAL,
	`unit_quantity`	INTEGER,
	`total_quantity`	INTEGER,
	PRIMARY KEY(`itemid`,`color`,`new_or_used`)
);
SELECT type,name,sql,tbl_name FROM sqlite_master UNION SELECT type,name,sql,tbl_name FROM sqlite_temp_master;
SELECT COUNT(*) FROM (SELECT `_rowid_`,* FROM `part` ORDER BY `_rowid_` ASC);
SELECT `_rowid_`,* FROM `part` ORDER BY `_rowid_` ASC LIMIT 0, 50000;