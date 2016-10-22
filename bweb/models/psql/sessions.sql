-- sessions table used for database sessions

begin;
---------------------------------------------------------------------------

create table sessions (
  id        varchar primary key,
  data      jsonb,
  inserted  timestamptz(0) default current_timestamp,
  updated   timestamptz(0) default current_timestamp
);

---------------------------------------------------------------------------
commit;
