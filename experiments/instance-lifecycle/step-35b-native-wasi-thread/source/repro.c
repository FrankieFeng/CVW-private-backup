#define _GNU_SOURCE
#include <wasmer.h>
#include <dirent.h>
#include <dlfcn.h>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/resource.h>
static long long stamp(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return (long long)t.tv_sec*1000000000+t.tv_nsec;}
static void stage(int p){void(*f)(int)=dlsym(RTLD_DEFAULT,"step35b_phase");if(f)f(p);}
static void snap(const char*tag){DIR*d=opendir("/proc/self/task");struct dirent*de;printf("SNAP {\"tag\":\"%s\",\"mono_ns\":%lld,\"tasks\":[",tag,stamp());int n=0;while((de=readdir(d))){if(de->d_name[0]=='.')continue;char p[512],wc[128]={0},name[128]={0};snprintf(p,sizeof p,"/proc/self/task/%s/comm",de->d_name);FILE*f=fopen(p,"r");if(!f)continue;fgets(name,sizeof name,f);fclose(f);name[strcspn(name,"\n")]=0;snprintf(p,sizeof p,"/proc/self/task/%s/wchan",de->d_name);f=fopen(p,"r");if(f){fgets(wc,sizeof wc,f);fclose(f);}printf("%s{\"tid\":%s,\"name\":\"%s\",\"wchan\":\"%s\"}",n++?",":"",de->d_name,name,wc);}closedir(d);struct rusage ru;getrusage(RUSAGE_SELF,&ru);printf("],\"threads\":%d,\"maxrss_kib\":%ld}\n",n,ru.ru_maxrss);fflush(stdout);if(n>220||ru.ru_maxrss>1536*1024)_exit(81);}
int main(int argc,char**argv){int n=argc>1?atoi(argv[1]):1;if(n<1||n>8)return 2;Dl_info d={0};dladdr((void*)wasi_env_new,&d);printf("LIB %s VERSION %s\n",d.dli_fname,wasmer_version());wasm_engine_t*eng=wasm_engine_new();if(!eng)return 3;snap("start");for(int i=0;i<n;i++){stage(10+i*10);wasm_store_t*s=wasm_store_new(eng);if(!s)return 4;stage(11+i*10);wasi_config_t*c=wasi_config_new("step35b");if(!c)return 5;stage(12+i*10);wasi_env_t*e=wasi_env_new(s,c);if(!e)return 6;stage(13+i*10);wasi_env_delete(e);stage(14+i*10);wasm_store_delete(s);char tag[64];snprintf(tag,sizeof tag,"deleted_%d",i);snap(tag);}wasm_engine_delete(eng);stage(100);snap("engine_deleted");for(int i=0;i<3;i++){struct timespec delay={1,0};nanosleep(&delay,0);char tag[64];snprintf(tag,sizeof tag,"idle_%ds",i+1);snap(tag);}return 0;}
