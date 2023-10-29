#!/usr/bin/bash

. /home/mike/.env

echo $(date +%Y%m%d_%H%M%S)  > $logs/refresh_books.log
/usr/bin/curl -X GET https://mikebromberek.com/api/books/refresh/ -H "Accept: application/json" -H "Authorization: Bearer ${token}" >> $logs/refresh_books.log
echo $(date +%Y%m%d_%H%M%S) >> $logs/refresh_books.log

