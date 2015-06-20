 #! /bin/bash
createdb -h localhost -p 5432 -U udesarrollo -E UTF8 SGPA_db_produccion

pg_restore -i -h localhost -p 5432 -U udesarrollo -d SGPA_db_produccion -v "poblado_tablas_produccion.backup"