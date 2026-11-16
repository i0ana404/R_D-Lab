# Deploy targets from Lab 3 (R-02). Run by a person in the Ubuntu VM, never by the AI agent.
# .PHONY is required: without it, make treats the secrets/ directory as the 'secrets' target
# and skips decryption.
.PHONY: secrets up down test

# Decrypt secrets/opensearch.enc.yaml and secrets/intel.enc.yaml at deploy time only. umask 077
# makes .env.secrets readable by the owner alone. If either decryption fails, the target exits
# non-zero and leaves no partial .env.secrets. `make down` deletes it.
secrets:
	umask 077 && sops -d secrets/opensearch.enc.yaml > .env.secrets.tmp && sops -d secrets/intel.enc.yaml >> .env.secrets.tmp && sed 's/: /=/' .env.secrets.tmp > .env.secrets; rc=$$?; rm -f .env.secrets.tmp; [ $$rc -eq 0 ] || rm -f .env.secrets; exit $$rc

up: secrets
	docker compose --env-file .env --env-file .env.secrets up -d

# The compose file requires the admin password variable even for `down`. The placeholder only
# satisfies that check; `down` never uses it. .env.secrets is deleted even if `down` fails.
down:
	OPENSEARCH_INITIAL_ADMIN_PASSWORD=unused docker compose down -v; rc=$$?; rm -f .env.secrets; exit $$rc

# Run the test suite: the same command the CI "test" job runs (Lab 4).
test:
	python3 -m pytest -q
