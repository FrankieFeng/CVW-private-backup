#define _GNU_SOURCE
#include <wasmer.h>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/resource.h>
static void snap(const char *tag){DIR*d=opendir("/proc/self/task");struct dirent*de;int n=0,epoll=0;while((de=readdir(d))){if(de->d_name[0]=='.')continue;n++;char p[256],buf[128]={0};snprintf(p,sizeof(p),"/proc/self/task/%s/wchan",de->d_name);FILE*f=fopen(p,"r");if(f){fgets(buf,sizeof(buf),f);fclose(f);if(strstr(buf,"epoll"))epoll++;}}closedir(d);struct rusage r;getrusage(RUSAGE_SELF,&r);printf("{\"tag\":\"%s\",\"threads\":%d,\"epoll_threads\":%d,\"maxrss_kib\":%ld}\n",tag,n,epoll,r.ru_maxrss);fflush(stdout);if(n>220||r.ru_maxrss>1536*1024)_exit(81);}
int main(int argc,char**argv){int env=argc>1&&strcmp(argv[1],"wasi")==0;wasm_engine_t*eng=wasm_engine_new();if(!eng)return 2;snap("start");for(int i=0;i<4;i++){wasm_store_t*s=wasm_store_new(eng);if(!s)return 3;if(env){wasi_config_t*c=wasi_config_new("step35a");if(!c)return 4;wasi_env_t*e=wasi_env_new(s,c);if(!e)return 5;wasi_env_delete(e);}unsigned long strong=**(unsigned long**)s;printf("{\"store\":%d,\"last_strong_before_delete\":%lu}\n",i,strong);wasm_store_delete(s);char tag[32];snprintf(tag,sizeof(tag),"closed%d",i);snap(tag);}wasm_engine_delete(eng);snap("engine_closed");sleep(1);snap("idle_1s");sleep(2);snap("idle_3s");return 0;}
