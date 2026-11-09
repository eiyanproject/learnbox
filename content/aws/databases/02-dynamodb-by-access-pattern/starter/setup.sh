#!/usr/bin/env bash
# Databases 2: DynamoDB, designed by access pattern.
set -euo pipefail

# 1. The table orders: pk (S) and sk (S), on-demand, GSI by-status on status + sk.


# 2. TTL on expires_at; point-in-time recovery on.


# 3. Write items.json (edit the file) with batch-write-item.

