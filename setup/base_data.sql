CREATE TABLE pq_database (
    database_id serial PRIMARY KEY,
    name varchar,
    username varchar,
    password varchar,
    port varchar,
    hostname varchar,
    active boolean
);
CREATE TABLE pq_test_type (
    test_type_id serial PRIMARY KEY,
    name varchar
);
CREATE TABLE pq_user (
    user_id serial PRIMARY KEY, 
    username varchar, 
    email varchar,
    password varchar
);
CREATE TABLE pq_user_session (
    user_session_id serial PRIMARY KEY,
    user_id int references pq_user(user_id),
    session_start timestamp,
    session_update timestamp
);
CREATE TABLE pq_permission (
    permission_id serial PRIMARY KEY, 
    name varchar
);
CREATE TABLE pq_user_permission (
    user_permission_id serial PRIMARY KEY, 
    user_id int references pq_user(user_id), 
    permission_id int references pq_permission(permission_id)
);
CREATE TABLE pq_schedule (
    schedule_id serial PRIMARY KEY, 
    name varchar
);
CREATE TABLE pq_test (
    test_id serial PRIMARY KEY, 
    name varchar,
    sql text, 
    python text,
    created timestamp, 
    modified timestamp, 
    lastrun timestamp,
    user_id int references pq_user(user_id), 
    schedule_id int references pq_schedule(schedule_id),
    test_type_id int references pq_test_type(test_type_id),
    database_id int references pq_database(database_id)
);
CREATE TABLE pq_log_type (
    log_type_id serial PRIMARY KEY,
    name varchar
);
CREATE TABLE pq_log (
    log_id serial PRIMARY KEY,
    log_type_id int references pq_log_type(log_type_id),
    test_id int references pq_test(test_id),
    message text
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
1	admin	example@email.com	'3c8486002eee6bafbd8967633ccdd05c38eec4823fae0b750f460a54f6c245b5'
\.

COPY pq_user_permission (user_permission_id, user_id, permission_id) FROM stdin;
1	1	3
\.

COPY pq_test_type (test_type_id, name) FROM stdin;
1	SQL
2	SQL+Python
\.

COPY pq_database (database_id, name, username, password, port, hostname, active) FROM stdin;
1	pyqual	pyqual	pyqual	5432	loclahost	true
\.

COPY pq_test (test_id, name, sql, python, created, user_id, schedule_id, test_type_id, database_id) FROM stdin;
1	Check for at least 1 super user	SELECT COUNT(user_id) FROM pq_user JOIN pq_user_permission perm USING (user_id) WHERE user_permission_id = 3;;	if data['count'] < 1:\n    return false	'2000-01-01 00:00:01'	1	2	2	1
2	Check for rules.	SELECT TRUE FROM pq_test LIMIT 1;		'2001-01-01 00:00:01'	1	1	1	1
3	Fail check	SELECT FALSE;	result = data[0][0]	'2001-01-01 00:00:01'	1	1	2	1
\.

COPY pq_log_type (log_type_id, name) FROM stdin;
1	Info
2	Warning
3	Error
\.

SELECT setval('pq_schedule_schedule_id_seq', (SELECT MAX(schedule_id) FROM pq_schedule)+1);
SELECT setval('pq_database_database_id_seq', (SELECT MAX(database_id) FROM pq_database)+1);
SELECT setval('pq_test_type_test_type_id_seq', (SELECT MAX(test_type_id) FROM pq_test_type)+1);
SELECT setval('pq_user_user_id_seq', (SELECT MAX(user_id) FROM pq_user)+1);
SELECT setval('pq_user_permission_user_permission_id_seq', (SELECT MAX(user_permission_id) FROM pq_user_permission)+1);
SELECT setval('pq_test_test_id_seq', (SELECT MAX(test_id) FROM pq_test)+1);
