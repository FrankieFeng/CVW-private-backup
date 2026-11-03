# CVW-SHA-NEGATIVE-5

Base CVW39E ddae029a; reuse existingnode-ready (sourcec6382c3), client3 andnativeSelectorpatched56b236ce. No VM/node/native/common/sync change or rebuild. Fivegroups G0Fresh G1Copy G2A-only G3A+Copy G4A+Copy+SHA.

Plan:6deploymentseeds(3contracts plain/A);25one-target SDK prechecks; then3independentmatchedbatches acrossall5methods/5variants.5targetcalls perbatch exceptraffle3(original3-persondrawfixture). Totalformal345targets. Same-nodeTxID linksVM/SDK; batch-levelmatchedwindowMEAN differences, no cross-nodeper-transactionsplicing. Raffle3drawsequenceCarol/Alice/Bob unchanged.

Startupuses39E componentstages+consumercompletedcounts+samequeuedoubleACK+realSDKprobe. ForERC/raffle firstactualsetup(mint/registerAll)servesasrealcommitprobe; no targetdrawconsumedbeforewindow. Identity usesactualtargetprobe. WarmQuerydoesnotpersistwrites. Guard1536MiB/220threads/32rootcallsunchanged. Stoponanycorrectness/ready/resourceerror; keepnegatives.

Pre-runtime setup failures retained: Python conditional typo corrected beforeexecution; configuration archive is39E/evidence/configuration (notaudit). Originalseed-identity-plain attemptneverstartednodeorSDK; failedemptydirectory/resultretained. Correctedtemplateandusefreshseed-v1names, no originalfilesoverwritten.

Seed seed-v1-identity-plain PASS, deployment only, no performance samples.

Seed seed-v1-identity-A PASS, deployment only, no performance samples.

Seed seed-v1-erc721-plain PASS, deployment only, no performance samples.

Seed seed-v1-erc721-A PASS, deployment only, no performance samples.

Seed seed-v1-raffle-plain PASS, deployment only, no performance samples.

Seed seed-v1-raffle-A PASS, deployment only, no performance samples.

pre-identity_address-G0 True 

pre-identity_address-G1 True 

pre-identity_address-G2 True 

pre-identity_address-G3 True 

pre-identity_address-G4 True 

pre-identity_callerAddress-G0 True 

pre-identity_callerAddress-G1 True 

pre-identity_callerAddress-G2 True 

pre-identity_callerAddress-G3 True 

pre-identity_callerAddress-G4 True 

pre-erc721_balanceOf-G0 True 

pre-erc721_balanceOf-G1 True 

pre-erc721_balanceOf-G2 True 

pre-erc721_balanceOf-G3 True 

pre-erc721_balanceOf-G4 True 

pre-erc721_tokenLatestTxInfo-G0 True 

pre-erc721_tokenLatestTxInfo-G1 True 

pre-erc721_tokenLatestTxInfo-G2 True 

pre-erc721_tokenLatestTxInfo-G3 True 

pre-erc721_tokenLatestTxInfo-G4 True 

pre-raffle_raffle-G0 True 

pre-raffle_raffle-G1 True 

pre-raffle_raffle-G2 True 

pre-raffle_raffle-G3 True 

pre-raffle_raffle-G4 True 

formal-identity_address-b1-G0 True 

formal-identity_address-b1-G1 True 

formal-identity_address-b1-G2 True 

formal-identity_address-b1-G3 True 

formal-identity_address-b1-G4 True 

formal-identity_callerAddress-b1-G1 True 

formal-identity_callerAddress-b1-G2 True 

formal-identity_callerAddress-b1-G3 True 

formal-identity_callerAddress-b1-G4 True 

formal-identity_callerAddress-b1-G0 True 

formal-erc721_balanceOf-b1-G2 True 

formal-erc721_balanceOf-b1-G3 True 

formal-erc721_balanceOf-b1-G4 True 

formal-erc721_balanceOf-b1-G0 True 

formal-erc721_balanceOf-b1-G1 True 

formal-erc721_tokenLatestTxInfo-b1-G3 True 

formal-erc721_tokenLatestTxInfo-b1-G4 True 

formal-erc721_tokenLatestTxInfo-b1-G0 True 

formal-erc721_tokenLatestTxInfo-b1-G1 True 

formal-erc721_tokenLatestTxInfo-b1-G2 True 

formal-raffle_raffle-b1-G4 True 

formal-raffle_raffle-b1-G0 True 

formal-raffle_raffle-b1-G1 True 

formal-raffle_raffle-b1-G2 True 

formal-raffle_raffle-b1-G3 True 

formal-identity_address-b2-G4 True 

formal-identity_address-b2-G3 True 

formal-identity_address-b2-G2 True 

formal-identity_address-b2-G1 True 

formal-identity_address-b2-G0 True 

formal-identity_callerAddress-b2-G3 True 

