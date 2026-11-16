# Front door from Lab 3: nginx terminates TLS in front of OpenSearch Dashboards.
# Pinned by tag and digest, so the build never floats. 1.30.6 is the 2026-10-14 security
# release. alpine-slim since 2026-11-16: the full image gained 3 HIGH CVEs in libxslt (XSLT module,
# unused here); slim leaves out the optional modules. Trivy: 0 HIGH/CRITICAL on 2026-11-16.
FROM nginx:1.30.6-alpine-slim@sha256:e2355aa95529a7999dad94ddcb45a8768abf6fb0b204c93b1a3ffce477d7b893

# Site config only. Certificates stay out of the image and are mounted at runtime
# from certs/ (git-ignored), exactly as in compose.yaml.
COPY frontdoor.conf /etc/nginx/conf.d/default.conf

EXPOSE 443
