#!/usr/bin/env bash
# Serverless 1: queues and dead letters.
set -euo pipefail

# 1. orders-dlq, 14 days of retention. Keep its ARN.


# 2. orders: visibility 120, long polling 20, retention 345600, redrive to
#    orders-dlq after 5 receives.


# 3. payments.fifo with content-based deduplication.


# 4. Two messages to orders; one to payments.fifo in group account-1.

