package wasmer

import "syscall"

func syscallTID() int { return syscall.Gettid() }
