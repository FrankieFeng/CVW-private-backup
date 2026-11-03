# Step-39C

Branch experiment/step39c-node-e2e-sha-acopy.
Base CVW cda3c0f3, node c28bfa8 with35C ancestor0ce8fba.
First: rebuild isolated network and real node smoke. No formal samples until every smoke gate passes.
RSS1536MiB/threads220/Owner32 unchanged.

Seed seed-compute-plain PASS, deployment only, no performance samples.

Seed seed-compute-A PASS, deployment only, no performance samples.

Seed seed-bigInput-plain PASS, deployment only, no performance samples.

Seed seed-bigInput-A PASS, deployment only, no performance samples.

Seed seed-exchange-plain PASS, deployment only, no performance samples.

Seed seed-exchange-A PASS, deployment only, no performance samples.

pre-compute_hashCal-E0 READY; raw logs/state/receipts saved.

pre-compute_hashCal-E1 READY; raw logs/state/receipts saved.

pre-compute_hashCal-E2 READY; raw logs/state/receipts saved.

pre-compute_hashCal-E3 READY; raw logs/state/receipts saved.

pre-bigInput_inputSize-E0 READY; raw logs/state/receipts saved.

pre-bigInput_inputSize-E1 READY; raw logs/state/receipts saved.

pre-bigInput_inputSize-E2 READY; raw logs/state/receipts saved.

pre-bigInput_inputSize-E3 READY; raw logs/state/receipts saved.

pre-exchange_buyNow-E0 READY; raw logs/state/receipts saved.

pre-exchange_buyNow-E1 READY; raw logs/state/receipts saved.

pre-exchange_buyNow-E2 READY; raw logs/state/receipts saved.

pre-exchange_buyNow-E3 READY; raw logs/state/receipts saved.

Checkpoint: 6 deployment seeds and 12 four-group SDK prechecks passed with exact business parity; real-node capacity8/full rejection/Reset recovery passed (peak1310.51MiB). Upgrade first rejected for required3 endorsements; no native/state fault. Preserved wrapper failures cap-seed0/1 (RWSet type) and smoke-upgrade-r1 (retry branch). Corrected harness/endorsement handling; active command upgrade.py smoke-upgrade-r2 retry on isolated home /tmp/cvw-step39c-upgrade. No formal samples started.

Postcheck smoke-rollback-compute_hashCal PASS; committed tx/readback + genuine error rollback verified after restart, sourcepre-compute_hashCal-E3-case.json

Postcheck smoke-rollback-bigInput_inputSize PASS; committed tx/readback + genuine error rollback verified after restart, sourcepre-bigInput_inputSize-E3-case.json

Postcheck smoke-rollback-exchange_buyNow PASS; committed tx/readback + genuine error rollback verified after restart, sourcepre-exchange_buyNow-E3-case.json

SMOKE_GATE PASSED: 121checks, SDK business/commit, real upgrade, invalid same-version upgrade, Reset/budget, Stop/inflight/restart, capacity8 rejection and resource balance. Formal transactions before gate=0. Next: study.py formal (3batches×3methods×4groups×10=360).

formal-compute_hashCal-b1-E0 PASSED; raw logs/state/receipts saved.

formal-compute_hashCal-b1-E1 PASSED; raw logs/state/receipts saved.

formal-compute_hashCal-b1-E2 PASSED; raw logs/state/receipts saved.

formal-compute_hashCal-b1-E3 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b1-E2 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b1-E3 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b1-E0 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b1-E1 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b1-E0 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b1-E1 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b1-E2 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b1-E3 PASSED; raw logs/state/receipts saved.

formal-compute_hashCal-b2-E3 PASSED; raw logs/state/receipts saved.

formal-compute_hashCal-b2-E2 PASSED; raw logs/state/receipts saved.

formal-compute_hashCal-b2-E1 PASSED; raw logs/state/receipts saved.

formal-compute_hashCal-b2-E0 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b2-E1 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b2-E0 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b2-E3 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b2-E2 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b2-E3 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b2-E2 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b2-E1 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b2-E0 PASSED; raw logs/state/receipts saved.

formal-compute_hashCal-b3-E1 PASSED; raw logs/state/receipts saved.

formal-compute_hashCal-b3-E0 PASSED; raw logs/state/receipts saved.

formal-compute_hashCal-b3-E3 PASSED; raw logs/state/receipts saved.

formal-compute_hashCal-b3-E2 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b3-E3 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b3-E2 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b3-E1 PASSED; raw logs/state/receipts saved.

formal-bigInput_inputSize-b3-E0 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b3-E1 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b3-E0 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b3-E3 PASSED; raw logs/state/receipts saved.

formal-exchange_buyNow-b3-E2 PASSED; raw logs/state/receipts saved.

Postcheck restart-formal-bigInput_inputSize-b1-E0 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b1-E0-case.json

Postcheck restart-formal-bigInput_inputSize-b1-E1 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b1-E1-case.json

Postcheck restart-formal-bigInput_inputSize-b1-E2 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b1-E2-case.json

Postcheck restart-formal-bigInput_inputSize-b1-E3 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b1-E3-case.json

Postcheck restart-formal-bigInput_inputSize-b2-E0 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b2-E0-case.json

Postcheck restart-formal-bigInput_inputSize-b2-E1 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b2-E1-case.json

Postcheck restart-formal-bigInput_inputSize-b2-E2 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b2-E2-case.json

Postcheck restart-formal-bigInput_inputSize-b2-E3 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b2-E3-case.json

