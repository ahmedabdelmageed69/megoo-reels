#!/usr/bin/env bash
# Downloads the brand fonts next to the tools (run once per machine).
set -e; cd "$(dirname "$0")"; mkdir -p fonts; cd fonts
npm pack @fontsource-variable/cairo @fontsource/jetbrains-mono --silent >/dev/null
for f in *.tgz; do tar xzf "$f" && rm -rf "${f%.tgz}" && mv package "${f%.tgz}" && rm "$f"; done
echo fonts ready
