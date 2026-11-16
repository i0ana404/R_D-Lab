# MISP setup (Lab 6)

## 2026-11-16

misp-docker commit: 2efbdcefd47cf6cd73889789d784044811b3edd8 2026-11-11

```
REPOSITORY                                                     TAG                  DIGEST                                                                    IMAGE ID       CREATED         SIZE
ghcr.io/misp/misp-docker/misp-modules                          latest               sha256:36e25925456ae510c71fc5c6c5b45ad2c3c9bacf19d1c981ccecfea0e8e8edd6   36e25925456a   4 days ago      1.9GB
ghcr.io/misp/misp-docker/misp-core                             latest               sha256:4b43b036962a1996ec23ba2ce619f88c8ad64a48729867348ae8dcf0dd9061db   4b43b036962a   4 days ago      2.05GB
ghcr.io/misp/misp-docker/misp-nginx                            latest               sha256:84bc3a6587eec76bc8d5285bf7b60a46cc89281367de0675dc97b87913b24c4f   84bc3a6587ee   4 days ago      275MB
ghcr.io/mariadb/mariadb                                        10.11                sha256:c22d749c07c6d2b3b5827074d7a54c97ebada20a69c491efef819b8c1ecaa96f   c22d749c07c6   5 days ago      466MB
ghcr.io/valkey-io/valkey                                       7.2                  sha256:828b1cbb1c258e02b9cd9588063fa997e097444e610d3f3c00d43e21400e2b8d   828b1cbb1c25   2 weeks ago     167MB
ghcr.io/egos-tech/smtp                                         2.0.12               sha256:c7577b21872f785ffdc9f4403938322cc424055c771621586bec60a05745d312   c7577b21872f   3 weeks ago     244MB
```

## Feed (2026-11-16)

- CIRCL OSINT Feed (https://www.circl.lu/doc/misp/feed-osint), format MISP, singurul feed activat.
- Fetch 2026-11-16, 12:55-13:45 EET (aprox. 50 min pe VM), job fetch_feed: 1681 evenimente, status Completed.

## TLS (2026-11-16)

- misp-nginx nu porneste fara certificat cand BASE_URL e https:// (bucla de restart).
- Certificat leaf emis offline din CA-ul step-ca din Lab 3: CN/SAN localhost + 127.0.0.1, valabil 90 de zile, cu lantul intermediar.
- ssl/key.pem root:101 0640 (cerinta misp-docker: nginx ruleaza ca uid/gid 101). Certificatul si cheia NU sunt in git.
- Verificat fara -k: curl --cacert root_ca.crt https://localhost:8444/ -> HTTP 302.
- MISP_CA pentru PyMISP = root_ca.crt (abatere de la ghid, care lasa MISP_CA gol si dezactiveaza verificarea TLS).
