#!/bin/bash
# Runs as root on the instance's first boot.
set -euo pipefail
dnf install -y nginx
echo "hello from learnbox" > /usr/share/nginx/html/index.html
systemctl enable --now nginx
