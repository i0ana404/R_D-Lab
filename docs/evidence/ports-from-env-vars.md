---
name: ports-from-env-vars
description: "Never hardcode ports in config files; read each from an env var with a documented default like ${OPENSEARCH_PORT:-9200}"
metadata:
  node_type: memory
  type: feedback
  modified: 2026-10-27T09:31:51.444Z
---

Never hardcode ports in configuration files (docker-compose.yml, Logstash pipelines, OpenSearch/Dashboards config, etc.). Read every port from an environment variable with a documented default, e.g. `${OPENSEARCH_PORT:-9200}`.

**Why:** Owner's explicit rule for this project (given 2026-10-27). They asked for it to live in auto memory, not CLAUDE.md.

**How to apply:** Whenever writing or editing a config that references a port, use `${VAR:-default}` and document the variable and its default. Combine with the CLAUDE.md rule that published ports bind to 127.0.0.1, e.g. `"127.0.0.1:${OPENSEARCH_PORT:-9200}:9200"`. Don't add new docs files for this unprompted; propose where to document the variables if no place exists.