Postcheck restart-formal-bigInput_inputSize-b3-E0 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b3-E0-case.json

Postcheck restart-formal-bigInput_inputSize-b3-E1 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b3-E1-case.json

Postcheck restart-formal-bigInput_inputSize-b3-E2 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b3-E2-case.json

Postcheck restart-formal-bigInput_inputSize-b3-E3 PASS; committed tx/readback verified after restart, sourceformal-bigInput_inputSize-b3-E3-case.json

Postcheck restart-formal-compute_hashCal-b1-E0 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b1-E0-case.json

Postcheck restart-formal-compute_hashCal-b1-E1 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b1-E1-case.json

Postcheck restart-formal-compute_hashCal-b1-E2 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b1-E2-case.json

Postcheck restart-formal-compute_hashCal-b1-E3 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b1-E3-case.json

Postcheck restart-formal-compute_hashCal-b2-E0 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b2-E0-case.json

Postcheck restart-formal-compute_hashCal-b2-E1 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b2-E1-case.json

Postcheck restart-formal-compute_hashCal-b2-E2 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b2-E2-case.json

Postcheck restart-formal-compute_hashCal-b2-E3 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b2-E3-case.json

Postcheck restart-formal-compute_hashCal-b3-E0 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b3-E0-case.json

Postcheck restart-formal-compute_hashCal-b3-E1 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b3-E1-case.json

Postcheck restart-formal-compute_hashCal-b3-E2 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b3-E2-case.json

Postcheck restart-formal-compute_hashCal-b3-E3 PASS; committed tx/readback verified after restart, sourceformal-compute_hashCal-b3-E3-case.json

Postcheck restart-formal-exchange_buyNow-b1-E0 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b1-E0-case.json

Postcheck restart-formal-exchange_buyNow-b1-E1 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b1-E1-case.json

Postcheck restart-formal-exchange_buyNow-b1-E2 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b1-E2-case.json

Postcheck restart-formal-exchange_buyNow-b1-E3 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b1-E3-case.json

Postcheck restart-formal-exchange_buyNow-b2-E0 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b2-E0-case.json

Postcheck restart-formal-exchange_buyNow-b2-E1 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b2-E1-case.json

Postcheck restart-formal-exchange_buyNow-b2-E2 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b2-E2-case.json

Postcheck restart-formal-exchange_buyNow-b2-E3 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b2-E3-case.json

Postcheck restart-formal-exchange_buyNow-b3-E0 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b3-E0-case.json

Postcheck restart-formal-exchange_buyNow-b3-E1 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b3-E1-case.json

Postcheck restart-formal-exchange_buyNow-b3-E2 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b3-E2-case.json

Postcheck restart-formal-exchange_buyNow-b3-E3 PASS; committed tx/readback verified after restart, sourceformal-exchange_buyNow-b3-E3-case.json


## Final checkpoint — complete

- Stage1: isolated node/client build, six frozen deployment seeds,12 method/config prechecks, real capacity8 rejection/Reset recovery, actual version upgrade/same-version rejection, in-flight Reset+Stop and restart, error rollback all completed. SMOKE_COMPLETE.json (121 checks) predates formal runs.
- Stage2: all36 formal processes finished:3 batches×3methods×4groups×10 =360/360 successful confirmed root transactions,0 failures/0timeouts. No sample deletion. EachOwner accepted12/limit32; noReset in formal.
- Stage3:36 additional read-only restarts verified every formal tx/height/result and final business KV projection.107 total node processes exited0 with native counts balanced and Artifact cleared; no active node/client remains.
- Stage4: scripts/analyze.py and scripts/finalize.py regenerated CSV/report from saved data. Stronger27 exact cross-group checks and720 child trace/Gas comparisons pass, no normalization beyond collection ordering.
- Negative evidence retained:24 >1sec short-method transactions atslot4, VM-entry proposal-state interval; TPS/P95 do not universally improve. Oldfalse orchestration/auth checks and original raw logs retained; details SMOKE.md.
- Native hash56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc. Actual network single-validatorTBFT(type1), notSolo; existingconfigunchanged.
- Resource thresholds unchanged1536MiB/220threads. PeakformalRSS1161.727MiB; allSmokepeak1310.508MiB; threadsmax46.
- Node integration committed independently at8ff98d6e25d6c16a73a8f7d80c404120d0d44c30; CVW experiment commit follows in its own isolated branch. No remote push.

### Commands and recoverability

All actual per-process argv/env/home stored in raw_logs/*-command.json and audit/*-orchestration.json, build commands in audit/node4-command.json/client3-command.json. Execution entries: study.py seeds/pre/formal; capacity.py,upgrade.py,inflight.py,restart_inflight.py,postcheck.py,restart_formal.py. Existing valid results were reused after interruption, not repeated. Final read-only commands: `python3 scripts/analyze.py`; `python3 scripts/finalize.py`.

Current blockers: no correctness/safety failure in completed bounded scope. Statistical/measurement limitation remains: only3 independent batches, short-method pre-VM tail behavior and globally stationary TBFT load not established. No further automatic experiment is authorized by this checkpoint.

Next command: read README.md, PAIRED_EFFECTS.csv, TPS_EFFECTS.csv and SMOKE.md for manual review. Do not rerun smoke_gate.py on completed data or automatically startStep40. No tests running in background.

Validation note: unrestricted git diff --check flags inherited CRLF/source whitespace and original console logs. These bytes are preserved to retain build/source and raw evidence identity; no broad formatting rewrite was performed. New reports/scripts checked separately.