formal-identity_callerAddress-b2-G2 True 

formal-identity_callerAddress-b2-G1 True 

formal-identity_callerAddress-b2-G0 True 

formal-identity_callerAddress-b2-G4 True 

formal-erc721_balanceOf-b2-G2 True 

formal-erc721_balanceOf-b2-G1 True 

formal-erc721_balanceOf-b2-G0 True 

formal-erc721_balanceOf-b2-G4 True 

formal-erc721_balanceOf-b2-G3 True 

formal-erc721_tokenLatestTxInfo-b2-G1 True 

formal-erc721_tokenLatestTxInfo-b2-G0 True 

formal-erc721_tokenLatestTxInfo-b2-G4 True 

formal-erc721_tokenLatestTxInfo-b2-G3 True 

formal-erc721_tokenLatestTxInfo-b2-G2 True 

formal-raffle_raffle-b2-G0 True 

formal-raffle_raffle-b2-G4 True 

formal-raffle_raffle-b2-G3 True 

formal-raffle_raffle-b2-G2 True 

formal-raffle_raffle-b2-G1 True 

formal-identity_address-b3-G2 True 

formal-identity_address-b3-G4 True 

formal-identity_address-b3-G1 True 

formal-identity_address-b3-G3 True 

formal-identity_address-b3-G0 True 

formal-identity_callerAddress-b3-G4 True 

formal-identity_callerAddress-b3-G1 True 

formal-identity_callerAddress-b3-G3 True 

formal-identity_callerAddress-b3-G0 True 

formal-identity_callerAddress-b3-G2 True 

formal-erc721_balanceOf-b3-G1 True 

formal-erc721_balanceOf-b3-G3 True 

formal-erc721_balanceOf-b3-G0 True 

formal-erc721_balanceOf-b3-G2 True 

formal-erc721_balanceOf-b3-G4 True 

formal-erc721_tokenLatestTxInfo-b3-G3 True 

formal-erc721_tokenLatestTxInfo-b3-G0 True 

formal-erc721_tokenLatestTxInfo-b3-G2 True 

formal-erc721_tokenLatestTxInfo-b3-G4 True 

formal-erc721_tokenLatestTxInfo-b3-G1 True 

formal-raffle_raffle-b3-G0 True 

formal-raffle_raffle-b3-G2 True 

formal-raffle_raffle-b3-G4 True 

formal-raffle_raffle-b3-G1 True 

formal-raffle_raffle-b3-G3 True 

ordercheck-raffle-G3 True 

ordercheck-raffle-G4 True 


## Complete

6newseeddeployments,25prechecksand345mainformaltransactionscompleted; all20fivegroupmethod/batchparities exact. Fivegroups supportedbyunchanged39Ebinary, no sourcebuild. Raffle3participants/3drawsperbatch unchanged; othermethods5targetsperbatch. Mainindependentpairedunits3batchwindows; VM/SDKlinkedwithinrun+TxIDonly.

OrderauditshowedraffleG4beforeG3inall3mainbatches. OneadditionalG3thenG4diagnosticwithoriginalfixture,6targettransactions, separatelykeptandexcludedmainCI. VM+3.245ms, E2E-0.793ms; cannotclaimstableSHAE2Erescue. No new experiments planned.

All376targettransactions(345formal+25pre+6supplement)successfullycommitted; nofailures/timeoutsremoved. ExistingSDKfinalgasincludespost-VMRW/Eventfee; allrawRWsetsrecomputed:balance+6/latest+22/raffle+18,+13,+8, all5variantsconsistent. Initialanalysisincorrectgas-equalityassumptioncorrectedbyexactsourceboundaries, noGaslogicchange.

108actualnodesexit0,Store814/814,Instance706/706,nativepending0; RSSpeak652.172MiB,threads45. Limits1536MiB/220/Owner32unchanged. G4ArtifacthitsgrowandStopclearsall; inputSHA+RuntimeClone retained. Failedinitialconfigurationpathattemptneverstartednodeandisretained(seed-identity-plain); correctseedsusev1paths.

Results:VM5/5SHAincrementspositiveinprimary3batches; finalG4versusFreshE2E3methodsCIpositive,2crosszero. StandaloneSHAE2Emostlyuncertain,balancepointnegative,andreverse-raffledoesnotrepeatpositiveE2E. No globalclaimallfivehistoricalnegativesrescued. SeeRESULTS.md alltables,CI,order,positivefractionsandPPT3statements.

Read-onlyrecompute: python3 scripts/analyze.py; python3 scripts/report.py. Allruntimeorchestrationargv in audit/*orchestration.json; nodeargv/env/native/binsha in raw_logs/*-command.json. Currentstatecomplete,noactivejobs, noStep40or37methodautoextension. Nextcommand: reviewRESULTS.mdandCORRECTNESS.md; waitforhumanreview. No remote push.
