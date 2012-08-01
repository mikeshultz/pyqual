CREATE TABLE pq_database (
    database_id serial,
    name varchar,
    username varchar,
    password varchar,
    port varchar,
    hostname varchar,
    active boolean
);
CREATE TABLE pq_test_type (
    test_type_id serial,
    name varchar
);
CREATE TABLE pq_test (
    test_id serial, 
    name varchar,
    sql text, 
    python text,
    created timestamp, 
    modified timestamp, 
    lastrun timestamp,
    user_id int, 
    schedule_id int,
    test_type_id int,
    database_id int
);
CREATE TABLE pq_user (
    user_id serial, 
    username varchar, 
    email varchar,
    password varchar
);
CREATE TABLE pq_user_permission (
    user_permissions_id serial, 
    user_id int, 
    permission_id int
);
CREATE TABLE pq_permission (
    permission_id serial, 
    name varchar
);
CREATE TABLE pq_schedule (
    schedule_id serial, 
    name varchar
);

COPY pq_schedule (schedule_id, name) FROM stdin;
1	Hourly
2	Daily
3	Weekly
4	Monthly
\.

COPY pq_permission (permission_id, name) FROM stdin;
1	Read
2	Write
3	Super
\.

COPY pq_user (user_id, username, email, password) FROM stdin;
1	admin	example@email.com	asdf09asd0f9asdf09asdf09
\.

COPY pq_user_permission (user_permissions_id, user_id, permission_id) FROM stdin;
1	1	3
\.

COPY pq_test_type (test_type_id, name) FROM stdin;
1	SQL
2	SQL+Python
\.

COPY pq_test (test_id, name, sql, python, created, user_id, schedule_id, test_type_id, database_id) FROM stdin;
1	'Check for at least 1 super user'	'SELCT COUNT(user_id) FROM pq_user WHERE permission_id = 3;'	'if data[\'count\'] < 1:\n    return false'	'2000-01-01 00:00:01'	1	2	2	1
2	'Check for rules.'	'SELECT TRUE FROM pq_test LIMIT 1;'	''	'2001-01-01 00:00:01'	1	1	1	1
\.
