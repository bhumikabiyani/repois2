 #! /bin/bash
pg_restore -i -h localhost -p 5432 -U udesarrollo -d SGPA_db_produccion -v "poblado_tablas_produccion.backup"