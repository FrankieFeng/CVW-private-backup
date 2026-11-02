# Step-36 progress

Audit/build lineage → inventory/fixtures → graded functional precheck → bounded3-batch measurement → read-only statistics and reports.
CVW base885db646, node0ce8fba; native56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc. New isolated worktrees, production unchanged. Only Common0, sync one client,1536MiB/220threads soft guards. No tests started.

Initial design:37 business candidates from32/33 plus rescan. 3 configurations mandatory, A-only where safe. Per method:3independent batches, initially2measured calls per group/batch, balance group order. Entire per-group ledger is cloned from equivalent frozen seed; prewarm/setup outside TPS window. All target calls invoke synchronously including read-only methods, so they actually submit transactions. Window first Invoke start→last Invoke return; post-window TxID/RWset verification required. Low N exploratory CIs, no universal claim.

Seed seed-compute-plain PASS, deployment only, no performance samples.

SDK timing code/serial client built, node2 readback hook built (node first build API name error retained). Empty-ledger seed compute plain deployed and closed safely. Before any formal sample freeze4target calls/group/batch (alterAdmin1),3batches; all setup/prewarm outside main window. Next real-node prechecks across three groups.

pre-compute_bigNumCal-G0 READY; raw logs/state/receipts saved. 

Seed seed-bigInput-plain PASS, deployment only, no performance samples.

Seed seed-bigInput-A PASS, deployment only, no performance samples.

Seed seed-compute-A PASS, deployment only, no performance samples.

Seed seed-erc721-plain PASS, deployment only, no performance samples.

Seed seed-erc721-A PASS, deployment only, no performance samples.

Seed seed-exchange-plain PASS, deployment only, no performance samples.

Seed seed-exchange-A PASS, deployment only, no performance samples.

Seed seed-fact-plain PASS, deployment only, no performance samples.

Seed seed-fact-A PASS, deployment only, no performance samples.

Seed seed-identity-plain PASS, deployment only, no performance samples.

Seed seed-identity-A PASS, deployment only, no performance samples.

Seed seed-itinerary-plain PASS, deployment only, no performance samples.

Seed seed-itinerary-A PASS, deployment only, no performance samples.

Seed seed-raffle-plain PASS, deployment only, no performance samples.

Seed seed-raffle-A PASS, deployment only, no performance samples.

p-bigInput_inputSize-G0 READY; raw logs/state/receipts saved. 

p-bigInput_inputSize-G1 READY; raw logs/state/receipts saved. 

p-bigInput_inputSize-G2 READY; raw logs/state/receipts saved. 

p-bigInput_inputSize-G3 READY; raw logs/state/receipts saved. 

f-bigInput_inputSize-b1-G0 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSize-b1-G1 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSize-b1-G2 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSize-b1-G3 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSize-b2-G2 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSize-b2-G3 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSize-b2-G0 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSize-b2-G1 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSize-b3-G1 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSize-b3-G0 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSize-b3-G3 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSize-b3-G2 PASSED; raw logs/state/receipts saved. 

p-bigInput_inputSizeMulti-G0 READY; raw logs/state/receipts saved. 

p-bigInput_inputSizeMulti-G1 READY; raw logs/state/receipts saved. 

p-bigInput_inputSizeMulti-G2 READY; raw logs/state/receipts saved. 

p-bigInput_inputSizeMulti-G3 READY; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b1-G0 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b1-G1 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b1-G2 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b1-G3 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b2-G2 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b2-G3 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b2-G0 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b2-G1 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b3-G1 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b3-G0 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b3-G3 PASSED; raw logs/state/receipts saved. 

f-bigInput_inputSizeMulti-b3-G2 PASSED; raw logs/state/receipts saved. 

p-bigInput_ioHeavy-G0 READY; raw logs/state/receipts saved. 

p-bigInput_ioHeavy-G1 READY; raw logs/state/receipts saved. 

p-bigInput_ioHeavy-G2 READY; raw logs/state/receipts saved. 

p-bigInput_ioHeavy-G3 READY; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b1-G0 PASSED; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b1-G1 PASSED; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b1-G2 PASSED; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b1-G3 PASSED; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b2-G2 PASSED; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b2-G3 PASSED; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b2-G0 PASSED; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b2-G1 PASSED; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b3-G1 PASSED; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b3-G0 PASSED; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b3-G3 PASSED; raw logs/state/receipts saved. 

f-bigInput_ioHeavy-b3-G2 PASSED; raw logs/state/receipts saved. 

p-identity_addWriteList-G0 READY; raw logs/state/receipts saved. 

p-identity_addWriteList-G1 READY; raw logs/state/receipts saved. 

p-identity_addWriteList-G2 READY; raw logs/state/receipts saved. 

p-identity_addWriteList-G3 READY; raw logs/state/receipts saved. 

f-identity_addWriteList-b1-G0 PASSED; raw logs/state/receipts saved. 

f-identity_addWriteList-b1-G1 PASSED; raw logs/state/receipts saved. 

f-identity_addWriteList-b1-G2 PASSED; raw logs/state/receipts saved. 

f-identity_addWriteList-b1-G3 PASSED; raw logs/state/receipts saved. 

f-identity_addWriteList-b2-G2 PASSED; raw logs/state/receipts saved. 

f-identity_addWriteList-b2-G3 PASSED; raw logs/state/receipts saved. 

f-identity_addWriteList-b2-G0 PASSED; raw logs/state/receipts saved. 

f-identity_addWriteList-b2-G1 PASSED; raw logs/state/receipts saved. 

f-identity_addWriteList-b3-G1 PASSED; raw logs/state/receipts saved. 

f-identity_addWriteList-b3-G0 PASSED; raw logs/state/receipts saved. 

f-identity_addWriteList-b3-G3 PASSED; raw logs/state/receipts saved. 

f-identity_addWriteList-b3-G2 PASSED; raw logs/state/receipts saved. 

p-identity_alterAdminAddress-G0 READY; raw logs/state/receipts saved. 

p-identity_alterAdminAddress-G1 READY; raw logs/state/receipts saved. 

p-identity_alterAdminAddress-G2 READY; raw logs/state/receipts saved. 

p-identity_alterAdminAddress-G3 READY; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b1-G0 PASSED; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b1-G1 PASSED; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b1-G2 PASSED; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b1-G3 PASSED; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b2-G2 PASSED; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b2-G3 PASSED; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b2-G0 PASSED; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b2-G1 PASSED; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b3-G1 PASSED; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b3-G0 PASSED; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b3-G3 PASSED; raw logs/state/receipts saved. 

f-identity_alterAdminAddress-b3-G2 PASSED; raw logs/state/receipts saved. 

p-identity_removeWriteList-G0 READY; raw logs/state/receipts saved. 

p-identity_removeWriteList-G1 READY; raw logs/state/receipts saved. 

p-identity_removeWriteList-G2 READY; raw logs/state/receipts saved. 

p-identity_removeWriteList-G3 READY; raw logs/state/receipts saved. 

f-identity_removeWriteList-b1-G0 PASSED; raw logs/state/receipts saved. 

f-identity_removeWriteList-b1-G1 PASSED; raw logs/state/receipts saved. 

