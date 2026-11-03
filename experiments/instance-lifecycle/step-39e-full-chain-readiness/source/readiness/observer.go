// Package readiness39e is an experiment-only observer for one configured chain per node.
package readiness39e

import (
 "context"
 "encoding/json"
 "fmt"
 "os"
 "sync"
 "time"
)
var enabled=os.Getenv("CM39E_READINESS")=="1"
var mu sync.Mutex
var changed=make(chan struct{})
var chainBegin=time.Now()
var state=State{Run:os.Getenv("CM39E_RUN"),Chain:os.Getenv("CM39E_CHAIN"),Stages:map[string]int64{}}
type State struct {
 Run string `json:"run"`;Chain string `json:"chain"`;Stages map[string]int64 `json:"stages_ns"`
 RegistryReturned bool `json:"registry_returned"`;ProviderReturned bool `json:"provider_returned"`;SyncStarted bool `json:"sync_started"`;ChainStarted bool `json:"chain_started"`
 CoreStarted bool `json:"core_started"`;ConsensusStarted bool `json:"consensus_started"`;ProposerReady bool `json:"proposer_ready"`
 ConsumerStarted bool `json:"consumer_started"`;ConsumerActive bool `json:"consumer_active"`;Notified uint64 `json:"notified"`;Taken uint64 `json:"taken"`;Completed uint64 `json:"completed"`;LastNotifiedHeight uint64 `json:"last_notified_height"`;LastCompletedHeight uint64 `json:"last_completed_height"`
 Closing bool `json:"closing"`;Ready bool `json:"ready"`;FenceCount uint64 `json:"fence_count"`;WallNS int64 `json:"wall_ns"`;SinceChainStartNS int64 `json:"since_chain_start_ns"`
}
var activeHeight uint64
func Enabled()bool{return enabled}
func signal(){close(changed);changed=make(chan struct{})}
func Mark(stage string){if !enabled{return};mu.Lock();if stage=="chain_start_enter"{chainBegin=time.Now()};state.Stages[stage]=time.Since(chainBegin).Nanoseconds();switch stage{case"registry_returned":state.RegistryReturned=true;case"provider_returned":state.ProviderReturned=true;case"sync_started":state.SyncStarted=true;case"chain_started":state.ChainStarted=true;case"core_start_return":state.CoreStarted=true;case"consensus_start_return":state.ConsensusStarted=true;case"stopping":state.Closing=true;case"rule_consumer_exit":state.ConsumerStarted=false};signal();x:=copyState();mu.Unlock();b,_:=json.Marshal(map[string]interface{}{"stage":stage,"state":x});fmt.Printf("STEP39E %s\n",b)}
func CoreReady(v bool){if !enabled{return};mu.Lock();state.ProposerReady=v;signal();mu.Unlock()}
func Notify(height uint64){if !enabled{return};mu.Lock();state.Notified++;state.LastNotifiedHeight=height;signal();mu.Unlock()}
// Waiting is called at each loop head, after ALL processing of the prior item.
func Waiting(){if !enabled{return};mu.Lock();state.ConsumerStarted=true;if state.ConsumerActive{state.Completed++;state.LastCompletedHeight=activeHeight};state.ConsumerActive=false;signal();mu.Unlock()}
func Taken(height uint64){if !enabled{return};mu.Lock();state.Taken++;state.ConsumerActive=true;activeHeight=height;signal();mu.Unlock()}
func copyState()State{x:=state;x.Stages=map[string]int64{};for k,v:=range state.Stages{x.Stages[k]=v};x.WallNS=time.Now().UnixNano();x.SinceChainStartNS=time.Since(chainBegin).Nanoseconds();x.Ready=x.RegistryReturned&&x.ProviderReturned&&x.SyncStarted&&x.ChainStarted&&x.CoreStarted&&x.ConsensusStarted&&x.ConsumerStarted&&!x.ConsumerActive&&x.Notified==x.Completed&&x.ProposerReady&&!x.Closing;return x}
func Snapshot()State{mu.Lock();defer mu.Unlock();return copyState()}
func Await(ctx context.Context)error{for{mu.Lock();s:=copyState();ch:=changed;mu.Unlock();if s.Closing{return fmt.Errorf("node stopping")};if s.Ready{return nil};select{case<-ctx.Done():return ctx.Err();case<-ch:}}}
func FenceAck(){mu.Lock();state.FenceCount++;signal();mu.Unlock()}
// AwaitHeight also proves the post-probe BlockInfo has actually completed rule processing.
func AwaitHeight(ctx context.Context,min uint64)error{for{mu.Lock();s:=copyState();ch:=changed;mu.Unlock();if s.Closing{return fmt.Errorf("node stopping")};if s.Ready&&s.LastCompletedHeight>=min{return nil};select{case<-ctx.Done():return ctx.Err();case<-ch:}}}
