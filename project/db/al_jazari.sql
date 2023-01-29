PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

CREATE TABLE categories(
    id integer not null unique primary key AUTOINCREMENT,
    name varchar(40) not null unique,
    img varchar(250) unique
);

CREATE TABLE models(
    id integer not null unique primary key AUTOINCREMENT,
    name varchar(40) not null unique,
    img varchar(250) unique,
    wrist boolean,
    motors integer,
    category_id integer not null,
    foreign key(category_id) references categories(id)
);

CREATE TABLE motors(
    id integer not null unique primary key AUTOINCREMENT,
    name varchar(40) not null unique,
    motor_model varchar(40),
    motor_num_in_the_model integer not null,
    model_id integer not null,
    foreign key(model_id) references models(id)
);

CREATE TABLE functions(
    id integer not null unique primary key AUTOINCREMENT,
    name varchar(40) not null unique,
    model_id integer not null,
    "default" boolean,
    foreign key(model_id) references models(id)
);

CREATE TABLE functions_moves(
    function_id integer not null,
    motor_id integer not null,
    move_num integer not null,
    wait_time_in_seconds numeric(4, 2) not null,
    primary key(function_id, move_num),
    foreign key(function_id) references functions(id),
    foreign key(motor_id) references motors(id)
);

insert into categories (name, img) values('Arm', 'imgs/models/1.png');

insert into models (name, img, wrist, motors, category_id) values('INMOOV Arm', 'imgs/models/1.png', '0', 5, 1);

insert into motors (name, motor_num_in_the_model, model_id) values
('Thumb', 0, 1),
('Index', 1, 1),
('Middle', 2, 1),
('Ring', 3, 1),
('Little', 4, 1);

insert into functions (name, model_id, "default") values ('Victory Sign', 1, 1);
 
insert into functions_moves (function_id, motor_id, move_num, wait_time_in_seconds) values
(1, 1, 1, 0),
(1, 4, 2, 0),
(1, 5, 3, 0);

COMMIT;