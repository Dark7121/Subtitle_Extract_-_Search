#!/bin/bash
set -e

until nc -z -v -w30 $DB_HOST $DB_PORT
do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - executing command"
exec "$@"
