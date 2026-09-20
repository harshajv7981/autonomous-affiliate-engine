#!/bin/sh
set -eu

config_path=${1:-infrastructure/postal/postal.yml}
template_path=infrastructure/postal/postal.yml.example

if [ ! -f "$config_path" ]; then
  cp "$template_path" "$config_path"
fi

if grep -q '\${POSTAL_RAILS_SECRET_KEY}' "$config_path"; then
  secret=$(openssl rand -hex 64)
  sed "s/\${POSTAL_RAILS_SECRET_KEY}/$secret/" "$config_path" > "$config_path.tmp"
  mv "$config_path.tmp" "$config_path"
  chmod 600 "$config_path"
  printf 'Generated Postal Rails secret in %s\n' "$config_path"
else
  printf 'Postal config already contains a Rails secret: %s\n' "$config_path"
fi