f-identity_removeWriteList-b1-G2 PASSED; raw logs/state/receipts saved. 

f-identity_removeWriteList-b1-G3 PASSED; raw logs/state/receipts saved. 

f-identity_removeWriteList-b2-G2 PASSED; raw logs/state/receipts saved. 

f-identity_removeWriteList-b2-G3 PASSED; raw logs/state/receipts saved. 

f-identity_removeWriteList-b2-G0 PASSED; raw logs/state/receipts saved. 

f-identity_removeWriteList-b2-G1 PASSED; raw logs/state/receipts saved. 

f-identity_removeWriteList-b3-G1 PASSED; raw logs/state/receipts saved. 

f-identity_removeWriteList-b3-G0 PASSED; raw logs/state/receipts saved. 

f-identity_removeWriteList-b3-G3 PASSED; raw logs/state/receipts saved. 

f-identity_removeWriteList-b3-G2 PASSED; raw logs/state/receipts saved. 

p-identity_isApprovedUser-G0 READY; raw logs/state/receipts saved. 

p-identity_isApprovedUser-G1 READY; raw logs/state/receipts saved. 

p-identity_isApprovedUser-G2 READY; raw logs/state/receipts saved. 

p-identity_isApprovedUser-G3 READY; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b1-G0 PASSED; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b1-G1 PASSED; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b1-G2 PASSED; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b1-G3 PASSED; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b2-G2 PASSED; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b2-G3 PASSED; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b2-G0 PASSED; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b2-G1 PASSED; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b3-G1 PASSED; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b3-G0 PASSED; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b3-G3 PASSED; raw logs/state/receipts saved. 

f-identity_isApprovedUser-b3-G2 PASSED; raw logs/state/receipts saved. 

p-identity_address-G0 READY; raw logs/state/receipts saved. 

p-identity_address-G1 READY; raw logs/state/receipts saved. 

p-identity_address-G2 READY; raw logs/state/receipts saved. 

p-identity_address-G3 READY; raw logs/state/receipts saved. 

f-identity_address-b1-G0 PASSED; raw logs/state/receipts saved. 

f-identity_address-b1-G1 PASSED; raw logs/state/receipts saved. 

f-identity_address-b1-G2 PASSED; raw logs/state/receipts saved. 

f-identity_address-b1-G3 PASSED; raw logs/state/receipts saved. 

f-identity_address-b2-G2 PASSED; raw logs/state/receipts saved. 

f-identity_address-b2-G3 PASSED; raw logs/state/receipts saved. 

f-identity_address-b2-G0 PASSED; raw logs/state/receipts saved. 

f-identity_address-b2-G1 PASSED; raw logs/state/receipts saved. 

f-identity_address-b3-G1 PASSED; raw logs/state/receipts saved. 

f-identity_address-b3-G0 PASSED; raw logs/state/receipts saved. 

f-identity_address-b3-G3 PASSED; raw logs/state/receipts saved. 

f-identity_address-b3-G2 PASSED; raw logs/state/receipts saved. 

p-itinerary_save-G0 READY; raw logs/state/receipts saved. 

p-itinerary_save-G1 READY; raw logs/state/receipts saved. 

p-itinerary_save-G2 READY; raw logs/state/receipts saved. 

p-itinerary_save-G3 READY; raw logs/state/receipts saved. 

f-itinerary_save-b1-G0 PASSED; raw logs/state/receipts saved. 

f-itinerary_save-b1-G1 PASSED; raw logs/state/receipts saved. 

f-itinerary_save-b1-G2 PASSED; raw logs/state/receipts saved. 

f-itinerary_save-b1-G3 PASSED; raw logs/state/receipts saved. 

f-itinerary_save-b2-G2 PASSED; raw logs/state/receipts saved. 

f-itinerary_save-b2-G3 PASSED; raw logs/state/receipts saved. 

f-itinerary_save-b2-G0 PASSED; raw logs/state/receipts saved. 

f-itinerary_save-b2-G1 PASSED; raw logs/state/receipts saved. 

f-itinerary_save-b3-G1 PASSED; raw logs/state/receipts saved. 

f-itinerary_save-b3-G0 PASSED; raw logs/state/receipts saved. 

f-itinerary_save-b3-G3 PASSED; raw logs/state/receipts saved. 

f-itinerary_save-b3-G2 PASSED; raw logs/state/receipts saved. 

p-itinerary_queryHistory-G0 READY; raw logs/state/receipts saved. 

p-itinerary_queryHistory-G1 READY; raw logs/state/receipts saved. 

p-itinerary_queryHistory-G2 READY; raw logs/state/receipts saved. 

p-itinerary_queryHistory-G3 READY; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b1-G0 PASSED; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b1-G1 PASSED; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b1-G2 PASSED; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b1-G3 PASSED; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b2-G2 PASSED; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b2-G3 PASSED; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b2-G0 PASSED; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b2-G1 PASSED; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b3-G1 PASSED; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b3-G0 PASSED; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b3-G3 PASSED; raw logs/state/receipts saved. 

f-itinerary_queryHistory-b3-G2 PASSED; raw logs/state/receipts saved. 

p-itinerary_saveAndQueryHistory-G0 READY; raw logs/state/receipts saved. 

p-itinerary_saveAndQueryHistory-G1 READY; raw logs/state/receipts saved. 

p-itinerary_saveAndQueryHistory-G2 READY; raw logs/state/receipts saved. 

p-itinerary_saveAndQueryHistory-G3 READY; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b1-G0 PASSED; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b1-G1 PASSED; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b1-G2 PASSED; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b1-G3 PASSED; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b2-G2 PASSED; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b2-G3 PASSED; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b2-G0 PASSED; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b2-G1 PASSED; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b3-G1 PASSED; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b3-G0 PASSED; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b3-G3 PASSED; raw logs/state/receipts saved. 

f-itinerary_saveAndQueryHistory-b3-G2 PASSED; raw logs/state/receipts saved. 

p-raffle_registerAll-G0 READY; raw logs/state/receipts saved. 

p-raffle_registerAll-G1 READY; raw logs/state/receipts saved. 

p-raffle_registerAll-G2 READY; raw logs/state/receipts saved. 

p-raffle_registerAll-G3 READY; raw logs/state/receipts saved. 

f-raffle_registerAll-b1-G0 PASSED; raw logs/state/receipts saved. 

f-raffle_registerAll-b1-G1 PASSED; raw logs/state/receipts saved. 

f-raffle_registerAll-b1-G2 PASSED; raw logs/state/receipts saved. 

f-raffle_registerAll-b1-G3 PASSED; raw logs/state/receipts saved. 

f-raffle_registerAll-b2-G2 PASSED; raw logs/state/receipts saved. 

f-raffle_registerAll-b2-G3 PASSED; raw logs/state/receipts saved. 

f-raffle_registerAll-b2-G0 PASSED; raw logs/state/receipts saved. 

f-raffle_registerAll-b2-G1 PASSED; raw logs/state/receipts saved. 

f-raffle_registerAll-b3-G1 PASSED; raw logs/state/receipts saved. 

