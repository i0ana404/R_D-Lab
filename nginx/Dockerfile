# Front door from Lab 3: nginx terminates TLS in front of OpenSearch Dashboards.
# Pinned by tag and digest, so the build never floats. 1.30.6 is the 2026-10-14 security
# release; Trivy reported 0 HIGH/CRITICAL on 2026-11-09 (1.27-alpine had 67, 1.30.5-alpine 18).
FROM nginx:1.30.6-alpine@sha256:583b7f2fce1cdb8da5ad5c39ebd3c33b98b87d493190e548bdee1fa8c619c311

# Site config only. Certificates stay out of the image and are mounted at runtime
# from certs/ (git-ignored), exactly as in compose.yaml.
COPY frontdoor.conf /etc/nginx/conf.d/default.conf

EXPOSE 443
