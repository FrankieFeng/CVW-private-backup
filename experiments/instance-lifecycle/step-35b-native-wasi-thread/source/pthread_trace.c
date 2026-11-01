#define _GNU_SOURCE
#include <pthread.h>
#include <dlfcn.h>
#include <execinfo.h>
#include <stdatomic.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
static int fd=-1;static pthread_mutex_t lock=PTHREAD_MUTEX_INITIALIZER;static _Atomic int phase=0;static _Atomic unsigned seq=0;
void step35b_phase(int p){atomic_store(&phase,p);}
static void emit(const char*s,size_t n){pthread_mutex_lock(&lock);if(fd>=0)write(fd,s,n);pthread_mutex_unlock(&lock);}
__attribute__((constructor))static void init(void){const char*p=getenv("STEP35B_TRACE");if(p)fd=open(p,O_WRONLY|O_CREAT|O_EXCL|O_APPEND,0600);}
struct ctx{void*(*fn)(void*);void*arg;unsigned id;int stage;};
static void finish(void*v){struct ctx*c=v;char b[512];int n=snprintf(b,sizeof b,"EXIT id=%u tid=%ld phase_created=%d\n",c->id,syscall(SYS_gettid),c->stage);emit(b,n);free(c);}
static void*entry(void*v){struct ctx*c=v;char b[512],name[64];pthread_getname_np(pthread_self(),name,sizeof name);int n=snprintf(b,sizeof b,"START id=%u tid=%ld phase_created=%d name=%s\n",c->id,syscall(SYS_gettid),c->stage,name);emit(b,n);void*r;pthread_cleanup_push(finish,c);r=c->fn(c->arg);pthread_cleanup_pop(1);return r;}
int pthread_create(pthread_t*t,const pthread_attr_t*a,void*(*fn)(void*),void*arg){int(*real)(pthread_t*,const pthread_attr_t*,void*(*)(void*),void*)=dlsym(RTLD_NEXT,"pthread_create");struct ctx*c=malloc(sizeof *c);if(!c)return 12;*c=(struct ctx){fn,arg,atomic_fetch_add(&seq,1)+1,atomic_load(&phase)};void*frames[32];int k=backtrace(frames,32);char b[8192];size_t n=snprintf(b,sizeof b,"CREATE id=%u parent_tid=%ld phase=%d start=%p\n",c->id,syscall(SYS_gettid),c->stage,fn);for(int i=1;i<k&&n<sizeof(b)-512;i++){Dl_info d={0};dladdr(frames[i],&d);n+=snprintf(b+n,sizeof(b)-n," FRAME id=%u module=%s offset=0x%lx symbol=%s\n",c->id,d.dli_fname?d.dli_fname:"?",(unsigned long)((uintptr_t)frames[i]-(uintptr_t)d.dli_fbase),d.dli_sname?d.dli_sname:"?");}emit(b,n);int r=real(t,a,entry,c);if(r)free(c);return r;}
