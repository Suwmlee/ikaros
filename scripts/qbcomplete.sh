#!/bin/bash
# qbcomplete.sh %D %N

QB_DOWNLOADS="${1}/${2}"
curl -XPOST http://127.0.0.1:12346/api/client -H 'Content-Type: application/json' \
--data @<(cat <<EOF
{"path":"$QB_DOWNLOADS"}
EOF
)