f-raffle_registerAll-b3-G0 PASSED; raw logs/state/receipts saved. 

f-raffle_registerAll-b3-G3 PASSED; raw logs/state/receipts saved. 

f-raffle_registerAll-b3-G2 PASSED; raw logs/state/receipts saved. 

p-raffle_query-G0 READY; raw logs/state/receipts saved. 

p-raffle_query-G1 READY; raw logs/state/receipts saved. 

p-raffle_query-G2 READY; raw logs/state/receipts saved. 

p-raffle_query-G3 READY; raw logs/state/receipts saved. 

f-raffle_query-b1-G0 PASSED; raw logs/state/receipts saved. 

f-raffle_query-b1-G1 PASSED; raw logs/state/receipts saved. 

f-raffle_query-b1-G2 PASSED; raw logs/state/receipts saved. 

f-raffle_query-b1-G3 PASSED; raw logs/state/receipts saved. 

f-raffle_query-b2-G2 PASSED; raw logs/state/receipts saved. 

f-raffle_query-b2-G3 PASSED; raw logs/state/receipts saved. 

f-raffle_query-b2-G0 PASSED; raw logs/state/receipts saved. 

f-raffle_query-b2-G1 PASSED; raw logs/state/receipts saved. 

f-raffle_query-b3-G1 PASSED; raw logs/state/receipts saved. 

f-raffle_query-b3-G0 PASSED; raw logs/state/receipts saved. 

f-raffle_query-b3-G3 PASSED; raw logs/state/receipts saved. 

f-raffle_query-b3-G2 PASSED; raw logs/state/receipts saved. 

p-raffle_raffle-G0 READY; raw logs/state/receipts saved. 

p-raffle_raffle-G1 READY; raw logs/state/receipts saved. 

p-raffle_raffle-G2 READY; raw logs/state/receipts saved. 

p-raffle_raffle-G3 READY; raw logs/state/receipts saved. 

f-raffle_raffle-b1-G0 FAILED_RUNTIME; raw logs/state/receipts saved. AssertionError(('num: 1, name: Alice, level: 1', 'num: 3, name: Carol, level: 1'))

p-raffle_registRaffle-G0 READY; raw logs/state/receipts saved. 

p-raffle_registRaffle-G1 READY; raw logs/state/receipts saved. 

p-raffle_registRaffle-G2 READY; raw logs/state/receipts saved. 

p-raffle_registRaffle-G3 READY; raw logs/state/receipts saved. 

f-raffle_registRaffle-b1-G0 PASSED; raw logs/state/receipts saved. 

f-raffle_registRaffle-b1-G1 PASSED; raw logs/state/receipts saved. 

f-raffle_registRaffle-b1-G2 PASSED; raw logs/state/receipts saved. 

f-raffle_registRaffle-b1-G3 PASSED; raw logs/state/receipts saved. 

f-raffle_registRaffle-b2-G2 PASSED; raw logs/state/receipts saved. 

f-raffle_registRaffle-b2-G3 PASSED; raw logs/state/receipts saved. 

f-raffle_registRaffle-b2-G0 PASSED; raw logs/state/receipts saved. 

f-raffle_registRaffle-b2-G1 PASSED; raw logs/state/receipts saved. 

f-raffle_registRaffle-b3-G1 PASSED; raw logs/state/receipts saved. 

f-raffle_registRaffle-b3-G0 PASSED; raw logs/state/receipts saved. 

f-raffle_registRaffle-b3-G3 PASSED; raw logs/state/receipts saved. 

f-raffle_registRaffle-b3-G2 PASSED; raw logs/state/receipts saved. 

p-fact_save-G0 READY; raw logs/state/receipts saved. 

p-fact_save-G1 READY; raw logs/state/receipts saved. 

p-fact_save-G2 READY; raw logs/state/receipts saved. 

p-fact_save-G3 READY; raw logs/state/receipts saved. 

f-fact_save-b1-G0 PASSED; raw logs/state/receipts saved. 

f-fact_save-b1-G1 PASSED; raw logs/state/receipts saved. 

f-fact_save-b1-G2 PASSED; raw logs/state/receipts saved. 

f-fact_save-b1-G3 PASSED; raw logs/state/receipts saved. 

f-fact_save-b2-G2 PASSED; raw logs/state/receipts saved. 

f-fact_save-b2-G3 PASSED; raw logs/state/receipts saved. 

f-fact_save-b2-G0 PASSED; raw logs/state/receipts saved. 

f-fact_save-b2-G1 PASSED; raw logs/state/receipts saved. 

f-fact_save-b3-G1 PASSED; raw logs/state/receipts saved. 

f-fact_save-b3-G0 PASSED; raw logs/state/receipts saved. 

f-fact_save-b3-G3 PASSED; raw logs/state/receipts saved. 

f-fact_save-b3-G2 PASSED; raw logs/state/receipts saved. 

p-fact_findByFileHash-G0 READY; raw logs/state/receipts saved. 

p-fact_findByFileHash-G1 READY; raw logs/state/receipts saved. 

p-fact_findByFileHash-G2 READY; raw logs/state/receipts saved. 

p-fact_findByFileHash-G3 READY; raw logs/state/receipts saved. 

f-fact_findByFileHash-b1-G0 PASSED; raw logs/state/receipts saved. 

f-fact_findByFileHash-b1-G1 PASSED; raw logs/state/receipts saved. 

f-fact_findByFileHash-b1-G2 PASSED; raw logs/state/receipts saved. 

f-fact_findByFileHash-b1-G3 PASSED; raw logs/state/receipts saved. 

f-fact_findByFileHash-b2-G2 PASSED; raw logs/state/receipts saved. 

f-fact_findByFileHash-b2-G3 PASSED; raw logs/state/receipts saved. 

f-fact_findByFileHash-b2-G0 PASSED; raw logs/state/receipts saved. 

f-fact_findByFileHash-b2-G1 PASSED; raw logs/state/receipts saved. 

f-fact_findByFileHash-b3-G1 PASSED; raw logs/state/receipts saved. 

f-fact_findByFileHash-b3-G0 PASSED; raw logs/state/receipts saved. 

f-fact_findByFileHash-b3-G3 PASSED; raw logs/state/receipts saved. 

f-fact_findByFileHash-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_balanceOf-G0 READY; raw logs/state/receipts saved. 

p-erc721_balanceOf-G1 READY; raw logs/state/receipts saved. 

p-erc721_balanceOf-G2 READY; raw logs/state/receipts saved. 

p-erc721_balanceOf-G3 READY; raw logs/state/receipts saved. 

f-erc721_balanceOf-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_balanceOf-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_balanceOf-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_balanceOf-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_balanceOf-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_balanceOf-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_balanceOf-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_balanceOf-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_balanceOf-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_balanceOf-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_balanceOf-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_balanceOf-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_ownerOf-G0 READY; raw logs/state/receipts saved. 

p-erc721_ownerOf-G1 READY; raw logs/state/receipts saved. 

p-erc721_ownerOf-G2 READY; raw logs/state/receipts saved. 

p-erc721_ownerOf-G3 READY; raw logs/state/receipts saved. 

