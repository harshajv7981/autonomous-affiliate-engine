#!/bin/sh
set -eu

export PATH="/Applications/Docker.app/Contents/Resources/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

compose="docker compose"
postal_config="infrastructure/postal/postal.yml"
listmonk_schema="$(mktemp)"
postal_schema="$(mktemp)"
trap 'rm -f "$listmonk_schema" "$postal_schema"' EXIT

./scripts/bootstrap/postal-init.sh "$postal_config"
$compose up -d

printf 'Waiting for core services...\n'
until [ "$($compose ps -q postgres | xargs docker inspect --format '{{.State.Health.Status}}' 2>/dev/null || true)" = "healthy" ] \
  && [ "$($compose ps -q redis | xargs docker inspect --format '{{.State.Health.Status}}' 2>/dev/null || true)" = "healthy" ]; do
  sleep 2
done

printf 'Initializing listmonk when required...\n'
docker exec affiliate-listmonk-db psql -U listmonk -d listmonk -tAc "select to_regclass('public.settings')" > "$listmonk_schema"
if ! grep -q 'settings' "$listmonk_schema"; then
  printf 'y\n' | $compose run --rm listmonk ./listmonk --config /listmonk/config.toml --install
fi

printf 'Initializing Postal when required...\n'
docker exec affiliate-postal-mariadb mariadb -upostal -ppostal postal -Nse "show tables like 'users'" > "$postal_schema"
if ! grep -q '^users$' "$postal_schema"; then
  $compose run --rm postal-runner postal initialize
fi

$compose up -d
printf '\nPhase 1 services:\n'
$compose ps
