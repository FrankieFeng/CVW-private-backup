#define _GNU_SOURCE
#include <wasmer.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <dlfcn.h>
static wasm_instance_t* make(wasm_store_t*s,wasm_module_t*m,wasm_memory_t*mem){wasm_extern_t* p=wasm_memory_as_extern(mem);wasm_extern_vec_t v={1,&p};wasm_trap_t*t=NULL;wasm_instance_t*i=wasm_instance_new(s,m,&v,&t);assert(t==NULL);return i;}
int main(int argc,char**argv){setbuf(stdout,NULL);assert(argc==2);Dl_info info;assert(dladdr((void*)wasm_store_new,&info));printf("loaded=%s version=%s\n",info.dli_fname,wasmer_version());
 FILE*f=fopen(argv[1],"rb");assert(f);fseek(f,0,SEEK_END);long n=ftell(f);rewind(f);char*b=malloc(n);assert(fread(b,1,n,f)==n);fclose(f);
 wasm_engine_t*e=wasm_engine_new();wasm_store_t*s0=wasm_store_new(e),*s1=wasm_store_new(e),*s2=wasm_store_new(e);assert(s0&&s1&&s2);wasm_byte_vec_t code;wasm_byte_vec_new(&code,n,b);free(b);wasm_module_t*m=wasm_module_new(s0,&code);assert(m);wasm_byte_vec_delete(&code);
 wasm_limits_t lim={1,1};wasm_memorytype_t*mt=wasm_memorytype_new(&lim);wasm_memory_t*m0=wasm_memory_new(s0,mt),*m1=wasm_memory_new(s1,mt),*m2=wasm_memory_new(s2,mt);assert(m0&&m1&&m2);wasm_memorytype_delete(mt);
 assert(make(s1,m,m0)==NULL);printf("foreign_store_import=rejected\n");wasm_instance_t*i1=make(s1,m,m1),*i2=make(s2,m,m2);assert(i1&&i2);wasm_memory_data(m1)[0]=123;assert(wasm_memory_data(m2)[0]==0);
 wasm_extern_vec_t v;wasm_instance_exports(i1,&v);wasm_func_t*fn=wasm_extern_as_func(v.data[0]);wasm_val_vec_t args={0,NULL},res;wasm_val_vec_new_uninitialized(&res,1);assert(wasm_func_call(fn,&args,&res)==NULL);assert(res.data[0].of.i32==123);wasm_val_vec_delete(&res);wasm_extern_vec_delete(&v);
 wasm_instance_delete(i2);wasm_instance_delete(i1);wasm_memory_delete(m2);wasm_memory_delete(m1);wasm_memory_delete(m0);wasm_store_delete(s2);wasm_store_delete(s1);wasm_module_delete(m);wasm_store_delete(s0);wasm_engine_delete(e);puts("PASS cached_module_distinct_native_stores memory_isolation stores=3/3 instances=2/2");return 0;}