f-erc721_ownerOf-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_ownerOf-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_ownerOf-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_ownerOf-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_ownerOf-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_ownerOf-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_ownerOf-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_ownerOf-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_ownerOf-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_ownerOf-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_ownerOf-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_ownerOf-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_getApproved-G0 READY; raw logs/state/receipts saved. 

p-erc721_getApproved-G1 READY; raw logs/state/receipts saved. 

p-erc721_getApproved-G2 READY; raw logs/state/receipts saved. 

p-erc721_getApproved-G3 READY; raw logs/state/receipts saved. 

f-erc721_getApproved-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_getApproved-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_getApproved-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_getApproved-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_getApproved-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_getApproved-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_getApproved-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_getApproved-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_getApproved-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_getApproved-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_getApproved-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_getApproved-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_tokenURI-G0 READY; raw logs/state/receipts saved. 

p-erc721_tokenURI-G1 READY; raw logs/state/receipts saved. 

p-erc721_tokenURI-G2 READY; raw logs/state/receipts saved. 

p-erc721_tokenURI-G3 READY; raw logs/state/receipts saved. 

f-erc721_tokenURI-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenURI-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenURI-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenURI-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenURI-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenURI-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenURI-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenURI-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenURI-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenURI-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenURI-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenURI-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_tokenMetadata-G0 READY; raw logs/state/receipts saved. 

p-erc721_tokenMetadata-G1 READY; raw logs/state/receipts saved. 

p-erc721_tokenMetadata-G2 READY; raw logs/state/receipts saved. 

p-erc721_tokenMetadata-G3 READY; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenMetadata-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_accountTokens-G0 READY; raw logs/state/receipts saved. 

p-erc721_accountTokens-G1 READY; raw logs/state/receipts saved. 

p-erc721_accountTokens-G2 READY; raw logs/state/receipts saved. 

p-erc721_accountTokens-G3 READY; raw logs/state/receipts saved. 

f-erc721_accountTokens-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_accountTokens-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_accountTokens-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_accountTokens-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_accountTokens-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_accountTokens-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_accountTokens-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_accountTokens-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_accountTokens-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_accountTokens-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_accountTokens-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_accountTokens-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_tokenLatestTxInfo-G0 READY; raw logs/state/receipts saved. 

p-erc721_tokenLatestTxInfo-G1 READY; raw logs/state/receipts saved. 

p-erc721_tokenLatestTxInfo-G2 READY; raw logs/state/receipts saved. 

p-erc721_tokenLatestTxInfo-G3 READY; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_tokenLatestTxInfo-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_name-G0 READY; raw logs/state/receipts saved. 

p-erc721_name-G1 READY; raw logs/state/receipts saved. 

p-erc721_name-G2 READY; raw logs/state/receipts saved. 

p-erc721_name-G3 READY; raw logs/state/receipts saved. 

f-erc721_name-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_name-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_name-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_name-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_name-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_name-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_name-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_name-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_name-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_name-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_name-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_name-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_symbol-G0 READY; raw logs/state/receipts saved. 

p-erc721_symbol-G1 READY; raw logs/state/receipts saved. 

p-erc721_symbol-G2 READY; raw logs/state/receipts saved. 

p-erc721_symbol-G3 READY; raw logs/state/receipts saved. 

f-erc721_symbol-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_symbol-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_symbol-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_symbol-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_symbol-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_symbol-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_symbol-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_symbol-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_symbol-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_symbol-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_symbol-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_symbol-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_setApprovalForAll2-G0 READY; raw logs/state/receipts saved. 

p-erc721_setApprovalForAll2-G1 READY; raw logs/state/receipts saved. 

p-erc721_setApprovalForAll2-G2 READY; raw logs/state/receipts saved. 

p-erc721_setApprovalForAll2-G3 READY; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_setApprovalForAll2-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_approve-G0 READY; raw logs/state/receipts saved. 

p-erc721_approve-G1 READY; raw logs/state/receipts saved. 

p-erc721_approve-G2 READY; raw logs/state/receipts saved. 

p-erc721_approve-G3 READY; raw logs/state/receipts saved. 

f-erc721_approve-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_approve-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_approve-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_approve-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_approve-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_approve-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_approve-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_approve-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_approve-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_approve-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_approve-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_approve-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_transferFrom-G0 READY; raw logs/state/receipts saved. 

p-erc721_transferFrom-G1 READY; raw logs/state/receipts saved. 

p-erc721_transferFrom-G2 READY; raw logs/state/receipts saved. 

p-erc721_transferFrom-G3 READY; raw logs/state/receipts saved. 

f-erc721_transferFrom-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_transferFrom-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_transferFrom-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_transferFrom-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_transferFrom-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_transferFrom-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_transferFrom-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_transferFrom-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_transferFrom-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_transferFrom-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_transferFrom-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_transferFrom-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_mint2-G0 READY; raw logs/state/receipts saved. 

p-erc721_mint2-G1 READY; raw logs/state/receipts saved. 

p-erc721_mint2-G2 READY; raw logs/state/receipts saved. 

p-erc721_mint2-G3 READY; raw logs/state/receipts saved. 

f-erc721_mint2-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_mint2-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_mint2-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_mint2-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_mint2-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_mint2-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_mint2-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_mint2-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_mint2-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_mint2-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_mint2-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_mint2-b3-G2 PASSED; raw logs/state/receipts saved. 

p-compute_bigNumCal-G0 READY; raw logs/state/receipts saved. 

p-compute_bigNumCal-G1 READY; raw logs/state/receipts saved. 

p-compute_bigNumCal-G2 READY; raw logs/state/receipts saved. 

p-compute_bigNumCal-G3 READY; raw logs/state/receipts saved. 

f-compute_bigNumCal-b1-G0 PASSED; raw logs/state/receipts saved. 

f-compute_bigNumCal-b1-G1 PASSED; raw logs/state/receipts saved. 

f-compute_bigNumCal-b1-G2 PASSED; raw logs/state/receipts saved. 

f-compute_bigNumCal-b1-G3 PASSED; raw logs/state/receipts saved. 

f-compute_bigNumCal-b2-G2 PASSED; raw logs/state/receipts saved. 

f-compute_bigNumCal-b2-G3 PASSED; raw logs/state/receipts saved. 

f-compute_bigNumCal-b2-G0 PASSED; raw logs/state/receipts saved. 

f-compute_bigNumCal-b2-G1 PASSED; raw logs/state/receipts saved. 

f-compute_bigNumCal-b3-G1 PASSED; raw logs/state/receipts saved. 

f-compute_bigNumCal-b3-G0 PASSED; raw logs/state/receipts saved. 

f-compute_bigNumCal-b3-G3 PASSED; raw logs/state/receipts saved. 

f-compute_bigNumCal-b3-G2 PASSED; raw logs/state/receipts saved. 

p-compute_hashCal-G0 READY; raw logs/state/receipts saved. 

p-compute_hashCal-G1 READY; raw logs/state/receipts saved. 

p-compute_hashCal-G2 READY; raw logs/state/receipts saved. 

p-compute_hashCal-G3 READY; raw logs/state/receipts saved. 

