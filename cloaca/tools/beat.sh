#!/usr/bin/env bash
# usage: beat.sh STAGE LINE PCT NEXT [EVENT]
# EVENT: routine (default) | milestone | release | halt
set -uo pipefail
LANE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EV="$LANE/evidence"; mkdir -p "$EV"
STAGE="${1:-0}"; LINE="${2:-none}"; PCT="${3:-0}"; NEXT="${4:-}"; EVENT="${5:-routine}"
[ -s /home/user/.private/bazalgette.env ] && { set -a; . /home/user/.private/bazalgette.env; set +a; }
: "${NTFY_TOPIC:?ntfy kit not loaded}"; NTFY_SERVER="${NTFY_SERVER:-https://ntfy.sh}"

python3 "$LANE/tools/state.py" > "$EV/.state.last" 2>/dev/null || true
S=$(cat "$EV/STATE.json" 2>/dev/null || echo '{}')
SEQ=$(( $(grep -c . "$EV/HEARTBEATS.jsonl" 2>/dev/null || echo 0) ))
NOW=$(date -u +%FT%TZ)
COMMIT=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("commit","0000000"))' "$EV/STATE.json" 2>/dev/null || echo 0000000)
BODY=$(python3 - "$S" "$SEQ" "$NOW" "$STAGE" "$LINE" "$PCT" "$NEXT" <<'PY'
import json,sys
s=json.loads(sys.argv[1]) if sys.argv[1].strip() else {}
seq,t,stage,line,pct,nxt=int(sys.argv[2]),sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7]
try: pctf=float(pct)
except Exception: pctf=0.0
print(json.dumps({"seq":seq,"t":t,"stage":stage,"line":line,
  "pct":round(pctf if pctf else float(s.get("pct",0.0)),2),
  "commit":s.get("commit","0000000"),
  "chunks_done":s.get("chunks_indexed",0),"bricks":s.get("brick_census",0),
  "engines_done":s.get("engines_done",0),"stations_done":s.get("stations_done",0),
  "renders_done":s.get("renders_done",0),"defects_open":s.get("defects_open",0),
  "census_equals_ledger":s.get("census_equals_ledger"),
  "ev":"beat","next":nxt},separators=(",",":")))
PY
)
case "$EVENT" in
  milestone) PRI=3; PTAG=default;;
  release)   PRI=4; PTAG=high;;
  halt)      PRI=5; PTAG=urgent;;
  *)         PRI=2; PTAG=low;;
esac
TITLE="BAZALGETTE ${STAGE} · ${LINE} · $(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("pct",0))' "$EV/STATE.json" 2>/dev/null || echo "$PCT")%"
RESP=$(printf 'url = "%s/%s"\nheader = "Title: %s"\nheader = "Priority: %s"\nheader = "Tags: heartbeat,stage-%s,%s"\ndata = "%s"\n' \
        "$NTFY_SERVER" "$NTFY_TOPIC" "$TITLE" "$PRI" "$STAGE" "$PTAG" \
        "$(printf '%s' "$BODY" | sed 's/"/\\"/g')" \
      | curl -sS -K - 2>"$EV/.beat_err")
redact_rc=$?
if [ -s "$EV/.beat_err" ]; then python3 -c 'import os,sys,re\nt=os.environ.get("NTFY_TOPIC","")\ns=open(sys.argv[1]).read()\nif t: s=s.replace(t,"<topic-redacted>")\nopen(sys.argv[2],"a").write(s)' "$EV/.beat_err" "$EV/HEARTBEAT_ERRORS.log"; : > "$EV/.beat_err"; fi
RC=$?
ID=$(printf '%s' "$RESP" | python3 -c 'import json,sys
try:
  d=json.load(sys.stdin); print(d.get("id",""))
except Exception: print("")' 2>/dev/null)
if [ $RC -ne 0 ] || [ -z "$ID" ]; then
  echo "{\"seq\":$SEQ,\"t\":\"$NOW\",\"delivered\":false,\"rc\":$RC,\"stage\":\"$STAGE\"}" >> "$EV/HEARTBEATS.jsonl"
  echo "BEAT FAILED seq=$SEQ rc=$RC (logged, run continues)" >&2
  exit 1
fi
python3 - "$EV/HEARTBEATS.jsonl" "$SEQ" "$NOW" "$ID" "$STAGE" "$LINE" "$BODY" <<'PY'
import json,sys
p,seq,t,mid,stage,line,body=sys.argv[1:8]
row={"seq":int(seq),"t":t,"id":mid,"stage":stage,"line":line,"delivered":True}
row.update({k:v for k,v in json.loads(body).items() if k in ("pct","commit","chunks_done","bricks","engines_done","defects_open","next")})
open(p,"a").write(json.dumps(row,separators=(",",":"))+"\n")
PY
echo "BEAT seq=$SEQ id=$ID stage=$STAGE line=$LINE pct=$(python3 -c 'import json;print(json.load(open("'"$EV"'/STATE.json")).get("pct",0))' 2>/dev/null)"
