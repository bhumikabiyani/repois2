#!/bin/sh
pg_dump -i -h localhost -p 5432 -U udesarrollo -F c -b -v -f "poblado_tablas_produccion.backup" SGPA_db_produccion