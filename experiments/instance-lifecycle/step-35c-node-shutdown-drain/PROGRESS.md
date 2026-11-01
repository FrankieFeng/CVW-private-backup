# Step-35C progress

Stage1 audit started. CVW basea9910fb7; node base72e077a. Native patched SHA56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc pinned; no native edits. Historical failure retained Step35B. Work stages: audit → observation-only bounded baseline → minimal fix → bounded regression → analysis.

Initial evidence: storage write_block_type=0 (Common mode), CoreEngine.OnMessage CommitBlock launches untracked AddBlock goroutine, CoreEngine.Stop only stops proposer. Need trace full drain before claiming causal gap; no queue assumption. Next read proposer/committer and create observation-only snapshot.

Observation-only binary built. Store0/common mode; new diagnostic events and a one-shot12s-bounded writer rendezvous only, no shutdown change. Initial copy permission/tool PATH issues resolved without editing original module cache. Next idle Stop then held-write Stop; stop unfixed expansion after first protocol violation.

Phase3 observation protocol violation reproduced (CommonWrite, held writer and Close overlap, exit2 StateDB). Unfixed expansion stopped. Phase4 minimal fix implemented: RPC GracefulStop20s fail-safe, Core commit/verify admission+15s drain, CommonPutBlock lease+15s close drain+WAL cleanup wait, idempotent ledgerClose. Quick-mode and multi-consensus remain outside this prototype gate; not modifying Selector or Gas. Next build fix and lifecycle unit tests before regression.

Regression fix-idle idle PASS; raw logs and counts persisted.

Regression fix-normal normal PASS; raw logs and counts persisted.

Candidate fixed3 failed at active buyNow: grpc1.47 ServeHTTP transport GracefulStop Drain() unimplemented; full log/binary retained, later cases not run. Static API correction: use HTTP2 per-request admission/count spanning ServeHTTP response, drain20s, existing grpc.Stop after drain. No dependency upgrade, no resource guard change. STOP archived asSTOP-fixed3.json for failed candidate; corrected fixed4 gets new bounded preflight, no known unsafe path silently reenabled.

Regression v4-idle idle PASS; raw logs and counts persisted.

Regression v4-active active PASS; raw logs and counts persisted.

Regression v4-normal normal PASS; raw logs and counts persisted.

Regression v4-writer writer PASS; raw logs and counts persisted.

Regression v4-reset reset PASS; raw logs and counts persisted.

Regression v4-reset-after reset_after PASS; raw logs and counts persisted.

Regression v4-reset-stop reset_stop PASS; raw logs and counts persisted.

Regression v4-active-reset-stop active_reset_stop PASS; raw logs and counts persisted.

Candidate fixed4 eight lifecycle cases PASS. Restart-v4-active failed before transactions: retained diagnostic socket path, not DB corruption; no ledger correctness inference. Implement diagnostic HTTP close/join and per-run path in fixed5; preserve old socket/log and binary. Also propagate module-stop errors via explicit fail-safe because existing Stop API is void. Only bounded final validation, no feature expansion.

Regression v5-idle idle PASS; raw logs and counts persisted.

Regression v5-active active PASS; raw logs and counts persisted.

Regression v5-writer writer PASS; raw logs and counts persisted.

Regression v5-normal normal PASS; raw logs and counts persisted.

Regression v5-reset reset PASS; raw logs and counts persisted.

Regression v5-reset-after reset_after PASS; raw logs and counts persisted.

Regression v5-reset-stop reset_stop PASS; raw logs and counts persisted.

Regression v5-active-reset-stop active_reset_stop PASS; raw logs and counts persisted.

Fixed5 full8-case matrix passed, diagnostic server exits and socket unlinks. Final bounded-wait audit: now Blockchain.Stop aborts on module errors, so VM Owner Stop may safely use explicit10s context (instead of original Background); final candidate6 will repeat bounded matrix and restart checks with same unchanged Guest/native/Gas.

Regression final-idle idle PASS; raw logs and counts persisted.

Regression final-active active PASS; raw logs and counts persisted.

Regression final-writer writer PASS; raw logs and counts persisted.

Regression final-normal normal PASS; raw logs and counts persisted.

Regression final-reset reset PASS; raw logs and counts persisted.

Regression final-reset-after reset_after PASS; raw logs and counts persisted.

