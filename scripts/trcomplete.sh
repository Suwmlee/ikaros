#!/bin/bash

TR_DOWNLOADS="$TR_TORRENT_DIR/$TR_TORRENT_NAME"
curl -XPOST http://127.0.0.1:12346/api/client -H 'Content-Type: application/json' \
--data @<(cat <<EOF
{"path":"$TR_DOWNLOADS"}
EOF
)
