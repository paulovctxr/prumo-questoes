#!/usr/bin/env bash
set -euo pipefail

: "${PRUMO_SUPABASE_URL:?Missing PRUMO_SUPABASE_URL}"
: "${PRUMO_SUPABASE_ANON_KEY:?Missing PRUMO_SUPABASE_ANON_KEY}"

python3 - <<'PY'
from pathlib import Path
import os, re

path = Path('dist/index.html')
text = path.read_text()
text = re.sub(r'window\.PRUMO_SUPABASE_URL="[^"]*"',
              'window.PRUMO_SUPABASE_URL=' + repr(os.environ['PRUMO_SUPABASE_URL']).replace("'", '"'), text)
text = re.sub(r'window\.PRUMO_SUPABASE_ANON_KEY="[^"]*"',
              'window.PRUMO_SUPABASE_ANON_KEY=' + repr(os.environ['PRUMO_SUPABASE_ANON_KEY']).replace("'", '"'), text)
path.write_text(text)
PY