f-compute_hashCal-b1-G0 PASSED; raw logs/state/receipts saved. 

f-compute_hashCal-b1-G1 PASSED; raw logs/state/receipts saved. 

f-compute_hashCal-b1-G2 PASSED; raw logs/state/receipts saved. 

f-compute_hashCal-b1-G3 PASSED; raw logs/state/receipts saved. 

f-compute_hashCal-b2-G2 PASSED; raw logs/state/receipts saved. 

f-compute_hashCal-b2-G3 PASSED; raw logs/state/receipts saved. 

f-compute_hashCal-b2-G0 PASSED; raw logs/state/receipts saved. 

f-compute_hashCal-b2-G1 PASSED; raw logs/state/receipts saved. 

f-compute_hashCal-b3-G1 PASSED; raw logs/state/receipts saved. 

f-compute_hashCal-b3-G0 PASSED; raw logs/state/receipts saved. 

f-compute_hashCal-b3-G3 PASSED; raw logs/state/receipts saved. 

f-compute_hashCal-b3-G2 PASSED; raw logs/state/receipts saved. 

p-compute_normalCal-G0 READY; raw logs/state/receipts saved. 

p-compute_normalCal-G1 READY; raw logs/state/receipts saved. 

p-compute_normalCal-G2 READY; raw logs/state/receipts saved. 

p-compute_normalCal-G3 READY; raw logs/state/receipts saved. 

f-compute_normalCal-b1-G0 PASSED; raw logs/state/receipts saved. 

f-compute_normalCal-b1-G1 PASSED; raw logs/state/receipts saved. 

f-compute_normalCal-b1-G2 PASSED; raw logs/state/receipts saved. 

f-compute_normalCal-b1-G3 PASSED; raw logs/state/receipts saved. 

f-compute_normalCal-b2-G2 PASSED; raw logs/state/receipts saved. 

f-compute_normalCal-b2-G3 PASSED; raw logs/state/receipts saved. 

f-compute_normalCal-b2-G0 PASSED; raw logs/state/receipts saved. 

f-compute_normalCal-b2-G1 PASSED; raw logs/state/receipts saved. 

f-compute_normalCal-b3-G1 PASSED; raw logs/state/receipts saved. 

f-compute_normalCal-b3-G0 PASSED; raw logs/state/receipts saved. 

f-compute_normalCal-b3-G3 PASSED; raw logs/state/receipts saved. 

f-compute_normalCal-b3-G2 PASSED; raw logs/state/receipts saved. 

p-fact_saveAndFindByFileHash-G0 READY; raw logs/state/receipts saved. 

p-fact_saveAndFindByFileHash-G1 READY; raw logs/state/receipts saved. 

p-fact_saveAndFindByFileHash-G2 READY; raw logs/state/receipts saved. 

p-fact_saveAndFindByFileHash-G3 READY; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b1-G0 PASSED; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b1-G1 PASSED; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b1-G2 PASSED; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b1-G3 PASSED; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b2-G2 PASSED; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b2-G3 PASSED; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b2-G0 PASSED; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b2-G1 PASSED; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b3-G1 PASSED; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b3-G0 PASSED; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b3-G3 PASSED; raw logs/state/receipts saved. 

f-fact_saveAndFindByFileHash-b3-G2 PASSED; raw logs/state/receipts saved. 

p-erc721_mint-G0 READY; raw logs/state/receipts saved. 

p-erc721_mint-G1 READY; raw logs/state/receipts saved. 

p-erc721_mint-G2 READY; raw logs/state/receipts saved. 

p-erc721_mint-G3 READY; raw logs/state/receipts saved. 

f-erc721_mint-b1-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_mint-b1-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_mint-b1-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_mint-b1-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_mint-b2-G2 PASSED; raw logs/state/receipts saved. 

f-erc721_mint-b2-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_mint-b2-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_mint-b2-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_mint-b3-G1 PASSED; raw logs/state/receipts saved. 

f-erc721_mint-b3-G0 PASSED; raw logs/state/receipts saved. 

f-erc721_mint-b3-G3 PASSED; raw logs/state/receipts saved. 

f-erc721_mint-b3-G2 PASSED; raw logs/state/receipts saved. 

p-exchange_buyNow-G0 READY; raw logs/state/receipts saved. 

p-exchange_buyNow-G1 READY; raw logs/state/receipts saved. 

p-exchange_buyNow-G2 READY; raw logs/state/receipts saved. 

p-exchange_buyNow-G3 READY; raw logs/state/receipts saved. 

f-exchange_buyNow-b1-G0 PASSED; raw logs/state/receipts saved. 

f-exchange_buyNow-b1-G1 PASSED; raw logs/state/receipts saved. 

f-exchange_buyNow-b1-G2 PASSED; raw logs/state/receipts saved. 

f-exchange_buyNow-b1-G3 PASSED; raw logs/state/receipts saved. 

f-exchange_buyNow-b2-G2 PASSED; raw logs/state/receipts saved. 

f-exchange_buyNow-b2-G3 PASSED; raw logs/state/receipts saved. 

f-exchange_buyNow-b2-G0 PASSED; raw logs/state/receipts saved. 

f-exchange_buyNow-b2-G1 PASSED; raw logs/state/receipts saved. 

f-exchange_buyNow-b3-G1 PASSED; raw logs/state/receipts saved. 

f-exchange_buyNow-b3-G0 PASSED; raw logs/state/receipts saved. 

f-exchange_buyNow-b3-G3 PASSED; raw logs/state/receipts saved. 

f-exchange_buyNow-b3-G2 PASSED; raw logs/state/receipts saved. 

p-identity_callerAddress-G0 READY; raw logs/state/receipts saved. 

p-identity_callerAddress-G1 READY; raw logs/state/receipts saved. 

p-identity_callerAddress-G2 READY; raw logs/state/receipts saved. 

p-identity_callerAddress-G3 READY; raw logs/state/receipts saved. 

f-identity_callerAddress-b1-G0 PASSED; raw logs/state/receipts saved. 

f-identity_callerAddress-b1-G1 PASSED; raw logs/state/receipts saved. 

f-identity_callerAddress-b1-G2 PASSED; raw logs/state/receipts saved. 

f-identity_callerAddress-b1-G3 PASSED; raw logs/state/receipts saved. 

f-identity_callerAddress-b2-G2 PASSED; raw logs/state/receipts saved. 

f-identity_callerAddress-b2-G3 PASSED; raw logs/state/receipts saved. 

f-identity_callerAddress-b2-G0 PASSED; raw logs/state/receipts saved. 

f-identity_callerAddress-b2-G1 PASSED; raw logs/state/receipts saved. 

f-identity_callerAddress-b3-G1 PASSED; raw logs/state/receipts saved. 

f-identity_callerAddress-b3-G0 PASSED; raw logs/state/receipts saved. 

f-identity_callerAddress-b3-G3 PASSED; raw logs/state/receipts saved. 

f-identity_callerAddress-b3-G2 PASSED; raw logs/state/receipts saved. 

