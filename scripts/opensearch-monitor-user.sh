#!/bin/sh
# Create or update the least-privilege OpenSearch user that the Prometheus exporter logs in
# with (RISK-REGISTER R-02, R-09). Called by `make up` after the stack starts; idempotent.
# Neither password appears on a command line: the admin password is already in the opensearch
# container's environment, and the monitor password is passed to it by name with exec -e.
set -eu

secrets=.env.secrets
OPENSEARCH_MONITOR_PASSWORD=$(sed -n 's/^OPENSEARCH_MONITOR_PASSWORD=//p' "$secrets")
if [ -z "$OPENSEARCH_MONITOR_PASSWORD" ]; then
    echo "OPENSEARCH_MONITOR_PASSWORD is missing from $secrets: run make secrets" >&2
    exit 1
fi
export OPENSEARCH_MONITOR_PASSWORD

docker compose --env-file .env --env-file "$secrets" \
    exec -T -e OPENSEARCH_MONITOR_PASSWORD opensearch \
    sh -s <scripts/opensearch-monitor-user.in-container.sh
