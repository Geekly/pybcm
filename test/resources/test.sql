-- http://sqlfiddle.com/#!7/d7b11/2

create table price_guide (
  itemid text,
  color text,
  new_or_used text,
  primary key(itemid, color, new_or_used)
 );

insert into price_guide ( itemid, color, new_or_used )
values
('6587', '10', 'N'),
('6587', '9', 'N'),
('2356', '9', 'N'),
('2356', '1', 'N'),
('2356', '1', 'U'),
('2356', '10', 'N'),
('4589', '1', 'N'),
('3706', '11', 'U');

CREATE TEMPORARY TABLE pair (itemid_ INTEGER, color_ INTEGER, new_or_used_ INTEGER);
INSERT INTO pair (itemid_, color_, new_or_used_) VALUES ('6587', '9', 'N');
INSERT INTO pair (itemid_, color_, new_or_used_) VALUES ('2356', '1', 'U');

-- https://stackoverflow.com/questions/10525779/how-can-i-rewrite-a-multi-column-in-clause-to-work-on-sqlite
-- Select the following rows
-- ('6587', '9')
-- ('2356', '1')

-- the tuple should be unique
SELECT     price_guide.*
FROM       price_guide
INNER JOIN pair
        ON pair.itemid_ = price_guide.itemid
       AND pair.color_ = price_guide.color
       AND pair.new_or_used_ = price_guide.new_or_used;

SELECT    price_guide.*
FROM      price_guide
LEFT JOIN pair
        ON pair.itemid_ = price_guide.itemid
       AND pair.color_ = price_guide.color
       AND pair.new_or_used_ = price_guide.new_or_used
     WHERE pair.itemid_ IS NULL
        OR pair.color_ IS NULL
        OR pair.new_or_used_ is NULL;

-- ***************
--  select the entries in pair table that don't exist in price_guide
SELECT pair.*
from pair
left join price_guide
 ON pair.itemid_ = price_guide.itemid
       AND pair.color_ = price_guide.color
       AND pair.new_or_used_ = price_guide.new_or_used
       where price_guide.color is NULL
       OR price_guide.itemid is null
       or price_guide.new_or_used is null;
-- ***************