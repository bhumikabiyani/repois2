#!/bin/bash
psql -h localhost -t -d SGPA_db_produccion -U udesarrollo -c "SELECT
'DROP TABLE ' || n.nspname || '.' || c.relname || ' CASCADE;'
FROM pg_catalog.pg_class c
LEFT JOIN pg_catalog.pg_user u ON u.usesysid = c.relowner
LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r','')
AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
AND pg_catalog.pg_table_is_visible(c.oid)
ORDER BY 1;" > droptables

psql -h localhost -d SGPA_db_produccion -U udesarrollo -f droptables