Regression final-reset-stop reset_stop PASS; raw logs and counts persisted.

Regression final-active-reset-stop active_reset_stop PASS; raw logs and counts persisted.

Restart check restart-final-active PASS, {"prior_tx_persisted": true, "tx_id": "18e3f88586ec47b8ca370cec12fb058dedc82606e1b4476db8cf899435cc4ff6", "gas": 12620048, "rollback_writes_empty": true, "owner_unchanged": true, "failed_tx_id": "18e3f8aa30bdaa32ca3b95d2ff2f7c6aed9627d518ff4022932fa09131a1ce88"}

Restart check restart-final-writer PASS, {"prior_tx_persisted": true, "tx_id": "18e3f886217462cdca7f44c12dbda95661cf91dc8bc04d168ffee309f154e4ab", "gas": 120135}

Restart check restart-final-active-reset-stop PASS, {"prior_tx_persisted": true, "tx_id": "18e3f8885bd5b5f8cad661ef7a94cfbdb77c05a96ca24d82a5fd3a4ea53dc01f", "gas": 120135}

Final matrix binary final: all8cases PASS. Release binary differs only preserving historical nil-Close behavior; targeted Close drain/idempotence/nil and gate tests PASS. Release restarted three same ledgers, prior-stop transactions persisted; duplicate real buyNow failed with empty writes and unchanged owner. No more dynamic tests. Next read-only reconstruction, reports and independent commits.

Release restart/rollback3checks PASS. Final background audit found ArchiveMgr.Close only signals, no join; sleeping loop/compaction could outlive DB close even though not observed failing. Minimal owned-worker join15s plus interruptible existing timer (no added Sleep), abort Close on drain error. No archive algorithm/Guest/Gas changes. Next final bounded closure matrix on release2 then reports; do not expand to other modes.

Regression candidate-idle idle PASS; raw logs and counts persisted.

Regression candidate-active active PASS; raw logs and counts persisted.

Regression candidate-writer writer PASS; raw logs and counts persisted.

Regression candidate-normal normal PASS; raw logs and counts persisted.

Regression candidate-reset reset PASS; raw logs and counts persisted.

Regression candidate-reset-after reset_after PASS; raw logs and counts persisted.

Regression candidate-reset-stop reset_stop PASS; raw logs and counts persisted.

Regression candidate-active-reset-stop active_reset_stop PASS; raw logs and counts persisted.

Restart check restart-candidate-active PASS, {"prior_tx_persisted": true, "tx_id": "18e3f9253f14b165ca77c91b1a4ac7af45907debbbf14f418cbcb410fe1d6d3c", "gas": 12620048, "rollback_writes_empty": true, "owner_unchanged": true, "failed_tx_id": "18e3f94081512636cae967792af9cd39992b7106fc894b578f3b99d580f3aad3"}

Restart check restart-candidate-writer PASS, {"prior_tx_persisted": true, "tx_id": "18e3f925d26502becabe3143437ad3f0f89648572ef94548a3e0b98f814ad010", "gas": 120135}

Restart check restart-candidate-active-reset-stop PASS, {"prior_tx_persisted": true, "tx_id": "18e3f92815d80ae9ca7eb25de1041bcc7f762e4e25de4d89a24db8e926e381d9", "gas": 120135}

Frozen candidate final:8/8cases and3/3restart checks PASS; candidate Store Close tests PASS. Relevant tasks/core/puts/writes/WAL/archive/diagnostic exits reconstructed balanced. Native SHA pinned unchanged. No running node on27535. Node source committed independently; no more code/runtime changes. Reports and provenance follow.

READ-ONLY handoff stage: candidate binaryc07aeffc171be1c3da8d8b4a69c74d19ef7008cf0253b78f916887b5cf47cc77, node commit0ce8fba. All8+3candidate cases exit0; counter/receipt/source/native checks passed. Final reports written; no current STOP (failed fixed3 latch preserved separately). No dynamic tests remain running. Next commit CVW experimental artifacts, mirror new report directory only; no remote push.

All delivery files ready; analysis asserts11final lifecycle/persistence cases and4same-input business parity records, candidate native unchanged. Go Heap/goroutine sampled fields added to RESOURCE_SUMMARY; absent snapshots explicitlynot_recorded. Node worktree clean commit0ce8fba. No further runs; commit experimental report/source/raw data, mirror main new directory only.
