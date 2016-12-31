-- request_log model

begin;
---------------------------------------------------------------------------

-- request_log --
--  This is the minimal request log table. 
--  	logged = timestamp
--  	email = user email, if any
--      request = request data

create table users (
  logged    timestamptz(6) default current_timestamp,
  session   json,
  request   json
);

---------------------------------------------------------------------------
commit;