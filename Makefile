# Deploy targets from Lab 3 (R-02). Run by a person in the Ubuntu VM, never by the AI agent.
# Targets must run in order so enrich-check stops up before secrets decrypts anything, even under make -j.
.NOTPARALLEL:
# .PHONY is required: without it, make treats the secrets/ directory as the 'secrets' target
# and skips decryption.
.PHONY: secrets enrich-check up down test

# Decrypt secrets/opensearch.enc.yaml, secrets/intel.enc.yaml and secrets/observability.enc.yaml
# at deploy time only. umask 077 makes .env.secrets readable by the owner alone. If any decryption
# fails, the target exits non-zero and leaves no partial .env.secrets. `make down` deletes it.
secrets:
	umask 077 && sops -d secrets/opensearch.enc.yaml > .env.secrets.tmp && sops -d secrets/intel.enc.yaml >> .env.secrets.tmp && sops -d secrets/observability.enc.yaml >> .env.secrets.tmp && sed 's/: /=/' .env.secrets.tmp > .env.secrets; rc=$$?; rm -f .env.secrets.tmp; [ $$rc -eq 0 ] || rm -f .env.secrets; exit $$rc

# Logstash's 30-enrich-ioc.conf cannot start without the lookup file enrich/ioc_ip.yml.
enrich-check:
	@test -s enrich/ioc_ip.yml || { echo "enrich/ioc_ip.yml is missing or empty: run scripts/misp_pull.py first (needed by logstash/pipeline/30-enrich-ioc.conf)" >&2; exit 1; }

up: enrich-check secrets
	docker compose --env-file .env --env-file .env.secrets up -d
	sh scripts/opensearch-monitor-user.sh

# The compose file requires the password variables even for `down`. The placeholders only
# satisfy that check; `down` never uses them. .env.secrets is deleted even if `down` fails.
down:
	OPENSEARCH_INITIAL_ADMIN_PASSWORD=unused GRAFANA_ADMIN_PASSWORD=unused OPENSEARCH_MONITOR_PASSWORD=unused docker compose down -v; rc=$$?; rm -f .env.secrets; exit $$rc

# Run the test suite: the same command the CI "test" job runs (Lab 4).
test:
	python3 -m pytest -q
