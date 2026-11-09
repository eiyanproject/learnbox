#!/usr/bin/env bash
# Serverless 2: fan-out with SNS.
set -euo pipefail

# 1. The topic order-events.


# 2. Queues billing and shipping, each letting only that topic send to it.


# 3. Subscribe both with raw delivery; shipping filters on event = order_paid.


# 4. Publish order_placed, then order_paid (as the message attribute event).

