#!/bin/sh
set -eu

BASE_URL="http://nginx"

fail() {
  echo "SMOKE TEST FAILED: $1" >&2
  exit 1
}

echo "== Smoke tests against ${BASE_URL} =="

echo "1. Reachability + routing: GET /version"
VERSION_JSON="$(curl -fsS "${BASE_URL}/version" || true)"
[ -n "$VERSION_JSON" ] || fail "/version returned empty response"
echo "$VERSION_JSON" | grep -q '"color"' || fail "/version missing 'color'"
echo "$VERSION_JSON" | grep -q '"version"' || fail "/version missing 'version'"
echo "   OK: $VERSION_JSON"

echo "2. DB integration: POST /db/populate"
POP_JSON="$(curl -fsS -X POST "${BASE_URL}/db/populate" || true)"
[ -n "$POP_JSON" ] || fail "/db/populate returned empty response"
echo "$POP_JSON" | grep -q '"status"' || fail "/db/populate missing 'status'"
echo "   OK: $POP_JSON"

echo "3. Data check: GET /stats (expect counts > 0)"
STATS_JSON="$(curl -fsS "${BASE_URL}/stats" || true)"
[ -n "$STATS_JSON" ] || fail "/stats returned empty response"
echo "$STATS_JSON" | grep -q '"tracker_count"' || fail "/stats missing tracker_count"
echo "$STATS_JSON" | grep -q '"vendor_count"' || fail "/stats missing vendor_count"

# Assert counts are not zero
echo "$STATS_JSON" | grep -Eq '"tracker_count":[[:space:]]*[1-9][0-9]*' || fail "tracker_count is 0"
echo "$STATS_JSON" | grep -Eq '"vendor_count":[[:space:]]*[1-9][0-9]*' || fail "vendor_count is 0"
echo "   OK: $STATS_JSON"

echo "4. Trackers UI route: GET /trackers (HTML check)"
HTML="$(curl -fsS "${BASE_URL}/trackers" || true)"
[ -n "$HTML" ] || fail "/trackers returned empty response"
echo "$HTML" | grep -q "Trackers" || fail "/trackers page missing expected text"
echo "   OK"

echo "5. Vendors API route: GET /vendors?limit=1 (non-empty array check)"
VENDORS_JSON="$(curl -fsS "${BASE_URL}/vendors?limit=1" || true)"
[ -n "$VENDORS_JSON" ] || fail "/vendors returned empty response"
# Should start with [ and contain at least one object "{"
echo "$VENDORS_JSON" | grep -Eq '^\[.*\{.*\}.*\]$' || fail "/vendors did not return a non-empty JSON array"
echo "   OK: $VENDORS_JSON"

echo "ALL SMOKE TESTS PASSED"
