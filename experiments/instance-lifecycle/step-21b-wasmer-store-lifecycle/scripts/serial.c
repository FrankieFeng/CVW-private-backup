#define _POSIX_C_SOURCE 200809L
#include <wasmer.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
static void event(const char *op,int id) {
 struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t);
 printf("EVENT mono_ns=%lld op=%s instance=%d pid=%d\n",(long long)t.tv_sec*1000000000+t.tv_nsec,op,id,getpid()); fflush(stdout);
}
static void check(int ok,const char *what) { if(!ok) {fprintf(stderr,"FAIL %s\n",what);exit(2);} }
int main(int argc,char **argv) {
 setbuf(stdout,NULL);
 check(argc==2 && (!strcmp(argv[1],"same") || !strcmp(argv[1],"different")),"mode");
 printf("native_version=%s mode=%s calls=3 wasi=no gas=NA\n",wasmer_version(),argv[1]);
 wasm_engine_t *engine=wasm_engine_new(); check(engine!=NULL,"engine");
 wasm_store_t *store=wasm_store_new(engine);check(store!=NULL,"store"); event("store_new",0);
 // (module (func (export "run") (result i32) i32.const 42))
 const unsigned char bytes[]={0,97,115,109,1,0,0,0,1,5,1,96,0,1,127,3,2,1,0,7,7,1,3,114,117,110,0,0,10,6,1,4,0,65,42,11};
 wasm_byte_vec_t code;wasm_byte_vec_new(&code,sizeof(bytes),(const char *)bytes);
 wasm_module_t *module=wasm_module_new(store,&code);check(module!=NULL,"module");wasm_byte_vec_delete(&code);
 wasm_extern_vec_t imports={0,NULL},exports[3];wasm_instance_t *inst[3]={NULL,NULL,NULL};
 int count=strcmp(argv[1],"same")==0?1:3;
 for(int i=0;i<count;i++) {
  wasm_trap_t *trap=NULL;event("create_begin",i);
  inst[i]=wasm_instance_new(store,module,&imports,&trap);check(inst[i]!=NULL && trap==NULL,"instantiate");
  wasm_instance_exports(inst[i],&exports[i]);check(exports[i].size==1,"exports");event("create_done",i);
 }
 for(int j=0;j<3;j++) {
  int i=count==1?0:j;wasm_func_t *func=wasm_extern_as_func(exports[i].data[0]);check(func!=NULL,"function");
  wasm_val_vec_t args={0,NULL},results;wasm_val_vec_new_uninitialized(&results,1);event("call_begin",i);
  wasm_trap_t *trap=wasm_func_call(func,&args,&results);
  check(trap==NULL && results.size==1 && results.data[0].kind==WASM_I32 && results.data[0].of.i32==42,"result 42");
  printf("RESULT call=%d instance=%d i32=42\n",j,i);event("call_done",i);wasm_val_vec_delete(&results);
 }
 for(int i=0;i<count;i++){event("close_begin",i);wasm_extern_vec_delete(&exports[i]);wasm_instance_delete(inst[i]);event("close_done",i);}
 wasm_module_delete(module);wasm_store_delete(store);event("store_delete",0);wasm_engine_delete(engine);
 puts("PASS serial native only");return 0;
}
