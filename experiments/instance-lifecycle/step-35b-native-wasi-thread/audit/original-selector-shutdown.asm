
CVW/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/wasmer-go/packaged/lib/linux-amd64/libwasmer.so:     file format elf64-x86-64


Disassembly of section .text:

0000000000abf070 <virtual_mio::selector::Selector::shutdown>:
  abf070:	50                   	push   %rax
  abf071:	48 83 c7 50          	add    $0x50,%rdi
  abf075:	ff 15 35 26 eb 00    	call   *0xeb2635(%rip)        # 19716b0 <_GLOBAL_OFFSET_TABLE_+0x6630>
  abf07b:	48 89 04 24          	mov    %rax,(%rsp)
  abf07f:	48 85 c0             	test   %rax,%rax
  abf082:	74 08                	je     abf08c <virtual_mio::selector::Selector::shutdown+0x1c>
  abf084:	48 89 e7             	mov    %rsp,%rdi
  abf087:	e8 24 fa ff ff       	call   abeab0 <core::ptr::drop_in_place<std::io::error::Error>>
  abf08c:	58                   	pop    %rax
  abf08d:	c3                   	ret
  abf08e:	66 90                	xchg   %ax,%ax

0000000000abf090 <virtual_mio::selector::Selector::add>:
  abf090:	55                   	push   %rbp
  abf091:	41 57                	push   %r15
  abf093:	41 56                	push   %r14
  abf095:	41 55                	push   %r13
  abf097:	41 54                	push   %r12
  abf099:	53                   	push   %rbx
  abf09a:	48 83 ec 58          	sub    $0x58,%rsp
  abf09e:	45 89 ce             	mov    %r9d,%r14d
  abf0a1:	4c 89 44 24 28       	mov    %r8,0x28(%rsp)
  abf0a6:	48 89 4c 24 18       	mov    %rcx,0x18(%rsp)
  abf0ab:	49 89 d7             	mov    %rdx,%r15
  abf0ae:	49                   	rex.WB
  abf0af:	89                   	.byte 0x89
