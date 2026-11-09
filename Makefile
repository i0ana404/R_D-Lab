# Deploy targets from Lab 3 (R-02). Run by a person in the Ubuntu VM, never by the AI agent.
# .PHONY is required: without it, make treats the secrets/ directory as the 'secrets' target
# and skips decryption.
.PHONY: secrets up down

# Decrypt the admin password at deploy time only. umask 077 makes .env.secrets readable by the
# owner alone, and `make down` deletes it.
secrets:
	umask 077 && sops -d secrets/opensearch.enc.yaml | sed 's/: /=/' > .env.secrets

up: secrets
	docker compose --env-file .env --env-file .env.secrets up -d

# The compose file requires the admin password variable even for `down`. The placeholder only
# satisfies that check; `down` never uses it. .env.secrets is deleted even if `down` fails.
down:
	OPENSEARCH_INITIAL_ADMIN_PASSWORD=unused docker compose down -v; rc=$$?; rm -f .env.secrets; exit $$rc
