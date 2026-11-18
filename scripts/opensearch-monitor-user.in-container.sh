#!/bin/sh
# Runs inside the opensearch container, fed on stdin by opensearch-monitor-user.sh.
# Role prometheus_monitor = action group cluster_monitor (cluster:monitor/*): cluster health
# and node stats only, no index data, no writes. The script proves that before it exits.
set -eu

: "${OPENSEARCH_INITIAL_ADMIN_PASSWORD:?missing in the opensearch container}"
: "${OPENSEARCH_MONITOR_PASSWORD:?not passed by opensearch-monitor-user.sh}"

base=https://localhost:9200
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
umask 077
# Credentials go through curl config files, not argv, so they never show in ps.
printf 'user = "admin:%s"\n' "$OPENSEARCH_INITIAL_ADMIN_PASSWORD" >"$tmp/admin.cfg"
printf 'user = "prometheus:%s"\n' "$OPENSEARCH_MONITOR_PASSWORD" >"$tmp/monitor.cfg"

# status CONFIG METHOD PATH [BODY_FILE]: print the HTTP status, keep the body in $tmp/resp
status() {
    if [ $# -eq 4 ]; then
        curl -sk -K "$1" -o "$tmp/resp" -w '%{http_code}' -X "$2" "$base$3" \
            -H 'Content-Type: application/json' --data-binary "@$4"
    else
        curl -sk -K "$1" -o "$tmp/resp" -w '%{http_code}' -X "$2" "$base$3"
    fi
}

# OpenSearch can take minutes to start in the VM: wait up to 5 minutes for the security API.
tries=0
until [ "$(status "$tmp/admin.cfg" GET /_plugins/_security/health)" = 200 ]; do
    tries=$((tries + 1))
    if [ "$tries" -gt 60 ]; then
        echo "OpenSearch security API not ready after 5 minutes" >&2
        exit 1
    fi
    sleep 5
done

put() {
    code=$(status "$tmp/admin.cfg" PUT "/_plugins/_security/api/$1" "$2")
    case "$code" in
    200 | 201) ;;
    *)
        echo "PUT $1 -> HTTP $code: $(cat "$tmp/resp")" >&2
        exit 1
        ;;
    esac
}

printf '%s\n' '{"cluster_permissions": ["cluster_monitor"]}' >"$tmp/role.json"
printf '{"password": "%s", "description": "Prometheus exporter, read-only monitoring"}\n' \
    "$OPENSEARCH_MONITOR_PASSWORD" >"$tmp/user.json"
printf '%s\n' '{"users": ["prometheus"]}' >"$tmp/mapping.json"

put roles/prometheus_monitor "$tmp/role.json"
put internalusers/prometheus "$tmp/user.json"
put rolesmapping/prometheus_monitor "$tmp/mapping.json"

# Least privilege, checked: health readable, index data not readable, writes refused.
# The read check uses a concrete probe index the admin creates: a wildcard such as sshd-*
# answers 200 with no hits while no index matches yet, which would prove nothing.
printf '%s\n' '{"probe": 1}' >"$tmp/doc.json"
status "$tmp/admin.cfg" PUT '/monitor-read-probe/_doc/1?refresh=true' "$tmp/doc.json" >/dev/null
health=$(status "$tmp/monitor.cfg" GET /_cluster/health)
search=$(status "$tmp/monitor.cfg" GET /monitor-read-probe/_search)
write=$(status "$tmp/monitor.cfg" PUT /monitor-write-probe/_doc/1 "$tmp/doc.json")
status "$tmp/admin.cfg" DELETE /monitor-read-probe >/dev/null || true
if [ "$write" != 403 ]; then
    status "$tmp/admin.cfg" DELETE /monitor-write-probe >/dev/null || true
fi
if [ "$health" != 200 ] || [ "$search" != 403 ] || [ "$write" != 403 ]; then
    echo "monitor user check failed: health=$health (want 200) search=$search (want 403) write=$write (want 403)" >&2
    exit 1
fi
echo "OpenSearch monitor user ready: cluster health 200, index search 403, write 403"
