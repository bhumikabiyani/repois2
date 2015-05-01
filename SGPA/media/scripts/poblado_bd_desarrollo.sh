#! /bin/bash
pg_restore -i -h localhost -p 5432 -U udesarrollo -d SGPA_db -v "poblado_tablas_desarrollo.backup"