#! /bin/bash
createdb -h localhost -p 5432 -U udesarrollo -E UTF8 SGPA_db

pg_restore -i -h localhost -p 5432 -U udesarrollo -d SGPA_db -v "poblado_tablas_desarrollo.backup"