Main matrix finished36methods; raffle_raffle initial4-draw window failed finite3-person fixture (observed winnersCarol/Alice/Bob then GuestExit2). Preserve all4attempts. Revision1: same people/algorithm/timestamp, exactly3valid draws with sequential expected winners, 3-call precheck then3batches, independent new ledgers/labels; no old failed samples pooled. All other formal data frozen. Next retry then restart/readback/error checks, no new optimization.

r1-raffle_raffle-b0-G0 READY; raw logs/state/receipts saved. 

r1-raffle_raffle-b0-G1 READY; raw logs/state/receipts saved. 

r1-raffle_raffle-b0-G2 READY; raw logs/state/receipts saved. 

r1-raffle_raffle-b0-G3 READY; raw logs/state/receipts saved. 

Raffle revision1 batch0 all4groups PASS, receipts/state/gas parity.

r1-raffle_raffle-b1-G0 PASSED; raw logs/state/receipts saved. 

r1-raffle_raffle-b1-G1 PASSED; raw logs/state/receipts saved. 

r1-raffle_raffle-b1-G2 PASSED; raw logs/state/receipts saved. 

r1-raffle_raffle-b1-G3 PASSED; raw logs/state/receipts saved. 

Raffle revision1 batch1 all4groups PASS, receipts/state/gas parity.

r1-raffle_raffle-b2-G2 PASSED; raw logs/state/receipts saved. 

r1-raffle_raffle-b2-G3 PASSED; raw logs/state/receipts saved. 

r1-raffle_raffle-b2-G0 PASSED; raw logs/state/receipts saved. 

r1-raffle_raffle-b2-G1 PASSED; raw logs/state/receipts saved. 

Raffle revision1 batch2 all4groups PASS, receipts/state/gas parity.

r1-raffle_raffle-b3-G1 PASSED; raw logs/state/receipts saved. 

r1-raffle_raffle-b3-G0 PASSED; raw logs/state/receipts saved. 

r1-raffle_raffle-b3-G3 PASSED; raw logs/state/receipts saved. 

r1-raffle_raffle-b3-G2 PASSED; raw logs/state/receipts saved. 

Raffle revision1 batch3 all4groups PASS, receipts/state/gas parity.

Postcheck post-bigInput_inputSize-G0 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-bigInput_inputSize-b3-G0-case.json

Postcheck post-bigInput_inputSize-G1 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-bigInput_inputSize-b3-G1-case.json

Postcheck post-bigInput_inputSize-G2 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-bigInput_inputSize-b3-G2-case.json

Postcheck post-bigInput_inputSize-G3 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-bigInput_inputSize-b3-G3-case.json

Postcheck post-bigInput_inputSizeMulti-G0 PASS; committed tx/readback verified after restart, sourcef-bigInput_inputSizeMulti-b3-G0-case.json

Postcheck post-bigInput_inputSizeMulti-G1 PASS; committed tx/readback verified after restart, sourcef-bigInput_inputSizeMulti-b3-G1-case.json

Postcheck post-bigInput_inputSizeMulti-G2 PASS; committed tx/readback verified after restart, sourcef-bigInput_inputSizeMulti-b3-G2-case.json

Postcheck post-bigInput_inputSizeMulti-G3 PASS; committed tx/readback verified after restart, sourcef-bigInput_inputSizeMulti-b3-G3-case.json

Postcheck post-bigInput_ioHeavy-G0 PASS; committed tx/readback verified after restart, sourcef-bigInput_ioHeavy-b3-G0-case.json

Postcheck post-bigInput_ioHeavy-G1 PASS; committed tx/readback verified after restart, sourcef-bigInput_ioHeavy-b3-G1-case.json

Postcheck post-bigInput_ioHeavy-G2 PASS; committed tx/readback verified after restart, sourcef-bigInput_ioHeavy-b3-G2-case.json

Postcheck post-bigInput_ioHeavy-G3 PASS; committed tx/readback verified after restart, sourcef-bigInput_ioHeavy-b3-G3-case.json

Postcheck post-compute_bigNumCal-G0 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-compute_bigNumCal-b3-G0-case.json

Postcheck post-compute_bigNumCal-G1 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-compute_bigNumCal-b3-G1-case.json

Postcheck post-compute_bigNumCal-G2 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-compute_bigNumCal-b3-G2-case.json

Postcheck post-compute_bigNumCal-G3 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-compute_bigNumCal-b3-G3-case.json

Postcheck post-compute_hashCal-G0 PASS; committed tx/readback verified after restart, sourcef-compute_hashCal-b3-G0-case.json

Postcheck post-compute_hashCal-G1 PASS; committed tx/readback verified after restart, sourcef-compute_hashCal-b3-G1-case.json

Postcheck post-compute_hashCal-G2 PASS; committed tx/readback verified after restart, sourcef-compute_hashCal-b3-G2-case.json

Postcheck post-compute_hashCal-G3 PASS; committed tx/readback verified after restart, sourcef-compute_hashCal-b3-G3-case.json

Postcheck post-compute_normalCal-G0 PASS; committed tx/readback verified after restart, sourcef-compute_normalCal-b3-G0-case.json

Postcheck post-compute_normalCal-G1 PASS; committed tx/readback verified after restart, sourcef-compute_normalCal-b3-G1-case.json

Postcheck post-compute_normalCal-G2 PASS; committed tx/readback verified after restart, sourcef-compute_normalCal-b3-G2-case.json

Postcheck post-compute_normalCal-G3 PASS; committed tx/readback verified after restart, sourcef-compute_normalCal-b3-G3-case.json

Postcheck post-erc721_accountTokens-G0 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-erc721_accountTokens-b3-G0-case.json

Postcheck post-erc721_accountTokens-G1 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-erc721_accountTokens-b3-G1-case.json

Postcheck post-erc721_accountTokens-G2 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-erc721_accountTokens-b3-G2-case.json

Postcheck post-erc721_accountTokens-G3 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-erc721_accountTokens-b3-G3-case.json

Postcheck post-erc721_approve-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_approve-b3-G0-case.json

Postcheck post-erc721_approve-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_approve-b3-G1-case.json

Postcheck post-erc721_approve-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_approve-b3-G2-case.json

Postcheck post-erc721_approve-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_approve-b3-G3-case.json

Postcheck post-erc721_balanceOf-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_balanceOf-b3-G0-case.json

Postcheck post-erc721_balanceOf-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_balanceOf-b3-G1-case.json

Postcheck post-erc721_balanceOf-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_balanceOf-b3-G2-case.json

Postcheck post-erc721_balanceOf-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_balanceOf-b3-G3-case.json

Postcheck post-erc721_getApproved-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_getApproved-b3-G0-case.json

Postcheck post-erc721_getApproved-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_getApproved-b3-G1-case.json

Postcheck post-erc721_getApproved-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_getApproved-b3-G2-case.json

Postcheck post-erc721_getApproved-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_getApproved-b3-G3-case.json

Postcheck post-erc721_mint-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_mint-b3-G0-case.json

Postcheck post-erc721_mint-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_mint-b3-G1-case.json

Postcheck post-erc721_mint-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_mint-b3-G2-case.json

Postcheck post-erc721_mint-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_mint-b3-G3-case.json

Postcheck post-erc721_mint2-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_mint2-b3-G0-case.json

