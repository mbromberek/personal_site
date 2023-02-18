#!/usr/bin/bash

curr_date=$(date +%Y%m%d_%H%M%S)
echo $curr_date
cd /home/mike/backups
pg_dump -U mike mdb | gzip > mdb_dumpfile_$curr_date.gz
tar -zcvf wrkt_files_$curr_date.gz $HOME/wrkt_files
