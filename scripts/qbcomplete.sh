#!/bin/bash
# qbcomplete.sh "%F"
# 如果docker的挂载路径与qbit挂载路径不同名的话，需要用以下命令a="%F"&& sh qbcomplete.sh ${a/qbit挂载路径/ikros挂载路径}

QB_DOWNLOADS="${1}"
curl -XPOST http://127.0.0.1:12346/api/client -H 'Content-Type: application/json' \
--data @<(cat <<EOF
{"path":"$QB_DOWNLOADS"}
EOF
)
