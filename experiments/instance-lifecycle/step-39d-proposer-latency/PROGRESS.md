# Step-39D

Base CVW ee87355b, node8ff98d6. Read-only historical reconstruction first. Original tmp ledgers no longer exist. Restore isolated development configuration for two bounded diagnostic runs only; no formal replacement samples. New node has a slow-RPC goroutine stack watchdog only, no consensus/VM/native changes. Planned windows8 and12, latter with2 real prelude transactions; Owner32/RSS1536MiB/threads220 unchanged.

Seed diag-seed-compute-plain PASS, deployment only, no performance samples.

window8 READY; raw logs/state/receipts saved.

window12-prelude2 READY; raw logs/state/receipts saved.


## Complete

Historical360 transactions reconstructed,24slow allformalordinal5/height6. Complete windows retained. RuleManager3-slot startup backpressure identified by source and two direct goroutine dumps. Registry.Start waits2s beforeProvider/RuleManager.Start; the serializedsafe msgbus stalls ahead ofTBFT notification.

Exactly2 diagnostic business runs plus1deployment seed: window8(0prelude),window12-prelude2(2prelude),20windowtx+2prelude allconfirmed. Slowordinal5→3, sameheight6; no extra performance samples planned. Bothnodes andseed exited0, Store/Instance balanced, Owneraccepted10/16(limit32), RSSmax593.902MiB, threadsmax28. No guard raised, forcedGC, requestSleep, Resetbudget refresh or production change. OnlyRPCwatchdog diagnosticnode patch; nofunctional repair.

Read-only reproduction commands: python3 scripts/analyze_history.py; python3 scripts/analyze_diagnostic.py; python3 scripts/report.py. Actual new runtime commands: STEP36_HOME=/tmp/cvw-step39d-seed-compute-plain python3 scripts/seed.py diag-seed-compute-plain compute plain; STEP36_HOME=/tmp/cvw-step39d-window8 STEP39D_N=8 STEP39D_PRELUDE=0 python3 scripts/case_run.py window8 compute_hashCal E0 diagnostic 1; STEP36_HOME=/tmp/cvw-step39d-window12-prelude2 STEP39D_N=12 STEP39D_PRELUDE=2 python3 scripts/case_run.py window12-prelude2 compute_hashCal E0 diagnostic 2. Build argv/evidence saved; original/tmp seeds no longer existed and configuration was restored.

Next action: manual review README/SOURCE_TRACE/NEXT_STEP. No task running, noStep40automaticexecution. New readiness barrier remains the minimum follow-up; no need to expand this diagnosis.

Diagnostic node source committed at589546a40ee518835b18c8103a23af43b628bb69. CVW experiment will be committed independently; no remote push. Single-validatorTBFT skipsSync ideal-heightwait, andchainStart isasynchronous; this explains whyport/firstreadyadmission was premature. All36historical windowstatistics replay exactly. Finaldeliverable readyforreview.
