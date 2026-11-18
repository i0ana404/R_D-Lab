# Front door from Lab 3: nginx terminates TLS in front of OpenSearch Dashboards.
# Pinned by tag and digest, so the build never floats. 1.30.6 is the 2026-10-14 security
# release. alpine-slim since 2026-11-16: the full image gained 3 HIGH CVEs in libxslt (XSLT module,
# unused here); slim leaves out the optional modules. Trivy: 0 HIGH/CRITICAL on 2026-11-16.
FROM nginx:1.31.8-alpine-slim@sha256:4c734d33ee731135dc9f2349914a34551c920f4451fca8bb05bf5880eb9079e8

# Site config only. Certificates stay out of the image and are mounted at runtime
# from certs/ (git-ignored), exactly as in compose.yaml.
COPY frontdoor.conf /etc/nginx/conf.d/default.conf

EXPOSE 443