Postcheck post-erc721_mint2-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_mint2-b3-G1-case.json

Postcheck post-erc721_mint2-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_mint2-b3-G2-case.json

Postcheck post-erc721_mint2-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_mint2-b3-G3-case.json

Postcheck post-erc721_name-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_name-b3-G0-case.json

Postcheck post-erc721_name-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_name-b3-G1-case.json

Postcheck post-erc721_name-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_name-b3-G2-case.json

Postcheck post-erc721_name-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_name-b3-G3-case.json

Postcheck post-erc721_ownerOf-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_ownerOf-b3-G0-case.json

Postcheck post-erc721_ownerOf-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_ownerOf-b3-G1-case.json

Postcheck post-erc721_ownerOf-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_ownerOf-b3-G2-case.json

Postcheck post-erc721_ownerOf-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_ownerOf-b3-G3-case.json

Postcheck post-erc721_setApprovalForAll2-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_setApprovalForAll2-b3-G0-case.json

Postcheck post-erc721_setApprovalForAll2-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_setApprovalForAll2-b3-G1-case.json

Postcheck post-erc721_setApprovalForAll2-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_setApprovalForAll2-b3-G2-case.json

Postcheck post-erc721_setApprovalForAll2-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_setApprovalForAll2-b3-G3-case.json

Postcheck post-erc721_symbol-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_symbol-b3-G0-case.json

Postcheck post-erc721_symbol-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_symbol-b3-G1-case.json

Postcheck post-erc721_symbol-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_symbol-b3-G2-case.json

Postcheck post-erc721_symbol-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_symbol-b3-G3-case.json

Postcheck post-erc721_tokenLatestTxInfo-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenLatestTxInfo-b3-G0-case.json

Postcheck post-erc721_tokenLatestTxInfo-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenLatestTxInfo-b3-G1-case.json

Postcheck post-erc721_tokenLatestTxInfo-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenLatestTxInfo-b3-G2-case.json

Postcheck post-erc721_tokenLatestTxInfo-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenLatestTxInfo-b3-G3-case.json

Postcheck post-erc721_tokenMetadata-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenMetadata-b3-G0-case.json

Postcheck post-erc721_tokenMetadata-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenMetadata-b3-G1-case.json

Postcheck post-erc721_tokenMetadata-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenMetadata-b3-G2-case.json

Postcheck post-erc721_tokenMetadata-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenMetadata-b3-G3-case.json

Postcheck post-erc721_tokenURI-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenURI-b3-G0-case.json

Postcheck post-erc721_tokenURI-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenURI-b3-G1-case.json

Postcheck post-erc721_tokenURI-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenURI-b3-G2-case.json

Postcheck post-erc721_tokenURI-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_tokenURI-b3-G3-case.json

Postcheck post-erc721_transferFrom-G0 PASS; committed tx/readback verified after restart, sourcef-erc721_transferFrom-b3-G0-case.json

Postcheck post-erc721_transferFrom-G1 PASS; committed tx/readback verified after restart, sourcef-erc721_transferFrom-b3-G1-case.json

Postcheck post-erc721_transferFrom-G2 PASS; committed tx/readback verified after restart, sourcef-erc721_transferFrom-b3-G2-case.json

Postcheck post-erc721_transferFrom-G3 PASS; committed tx/readback verified after restart, sourcef-erc721_transferFrom-b3-G3-case.json

Postcheck post-exchange_buyNow-G0 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-exchange_buyNow-b3-G0-case.json

Postcheck post-exchange_buyNow-G1 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-exchange_buyNow-b3-G1-case.json

Postcheck post-exchange_buyNow-G2 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-exchange_buyNow-b3-G2-case.json

Postcheck post-exchange_buyNow-G3 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-exchange_buyNow-b3-G3-case.json

Postcheck post-fact_findByFileHash-G0 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-fact_findByFileHash-b3-G0-case.json

Postcheck post-fact_findByFileHash-G1 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-fact_findByFileHash-b3-G1-case.json

Postcheck post-fact_findByFileHash-G2 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-fact_findByFileHash-b3-G2-case.json

Postcheck post-fact_findByFileHash-G3 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-fact_findByFileHash-b3-G3-case.json

Postcheck post-fact_save-G0 PASS; committed tx/readback verified after restart, sourcef-fact_save-b3-G0-case.json

Postcheck post-fact_save-G1 PASS; committed tx/readback verified after restart, sourcef-fact_save-b3-G1-case.json

Postcheck post-fact_save-G2 PASS; committed tx/readback verified after restart, sourcef-fact_save-b3-G2-case.json

Postcheck post-fact_save-G3 PASS; committed tx/readback verified after restart, sourcef-fact_save-b3-G3-case.json

Postcheck post-fact_saveAndFindByFileHash-G0 PASS; committed tx/readback verified after restart, sourcef-fact_saveAndFindByFileHash-b3-G0-case.json

Postcheck post-fact_saveAndFindByFileHash-G1 PASS; committed tx/readback verified after restart, sourcef-fact_saveAndFindByFileHash-b3-G1-case.json

Postcheck post-fact_saveAndFindByFileHash-G2 PASS; committed tx/readback verified after restart, sourcef-fact_saveAndFindByFileHash-b3-G2-case.json

Postcheck post-fact_saveAndFindByFileHash-G3 PASS; committed tx/readback verified after restart, sourcef-fact_saveAndFindByFileHash-b3-G3-case.json

Postcheck post-identity_addWriteList-G0 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-identity_addWriteList-b3-G0-case.json

Postcheck post-identity_addWriteList-G1 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-identity_addWriteList-b3-G1-case.json

Postcheck post-identity_addWriteList-G2 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-identity_addWriteList-b3-G2-case.json

Postcheck post-identity_addWriteList-G3 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-identity_addWriteList-b3-G3-case.json

Postcheck post-identity_address-G0 PASS; committed tx/readback verified after restart, sourcef-identity_address-b3-G0-case.json

Postcheck post-identity_address-G1 PASS; committed tx/readback verified after restart, sourcef-identity_address-b3-G1-case.json

Postcheck post-identity_address-G2 PASS; committed tx/readback verified after restart, sourcef-identity_address-b3-G2-case.json

Postcheck post-identity_address-G3 PASS; committed tx/readback verified after restart, sourcef-identity_address-b3-G3-case.json

Postcheck post-identity_alterAdminAddress-G0 PASS; committed tx/readback verified after restart, sourcef-identity_alterAdminAddress-b3-G0-case.json

Postcheck post-identity_alterAdminAddress-G1 PASS; committed tx/readback verified after restart, sourcef-identity_alterAdminAddress-b3-G1-case.json

Postcheck post-identity_alterAdminAddress-G2 PASS; committed tx/readback verified after restart, sourcef-identity_alterAdminAddress-b3-G2-case.json

Postcheck post-identity_alterAdminAddress-G3 PASS; committed tx/readback verified after restart, sourcef-identity_alterAdminAddress-b3-G3-case.json

Postcheck post-identity_callerAddress-G0 PASS; committed tx/readback verified after restart, sourcef-identity_callerAddress-b3-G0-case.json

