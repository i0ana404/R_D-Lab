# Front door from Lab 3: nginx terminates TLS in front of OpenSearch Dashboards.
# Pinned by tag and digest, so the build never floats. 1.30.7 is the 2026-11-18 stable security
# release; digest recorded on the deploy host 2026-11-20. Adopted 2 days after release, a deliberate
# exception to the 7-day cooldown: the pinned 1.30.6 had 6 fixed HIGH/CRITICAL CVEs.
# alpine-slim since 2026-11-16: the full image gained 3 HIGH CVEs in libxslt (XSLT module,
# unused here); slim leaves out the optional modules. Trivy 0.76.1: 0 HIGH/CRITICAL on 2026-11-20.
FROM nginx:1.30.7-alpine-slim@sha256:8c950211a641ec5b23f265450517001f6bcca533666120ebe36cb4cff3d00a55

# Site config only. Certificates stay out of the image and are mounted at runtime
# from certs/ (git-ignored), exactly as in compose.yaml.
COPY frontdoor.conf /etc/nginx/conf.d/default.conf

EXPOSE 443
