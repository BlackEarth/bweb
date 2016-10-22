-- users model

begin;
---------------------------------------------------------------------------

-- users --
--  This is the minimal users table. Add other fields that you would like.
--  	email = user id
--  	pwd is hashed (use the strongest one-way hash you can)
--  	verification is optional

create table users (
  email       varchar primary key,
  pwd         varchar,
  registered  timestamptz(0) default current_timestamp,
  verified    timestamptz(0)
);

---------------------------------------------------------------------------
commit;