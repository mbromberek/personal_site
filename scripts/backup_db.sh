#!/usr/bin/bash

curr_date=$(date +%Y%m%d_%H%M%S)
echo $curr_date
cd /home/mike/backups
pg_dump -U mike mdb | gzip > mdb_dumpfile_$curr_date.gz
