#!/usr/bin/env bash
#
# Create the EVERY1 Pages project and attach its custom domain, if they do not
# already exist.
#
# Both steps check first and do nothing when the thing is already there, so this is
# safe to run on every push. It never prints the token. It exits 0 even when a call
# fails, because a missing second site must not stop the portal from deploying: the
# failure is reported and the deploy continues.
#
# Needs CLOUDFLARE_API_TOKEN with Pages:Edit on the account, and CLOUDFLARE_ACCOUNT_ID.

set -uo pipefail

PROJECT="${PROJECT:-every1-brand}"
DOMAIN="${DOMAIN:-brand.every1movement.com}"
: "${CLOUDFLARE_API_TOKEN:?CLOUDFLARE_API_TOKEN is not set}"
: "${CLOUDFLARE_ACCOUNT_ID:?CLOUDFLARE_ACCOUNT_ID is not set}"

API="https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/pages/projects"
AUTH="Authorization: Bearer ${CLOUDFLARE_API_TOKEN}"

say() { printf '%s\n' "$*"; }

report() {  # report <file> <success message>
  python3 - "$1" "$2" <<'PY'
import json, sys
path, ok = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(path))
except Exception as exc:
    print(f"could not read the response: {exc}")
    raise SystemExit
if d.get("success"):
    print(ok)
else:
    errs = d.get("errors") or d.get("messages") or "no detail returned"
    print(f"FAILED: {json.dumps(errs)[:400]}")
PY
}

code=$(curl -sS -o /tmp/cf-project.json -w '%{http_code}' "${API}/${PROJECT}" -H "${AUTH}")
if [ "${code}" = "200" ]; then
  say "Pages project ${PROJECT} already exists."
else
  say "Creating Pages project ${PROJECT} ..."
  curl -sS -o /tmp/cf-create.json -X POST "${API}" \
    -H "${AUTH}" -H 'Content-Type: application/json' \
    -d "{\"name\":\"${PROJECT}\",\"production_branch\":\"main\"}"
  report /tmp/cf-create.json "Created ${PROJECT}."
fi

curl -sS -o /tmp/cf-domains.json "${API}/${PROJECT}/domains" -H "${AUTH}"
have=$(DOMAIN="${DOMAIN}" python3 - <<'PY'
import json, os
try:
    d = json.load(open("/tmp/cf-domains.json"))
except Exception:
    print("unknown"); raise SystemExit
names = [x.get("name") for x in (d.get("result") or [])]
print("yes" if os.environ["DOMAIN"] in names else "no")
PY
)

if [ "${have}" = "yes" ]; then
  say "Custom domain ${DOMAIN} already attached."
elif [ "${have}" = "unknown" ]; then
  say "Could not read the domain list; leaving ${DOMAIN} alone."
else
  say "Attaching ${DOMAIN} ..."
  curl -sS -o /tmp/cf-domain.json -X POST "${API}/${PROJECT}/domains" \
    -H "${AUTH}" -H 'Content-Type: application/json' \
    -d "{\"name\":\"${DOMAIN}\"}"
  report /tmp/cf-domain.json "Attached ${DOMAIN}."
fi

exit 0
