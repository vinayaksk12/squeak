SELECT * INTO OUTFILE '/tmp/2015_data.csv'   FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'   LINES TERMINATED BY '\n'   FROM company_old where incorporation_date like '2015%';
