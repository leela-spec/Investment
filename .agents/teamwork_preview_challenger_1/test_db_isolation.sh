#!/bin/bash
ROLES="priv_openproject_app priv_paperless_app priv_firefly_app comm_openproject_app comm_paperless_app comm_firefly_app"
DBS="priv_openproject priv_paperless priv_firefly comm_openproject comm_paperless comm_firefly"

allowed_count=0
denied_count=0
other_count=0

for r in $ROLES; do
  for d in $DBS; do
    if docker exec ki-basis-shared-postgres psql -U "$r" -d "$d" -c "SELECT 1;" >/dev/null 2>&1; then
      echo "RESULT: $r -> $d: ALLOWED"
      ((allowed_count++))
    else
      err=$(docker exec ki-basis-shared-postgres psql -U "$r" -d "$d" -c "SELECT 1;" 2>&1 | tr '\n' ' ')
      echo "RESULT: $r -> $d: DENIED - $err"
      ((denied_count++))
    fi
  done
done

echo "SUMMARY: ALLOWED=$allowed_count, DENIED=$denied_count, OTHER=$other_count"