Postcheck post-identity_callerAddress-G1 PASS; committed tx/readback verified after restart, sourcef-identity_callerAddress-b3-G1-case.json

Postcheck post-identity_callerAddress-G2 PASS; committed tx/readback verified after restart, sourcef-identity_callerAddress-b3-G2-case.json

Postcheck post-identity_callerAddress-G3 PASS; committed tx/readback verified after restart, sourcef-identity_callerAddress-b3-G3-case.json

Postcheck post-identity_isApprovedUser-G0 PASS; committed tx/readback verified after restart, sourcef-identity_isApprovedUser-b3-G0-case.json

Postcheck post-identity_isApprovedUser-G1 PASS; committed tx/readback verified after restart, sourcef-identity_isApprovedUser-b3-G1-case.json

Postcheck post-identity_isApprovedUser-G2 PASS; committed tx/readback verified after restart, sourcef-identity_isApprovedUser-b3-G2-case.json

Postcheck post-identity_isApprovedUser-G3 PASS; committed tx/readback verified after restart, sourcef-identity_isApprovedUser-b3-G3-case.json

Postcheck post-identity_removeWriteList-G0 PASS; committed tx/readback verified after restart, sourcef-identity_removeWriteList-b3-G0-case.json

Postcheck post-identity_removeWriteList-G1 PASS; committed tx/readback verified after restart, sourcef-identity_removeWriteList-b3-G1-case.json

Postcheck post-identity_removeWriteList-G2 PASS; committed tx/readback verified after restart, sourcef-identity_removeWriteList-b3-G2-case.json

Postcheck post-identity_removeWriteList-G3 PASS; committed tx/readback verified after restart, sourcef-identity_removeWriteList-b3-G3-case.json

Postcheck post-itinerary_queryHistory-G0 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-itinerary_queryHistory-b3-G0-case.json

Postcheck post-itinerary_queryHistory-G1 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-itinerary_queryHistory-b3-G1-case.json

Postcheck post-itinerary_queryHistory-G2 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-itinerary_queryHistory-b3-G2-case.json

Postcheck post-itinerary_queryHistory-G3 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-itinerary_queryHistory-b3-G3-case.json

Postcheck post-itinerary_save-G0 PASS; committed tx/readback verified after restart, sourcef-itinerary_save-b3-G0-case.json

Postcheck post-itinerary_save-G1 PASS; committed tx/readback verified after restart, sourcef-itinerary_save-b3-G1-case.json

Postcheck post-itinerary_save-G2 PASS; committed tx/readback verified after restart, sourcef-itinerary_save-b3-G2-case.json

Postcheck post-itinerary_save-G3 PASS; committed tx/readback verified after restart, sourcef-itinerary_save-b3-G3-case.json

Postcheck post-itinerary_saveAndQueryHistory-G0 PASS; committed tx/readback verified after restart, sourcef-itinerary_saveAndQueryHistory-b3-G0-case.json

Postcheck post-itinerary_saveAndQueryHistory-G1 PASS; committed tx/readback verified after restart, sourcef-itinerary_saveAndQueryHistory-b3-G1-case.json

Postcheck post-itinerary_saveAndQueryHistory-G2 PASS; committed tx/readback verified after restart, sourcef-itinerary_saveAndQueryHistory-b3-G2-case.json

Postcheck post-itinerary_saveAndQueryHistory-G3 PASS; committed tx/readback verified after restart, sourcef-itinerary_saveAndQueryHistory-b3-G3-case.json

Postcheck post-raffle_query-G0 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-raffle_query-b3-G0-case.json

Postcheck post-raffle_query-G1 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-raffle_query-b3-G1-case.json

Postcheck post-raffle_query-G2 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-raffle_query-b3-G2-case.json

Postcheck post-raffle_query-G3 PASS; committed tx/readback + genuine error rollback verified after restart, sourcef-raffle_query-b3-G3-case.json

Postcheck post-raffle_registRaffle-G0 PASS; committed tx/readback verified after restart, sourcef-raffle_registRaffle-b3-G0-case.json

Postcheck post-raffle_registRaffle-G1 PASS; committed tx/readback verified after restart, sourcef-raffle_registRaffle-b3-G1-case.json

Postcheck post-raffle_registRaffle-G2 PASS; committed tx/readback verified after restart, sourcef-raffle_registRaffle-b3-G2-case.json

Postcheck post-raffle_registRaffle-G3 PASS; committed tx/readback verified after restart, sourcef-raffle_registRaffle-b3-G3-case.json

Postcheck post-raffle_registerAll-G0 PASS; committed tx/readback verified after restart, sourcef-raffle_registerAll-b3-G0-case.json

Postcheck post-raffle_registerAll-G1 PASS; committed tx/readback verified after restart, sourcef-raffle_registerAll-b3-G1-case.json

Postcheck post-raffle_registerAll-G2 PASS; committed tx/readback verified after restart, sourcef-raffle_registerAll-b3-G2-case.json

Postcheck post-raffle_registerAll-G3 PASS; committed tx/readback verified after restart, sourcef-raffle_registerAll-b3-G3-case.json

Postcheck post-raffle_raffle-G0 PASS; committed tx/readback + genuine error rollback verified after restart, sourcer1-raffle_raffle-b3-G0-case.json

Postcheck post-raffle_raffle-G1 PASS; committed tx/readback + genuine error rollback verified after restart, sourcer1-raffle_raffle-b3-G1-case.json

Postcheck post-raffle_raffle-G2 PASS; committed tx/readback + genuine error rollback verified after restart, sourcer1-raffle_raffle-b3-G2-case.json

Postcheck post-raffle_raffle-G3 PASS; committed tx/readback + genuine error rollback verified after restart, sourcer1-raffle_raffle-b3-G3-case.json

## 最终恢复点：正式实验与重启复核全部完成

- 所有8合约/37业务方法四组PASSED，3批；1728有效正式提交、444窗口。
- raffle原失败保留；revision1同三人名单3次完整执行，3批每组9次。
- 148次重启交易/状态回读及36次真实错误回滚完成，无共享STOP守卫触发。
- python3 scripts/analyze.py 已完成：audit/recompute.json。
- python3 scripts/report.py 已完成：audit/final-counts.json及结果报告。
- python3 scripts/stages.py 已完成：NODE_STAGES.csv，1728笔全部匹配PutBlock/RPC。
- python3 -m py_compile scripts/*.py 通过；无运行中的step36 systemd任务。
- 762份/proc加载maps均指向冻结Selector修复库；源码/二进制/环境/配置审计已保存。
- 剩余收尾：记录独立分支提交、生成文件清单与镜像供IDE阅读。无待补跑的正式方法。
- 不再执行experiment.py/retry_raffle.py/postcheck_all.py；如需复算仅执行analyze.py、report.py、stages.py，均不启动节点。

### 收尾完成
正式数据与报告已提交独立CVW分支，数据提交c095285b；节点集成提交c28bfa8。未推送。所有测试进程退出。镜像到CVW同名新实验目录仅供阅读，不覆盖历史目录。后续只需读取RESULTS.md和CSV，无待执行性能实验。
