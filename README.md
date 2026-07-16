Agent tooling for playing [Server Survival](https://pshenok.github.io/server-survival/).

Start with `python ledger.py h`, then `python ledger.py audit`. Weak agents must
use the deterministic files documented in `playwright/README.md`. If the active
run is finished, `python ledger.py fresh` creates the next audited UI run.
