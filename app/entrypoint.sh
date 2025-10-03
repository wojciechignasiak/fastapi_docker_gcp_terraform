#!/bin/sh

echo "Waiting for Database..."

while ! nc -z postgresql 5432; do
  sleep 0.1
done

echo "Database started!"

exec "$@"