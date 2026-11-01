
CVW/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/wasmer-go/packaged/lib/linux-amd64/libwasmer.so:     file format elf64-x86-64


Disassembly of section .text:

0000000000abfb90 <virtual_mio::selector::Selector::run>:
  abfb90:	55                   	push   %rbp
  abfb91:	41 57                	push   %r15
  abfb93:	41 56                	push   %r14
  abfb95:	41 55                	push   %r13
  abfb97:	41 54                	push   %r12
  abfb99:	53                   	push   %rbx
  abfb9a:	48 81 ec 28 02 00 00 	sub    $0x228,%rsp
  abfba1:	48 89 bc 24 78 01 00 	mov    %rdi,0x178(%rsp)
  abfba8:	00 
  abfba9:	89 b4 24 6c 01 00 00 	mov    %esi,0x16c(%rsp)
  abfbb0:	48 8d bc 24 80 01 00 	lea    0x180(%rsp),%rdi
  abfbb7:	00 
  abfbb8:	be 80 00 00 00       	mov    $0x80,%esi
  abfbbd:	ff 15 5d eb ea 00    	call   *0xeaeb5d(%rip)        # 196e720 <_GLOBAL_OFFSET_TABLE_+0x36a0>
  abfbc3:	48 8d 05 56 7f e0 00 	lea    0xe07f56(%rip),%rax        # 18c7b20 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x240>
  abfbca:	48 89 04 24          	mov    %rax,(%rsp)
  abfbce:	48 8d bc 24 6c 01 00 	lea    0x16c(%rsp),%rdi
  abfbd5:	00 
  abfbd6:	48 8d b4 24 80 01 00 	lea    0x180(%rsp),%rsi
  abfbdd:	00 
  abfbde:	b9 00 ca 9a 3b       	mov    $0x3b9aca00,%ecx
  abfbe3:	ff 15 af 2e eb 00    	call   *0xeb2eaf(%rip)        # 1972a98 <_GLOBAL_OFFSET_TABLE_+0x7a18>
  abfbe9:	48 85 c0             	test   %rax,%rax
  abfbec:	0f 85 fd 1a 00 00    	jne    ac16ef <virtual_mio::selector::Selector::run+0x1b5f>
  abfbf2:	4c 8b bc 24 78 01 00 	mov    0x178(%rsp),%r15
  abfbf9:	00 
  abfbfa:	49 8d 47 18          	lea    0x18(%r15),%rax
  abfbfe:	48 89 84 24 70 01 00 	mov    %rax,0x170(%rsp)
  abfc05:	00 
  abfc06:	31 c0                	xor    %eax,%eax
  abfc08:	b9 01 00 00 00       	mov    $0x1,%ecx
  abfc0d:	f0 41 0f b1 4f 18    	lock cmpxchg %ecx,0x18(%r15)
  abfc13:	74 0e                	je     abfc23 <virtual_mio::selector::Selector::run+0x93>
  abfc15:	48 8b bc 24 70 01 00 	mov    0x170(%rsp),%rdi
  abfc1c:	00 
  abfc1d:	ff 15 8d 04 eb 00    	call   *0xeb048d(%rip)        # 19700b0 <_GLOBAL_OFFSET_TABLE_+0x5030>
  abfc23:	48 8d 05 4e c5 eb 00 	lea    0xebc54e(%rip),%rax        # 197c178 <std::panicking::panic_count::GLOBAL_PANIC_COUNT>
  abfc2a:	48 8b 00             	mov    (%rax),%rax
  abfc2d:	48 b9 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%rcx
  abfc34:	ff ff 7f 
  abfc37:	48 85 c8             	test   %rcx,%rax
  abfc3a:	74 24                	je     abfc60 <virtual_mio::selector::Selector::run+0xd0>
  abfc3c:	ff 15 56 31 eb 00    	call   *0xeb3156(%rip)        # 1972d98 <_GLOBAL_OFFSET_TABLE_+0x7d18>
  abfc42:	34 01                	xor    $0x1,%al
  abfc44:	89 44 24 14          	mov    %eax,0x14(%rsp)
  abfc48:	41 0f b6 47 1c       	movzbl 0x1c(%r15),%eax
  abfc4d:	84 c0                	test   %al,%al
  abfc4f:	74 24                	je     abfc75 <virtual_mio::selector::Selector::run+0xe5>
  abfc51:	e9 14 1b 00 00       	jmp    ac176a <virtual_mio::selector::Selector::run+0x1bda>
  abfc56:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  abfc5d:	00 00 00 
  abfc60:	c7 44 24 14 00 00 00 	movl   $0x0,0x14(%rsp)
  abfc67:	00 
  abfc68:	41 0f b6 47 1c       	movzbl 0x1c(%r15),%eax
  abfc6d:	84 c0                	test   %al,%al
  abfc6f:	0f 85 f5 1a 00 00    	jne    ac176a <virtual_mio::selector::Selector::run+0x1bda>
  abfc75:	48 8d 84 24 80 01 00 	lea    0x180(%rsp),%rax
  abfc7c:	00 
  abfc7d:	48 89 84 24 18 02 00 	mov    %rax,0x218(%rsp)
  abfc84:	00 
  abfc85:	48 c7 84 24 20 02 00 	movq   $0x0,0x220(%rsp)
  abfc8c:	00 00 00 00 00 
  abfc91:	49 8d 47 40          	lea    0x40(%r15),%rax
  abfc95:	48 89 84 24 98 01 00 	mov    %rax,0x198(%rsp)
  abfc9c:	00 
  abfc9d:	eb 13                	jmp    abfcb2 <virtual_mio::selector::Selector::run+0x122>
  abfc9f:	90                   	nop
  abfca0:	49 8b 7c 24 f0       	mov    -0x10(%r12),%rdi
  abfca5:	49 8b 44 24 f8       	mov    -0x8(%r12),%rax
  abfcaa:	be 03 00 00 00       	mov    $0x3,%esi
  abfcaf:	ff 50 20             	call   *0x20(%rax)
  abfcb2:	48 8d bc 24 18 02 00 	lea    0x218(%rsp),%rdi
  abfcb9:	00 
  abfcba:	ff 15 68 b9 ea 00    	call   *0xeab968(%rip)        # 196b628 <_GLOBAL_OFFSET_TABLE_+0x5a8>
  abfcc0:	49 89 c6             	mov    %rax,%r14
  abfcc3:	48 85 c0             	test   %rax,%rax
  abfcc6:	0f 84 d4 18 00 00    	je     ac15a0 <virtual_mio::selector::Selector::run+0x1a10>
  abfccc:	49 8b 5e 04          	mov    0x4(%r14),%rbx
  abfcd0:	48 89 5c 24 58       	mov    %rbx,0x58(%rsp)
  abfcd5:	48 8b 84 24 78 01 00 	mov    0x178(%rsp),%rax
  abfcdc:	00 
  abfcdd:	48 3b 58 10          	cmp    0x10(%rax),%rbx
  abfce1:	0f 84 12 19 00 00    	je     ac15f9 <virtual_mio::selector::Selector::run+0x1a69>
  abfce7:	49 83 7f 38 00       	cmpq   $0x0,0x38(%r15)
  abfcec:	0f 84 0e 03 00 00    	je     ac0000 <virtual_mio::selector::Selector::run+0x470>
  abfcf2:	48 8b bc 24 98 01 00 	mov    0x198(%rsp),%rdi
  abfcf9:	00 
  abfcfa:	48 8d 74 24 58       	lea    0x58(%rsp),%rsi
  abfcff:	e8 ec 24 00 00       	call   ac21f0 <core::hash::BuildHasher::hash_one>
  abfd04:	49 8b 4f 20          	mov    0x20(%r15),%rcx
  abfd08:	49 8b 57 28          	mov    0x28(%r15),%rdx
  abfd0c:	48 89 d6             	mov    %rdx,%rsi
  abfd0f:	48 21 c6             	and    %rax,%rsi
  abfd12:	48 c1 e8 39          	shr    $0x39,%rax
  abfd16:	66 0f 6e c0          	movd   %eax,%xmm0
  abfd1a:	66 0f 60 c0          	punpcklbw %xmm0,%xmm0
  abfd1e:	f2 0f 70 c0 00       	pshuflw $0x0,%xmm0,%xmm0
  abfd23:	66 0f 70 c0 00       	pshufd $0x0,%xmm0,%xmm0
  abfd28:	48 8d 41 e8          	lea    -0x18(%rcx),%rax
  abfd2c:	31 ff                	xor    %edi,%edi
  abfd2e:	f3 0f 6f 0c 31       	movdqu (%rcx,%rsi,1),%xmm1
  abfd33:	66 0f 6f d1          	movdqa %xmm1,%xmm2
  abfd37:	66 0f 74 d0          	pcmpeqb %xmm0,%xmm2
  abfd3b:	66 44 0f d7 c2       	pmovmskb %xmm2,%r8d
  abfd40:	45 85 c0             	test   %r8d,%r8d
  abfd43:	74 30                	je     abfd75 <virtual_mio::selector::Selector::run+0x1e5>
  abfd45:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
  abfd4c:	00 00 00 00 
  abfd50:	f3 45 0f bc c8       	tzcnt  %r8d,%r9d
  abfd55:	49 01 f1             	add    %rsi,%r9
  abfd58:	49 21 d1             	and    %rdx,%r9
  abfd5b:	49 f7 d9             	neg    %r9
  abfd5e:	4f 8d 0c 49          	lea    (%r9,%r9,2),%r9
  abfd62:	4a 3b 1c c8          	cmp    (%rax,%r9,8),%rbx
  abfd66:	74 38                	je     abfda0 <virtual_mio::selector::Selector::run+0x210>
  abfd68:	45 8d 48 ff          	lea    -0x1(%r8),%r9d
  abfd6c:	66 45 21 c1          	and    %r8w,%r9w
  abfd70:	45 89 c8             	mov    %r9d,%r8d
  abfd73:	75 db                	jne    abfd50 <virtual_mio::selector::Selector::run+0x1c0>
  abfd75:	66 0f 74 0d e3 93 8e 	pcmpeqb 0x8e93e3(%rip),%xmm1        # 13a9160 <anon.099b9761fdd342048277791c2db80edd.12.llvm.7925050829545238201>
  abfd7c:	00 
  abfd7d:	66 44 0f d7 c1       	pmovmskb %xmm1,%r8d
  abfd82:	45 85 c0             	test   %r8d,%r8d
  abfd85:	0f 85 75 02 00 00    	jne    ac0000 <virtual_mio::selector::Selector::run+0x470>
  abfd8b:	48 01 fe             	add    %rdi,%rsi
  abfd8e:	48 83 c6 10          	add    $0x10,%rsi
  abfd92:	48 83 c7 10          	add    $0x10,%rdi
  abfd96:	48 21 d6             	and    %rdx,%rsi
  abfd99:	eb 93                	jmp    abfd2e <virtual_mio::selector::Selector::run+0x19e>
  abfd9b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  abfda0:	4e 8d 24 c9          	lea    (%rcx,%r9,8),%r12
  abfda4:	45 8b 2e             	mov    (%r14),%r13d
  abfda7:	41 f6 c5 03          	test   $0x3,%r13b
  abfdab:	0f 84 ee 08 00 00    	je     ac069f <virtual_mio::selector::Selector::run+0xb0f>
  abfdb1:	48 8d 05 e0 97 eb 00 	lea    0xeb97e0(%rip),%rax        # 1979598 <tracing_core::metadata::MAX_LEVEL>
  abfdb8:	48 8b 00             	mov    (%rax),%rax
  abfdbb:	48 85 c0             	test   %rax,%rax
  abfdbe:	0f 84 70 02 00 00    	je     ac0034 <virtual_mio::selector::Selector::run+0x4a4>
  abfdc4:	48 8d 05 a5 c2 eb 00 	lea    0xebc2a5(%rip),%rax        # 197c070 <tracing_core::dispatcher::EXISTS>
  abfdcb:	0f b6 00             	movzbl (%rax),%eax
  abfdce:	84 c0                	test   %al,%al
  abfdd0:	0f 85 ba 08 00 00    	jne    ac0690 <virtual_mio::selector::Selector::run+0xb00>
  abfdd6:	48 8d 05 8b c2 eb 00 	lea    0xebc28b(%rip),%rax        # 197c068 <log::MAX_LOG_LEVEL_FILTER>
  abfddd:	48 8b 00             	mov    (%rax),%rax
  abfde0:	48 83 f8 05          	cmp    $0x5,%rax
  abfde4:	0f 85 a6 08 00 00    	jne    ac0690 <virtual_mio::selector::Selector::run+0xb00>
  abfdea:	4c 8b 35 b7 8d eb 00 	mov    0xeb8db7(%rip),%r14        # 1978ba8 <virtual_mio::selector::Selector::run::__CALLSITE>
  abfdf1:	f3 41 0f 6f 46 20    	movdqu 0x20(%r14),%xmm0
  abfdf7:	48 c7 84 24 b8 01 00 	movq   $0x5,0x1b8(%rsp)
  abfdfe:	00 05 00 00 00 
  abfe03:	f3 0f 7f 84 24 c0 01 	movdqu %xmm0,0x1c0(%rsp)
  abfe0a:	00 00 
  abfe0c:	ff 15 1e dd ea 00    	call   *0xeadd1e(%rip)        # 196db30 <_GLOBAL_OFFSET_TABLE_+0x2ab0>
  abfe12:	48 89 c3             	mov    %rax,%rbx
  abfe15:	48 89 d5             	mov    %rdx,%rbp
  abfe18:	48 89 c7             	mov    %rax,%rdi
  abfe1b:	48 8d b4 24 b8 01 00 	lea    0x1b8(%rsp),%rsi
  abfe22:	00 
  abfe23:	ff 52 18             	call   *0x18(%rdx)
  abfe26:	84 c0                	test   %al,%al
  abfe28:	0f 84 62 08 00 00    	je     ac0690 <virtual_mio::selector::Selector::run+0xb00>
  abfe2e:	48 8b 05 73 8d eb 00 	mov    0xeb8d73(%rip),%rax        # 1978ba8 <virtual_mio::selector::Selector::run::__CALLSITE>
  abfe35:	48 8b 48 38          	mov    0x38(%rax),%rcx
  abfe39:	48 85 c9             	test   %rcx,%rcx
  abfe3c:	0f 84 92 18 00 00    	je     ac16d4 <virtual_mio::selector::Selector::run+0x1b44>
  abfe42:	48 8b 78 30          	mov    0x30(%rax),%rdi
  abfe46:	48 8b 50 40          	mov    0x40(%rax),%rdx
  abfe4a:	48 8b 70 48          	mov    0x48(%rax),%rsi
  abfe4e:	48 89 bc 24 f0 00 00 	mov    %rdi,0xf0(%rsp)
  abfe55:	00 
  abfe56:	48 89 8c 24 f8 00 00 	mov    %rcx,0xf8(%rsp)
  abfe5d:	00 
  abfe5e:	48 89 94 24 00 01 00 	mov    %rdx,0x100(%rsp)
  abfe65:	00 
  abfe66:	48 89 b4 24 08 01 00 	mov    %rsi,0x108(%rsp)
  abfe6d:	00 
  abfe6e:	48 c7 84 24 10 01 00 	movq   $0x0,0x110(%rsp)
  abfe75:	00 00 00 00 00 
  abfe7a:	4c 8d 05 b7 7c e0 00 	lea    0xe07cb7(%rip),%r8        # 18c7b38 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x258>
  abfe81:	4c 89 84 24 18 01 00 	mov    %r8,0x118(%rsp)
  abfe88:	00 
  abfe89:	48 c7 84 24 20 01 00 	movq   $0x1,0x120(%rsp)
  abfe90:	00 01 00 00 00 
  abfe95:	48 c7 84 24 28 01 00 	movq   $0x8,0x128(%rsp)
  abfe9c:	00 08 00 00 00 
  abfea1:	66 0f ef c0          	pxor   %xmm0,%xmm0
  abfea5:	f3 0f 7f 84 24 30 01 	movdqu %xmm0,0x130(%rsp)
  abfeac:	00 00 
  abfeae:	48 83 f9 01          	cmp    $0x1,%rcx
  abfeb2:	0f 84 1c 18 00 00    	je     ac16d4 <virtual_mio::selector::Selector::run+0x1b44>
  abfeb8:	48 89 7c 24 60       	mov    %rdi,0x60(%rsp)
  abfebd:	48 89 4c 24 68       	mov    %rcx,0x68(%rsp)
  abfec2:	48 89 54 24 70       	mov    %rdx,0x70(%rsp)
  abfec7:	48 89 74 24 78       	mov    %rsi,0x78(%rsp)
  abfecc:	48 c7 84 24 80 00 00 	movq   $0x1,0x80(%rsp)
  abfed3:	00 01 00 00 00 
  abfed8:	4c 8d 44 24 58       	lea    0x58(%rsp),%r8
  abfedd:	4c 89 44 24 08       	mov    %r8,0x8(%rsp)
  abfee2:	48 83 f9 03          	cmp    $0x3,%rcx
  abfee6:	0f 82 e8 17 00 00    	jb     ac16d4 <virtual_mio::selector::Selector::run+0x1b44>
  abfeec:	48 89 7c 24 30       	mov    %rdi,0x30(%rsp)
  abfef1:	48 89 4c 24 38       	mov    %rcx,0x38(%rsp)
  abfef6:	48 89 54 24 40       	mov    %rdx,0x40(%rsp)
  abfefb:	48 89 74 24 48       	mov    %rsi,0x48(%rsp)
  abff00:	48 83 c0 30          	add    $0x30,%rax
  abff04:	48 8d 8c 24 88 00 00 	lea    0x88(%rsp),%rcx
  abff0b:	00 
  abff0c:	48 89 4c 24 18       	mov    %rcx,0x18(%rsp)
  abff11:	48 c7 44 24 20 03 00 	movq   $0x3,0x20(%rsp)
  abff18:	00 00 
  abff1a:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  abff1f:	48 8b 84 24 c8 01 00 	mov    0x1c8(%rsp),%rax
  abff26:	00 
  abff27:	48 89 84 24 e0 00 00 	mov    %rax,0xe0(%rsp)
  abff2e:	00 
  abff2f:	48 c7 44 24 50 02 00 	movq   $0x2,0x50(%rsp)
  abff36:	00 00 
  abff38:	48 8d 05 df 89 98 00 	lea    0x9889df(%rip),%rax        # 144891e <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3eb8>
  abff3f:	48 89 84 24 48 01 00 	mov    %rax,0x148(%rsp)
  abff46:	00 
  abff47:	48 8d 84 24 f0 00 00 	lea    0xf0(%rsp),%rax
  abff4e:	00 
  abff4f:	48 89 84 24 88 00 00 	mov    %rax,0x88(%rsp)
  abff56:	00 
  abff57:	48 8d 84 24 18 01 00 	lea    0x118(%rsp),%rax
  abff5e:	00 
  abff5f:	48 89 84 24 90 00 00 	mov    %rax,0x90(%rsp)
  abff66:	00 
  abff67:	48 8d 05 72 7b e0 00 	lea    0xe07b72(%rip),%rax        # 18c7ae0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x200>
  abff6e:	48 89 84 24 98 00 00 	mov    %rax,0x98(%rsp)
  abff75:	00 
  abff76:	48 8d 44 24 60       	lea    0x60(%rsp),%rax
  abff7b:	48 89 84 24 a0 00 00 	mov    %rax,0xa0(%rsp)
  abff82:	00 
  abff83:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  abff88:	48 89 84 24 a8 00 00 	mov    %rax,0xa8(%rsp)
  abff8f:	00 
  abff90:	48 8d 05 b1 7b e0 00 	lea    0xe07bb1(%rip),%rax        # 18c7b48 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x268>
  abff97:	48 89 84 24 b0 00 00 	mov    %rax,0xb0(%rsp)
  abff9e:	00 
  abff9f:	48 8d 44 24 30       	lea    0x30(%rsp),%rax
  abffa4:	48 89 84 24 b8 00 00 	mov    %rax,0xb8(%rsp)
  abffab:	00 
  abffac:	48 8d 84 24 48 01 00 	lea    0x148(%rsp),%rax
  abffb3:	00 
  abffb4:	48 89 84 24 c0 00 00 	mov    %rax,0xc0(%rsp)
  abffbb:	00 
  abffbc:	48 8d 05 a5 7b e0 00 	lea    0xe07ba5(%rip),%rax        # 18c7b68 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x288>
  abffc3:	48 89 84 24 c8 00 00 	mov    %rax,0xc8(%rsp)
  abffca:	00 
  abffcb:	f3 0f 6f 84 24 b8 01 	movdqu 0x1b8(%rsp),%xmm0
  abffd2:	00 00 
  abffd4:	66 0f 7f 84 24 d0 00 	movdqa %xmm0,0xd0(%rsp)
  abffdb:	00 00 
  abffdd:	4c 89 f7             	mov    %r14,%rdi
  abffe0:	48 89 de             	mov    %rbx,%rsi
  abffe3:	48 89 ea             	mov    %rbp,%rdx
  abffe6:	48 8d 8c 24 d0 00 00 	lea    0xd0(%rsp),%rcx
  abffed:	00 
  abffee:	4c 8d 44 24 18       	lea    0x18(%rsp),%r8
  abfff3:	ff 15 9f c1 ea 00    	call   *0xeac19f(%rip)        # 196c198 <_GLOBAL_OFFSET_TABLE_+0x1118>
  abfff9:	e9 92 06 00 00       	jmp    ac0690 <virtual_mio::selector::Selector::run+0xb00>
  abfffe:	66 90                	xchg   %ax,%ax
  ac0000:	48 8d 05 91 95 eb 00 	lea    0xeb9591(%rip),%rax        # 1979598 <tracing_core::metadata::MAX_LEVEL>
  ac0007:	48 8b 00             	mov    (%rax),%rax
  ac000a:	48 83 f8 01          	cmp    $0x1,%rax
  ac000e:	0f 87 4c 02 00 00    	ja     ac0260 <virtual_mio::selector::Selector::run+0x6d0>
  ac0014:	0f b6 05 85 8b eb 00 	movzbl 0xeb8b85(%rip),%eax        # 1978ba0 <virtual_mio::selector::Selector::run::__CALLSITE+0x10>
  ac001b:	84 c0                	test   %al,%al
  ac001d:	0f 84 3d 02 00 00    	je     ac0260 <virtual_mio::selector::Selector::run+0x6d0>
  ac0023:	0f b6 c8             	movzbl %al,%ecx
  ac0026:	83 f9 01             	cmp    $0x1,%ecx
  ac0029:	74 49                	je     ac0074 <virtual_mio::selector::Selector::run+0x4e4>
  ac002b:	83 f9 02             	cmp    $0x2,%ecx
  ac002e:	75 2f                	jne    ac005f <virtual_mio::selector::Selector::run+0x4cf>
  ac0030:	b0 02                	mov    $0x2,%al
  ac0032:	eb 40                	jmp    ac0074 <virtual_mio::selector::Selector::run+0x4e4>
  ac0034:	0f b6 05 7d 8b eb 00 	movzbl 0xeb8b7d(%rip),%eax        # 1978bb8 <virtual_mio::selector::Selector::run::__CALLSITE+0x10>
  ac003b:	84 c0                	test   %al,%al
  ac003d:	0f 84 81 fd ff ff    	je     abfdc4 <virtual_mio::selector::Selector::run+0x234>
  ac0043:	0f b6 c8             	movzbl %al,%ecx
  ac0046:	83 f9 01             	cmp    $0x1,%ecx
  ac0049:	0f 84 ed 03 00 00    	je     ac043c <virtual_mio::selector::Selector::run+0x8ac>
  ac004f:	83 f9 02             	cmp    $0x2,%ecx
  ac0052:	0f 85 cf 03 00 00    	jne    ac0427 <virtual_mio::selector::Selector::run+0x897>
  ac0058:	b0 02                	mov    $0x2,%al
  ac005a:	e9 dd 03 00 00       	jmp    ac043c <virtual_mio::selector::Selector::run+0x8ac>
  ac005f:	48 8d 3d 2a 8b eb 00 	lea    0xeb8b2a(%rip),%rdi        # 1978b90 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac0066:	ff 15 64 f3 ea 00    	call   *0xeaf364(%rip)        # 196f3d0 <_GLOBAL_OFFSET_TABLE_+0x4350>
  ac006c:	84 c0                	test   %al,%al
  ac006e:	0f 84 ec 01 00 00    	je     ac0260 <virtual_mio::selector::Selector::run+0x6d0>
  ac0074:	48 8b 3d 15 8b eb 00 	mov    0xeb8b15(%rip),%rdi        # 1978b90 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac007b:	0f b6 f0             	movzbl %al,%esi
  ac007e:	ff 15 d4 1e eb 00    	call   *0xeb1ed4(%rip)        # 1971f58 <_GLOBAL_OFFSET_TABLE_+0x6ed8>
  ac0084:	84 c0                	test   %al,%al
  ac0086:	0f 84 d4 01 00 00    	je     ac0260 <virtual_mio::selector::Selector::run+0x6d0>
  ac008c:	48 8b 3d fd 8a eb 00 	mov    0xeb8afd(%rip),%rdi        # 1978b90 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac0093:	48 8b 47 38          	mov    0x38(%rdi),%rax
  ac0097:	48 85 c0             	test   %rax,%rax
  ac009a:	0f 84 17 16 00 00    	je     ac16b7 <virtual_mio::selector::Selector::run+0x1b27>
  ac00a0:	48 8b 77 30          	mov    0x30(%rdi),%rsi
  ac00a4:	48 8b 4f 40          	mov    0x40(%rdi),%rcx
  ac00a8:	48 8b 57 48          	mov    0x48(%rdi),%rdx
  ac00ac:	48 89 74 24 60       	mov    %rsi,0x60(%rsp)
  ac00b1:	48 89 44 24 68       	mov    %rax,0x68(%rsp)
  ac00b6:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
  ac00bb:	48 89 54 24 78       	mov    %rdx,0x78(%rsp)
  ac00c0:	48 c7 84 24 80 00 00 	movq   $0x0,0x80(%rsp)
  ac00c7:	00 00 00 00 00 
  ac00cc:	4c 8d 05 fd 79 e0 00 	lea    0xe079fd(%rip),%r8        # 18c7ad0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x1f0>
  ac00d3:	4c 89 84 24 88 00 00 	mov    %r8,0x88(%rsp)
  ac00da:	00 
  ac00db:	48 c7 84 24 90 00 00 	movq   $0x1,0x90(%rsp)
  ac00e2:	00 01 00 00 00 
  ac00e7:	48 c7 84 24 98 00 00 	movq   $0x8,0x98(%rsp)
  ac00ee:	00 08 00 00 00 
  ac00f3:	66 0f ef c0          	pxor   %xmm0,%xmm0
  ac00f7:	f3 0f 7f 84 24 a0 00 	movdqu %xmm0,0xa0(%rsp)
  ac00fe:	00 00 
  ac0100:	48 83 f8 01          	cmp    $0x1,%rax
  ac0104:	0f 84 ad 15 00 00    	je     ac16b7 <virtual_mio::selector::Selector::run+0x1b27>
  ac010a:	4c 8d 47 30          	lea    0x30(%rdi),%r8
  ac010e:	48 89 74 24 30       	mov    %rsi,0x30(%rsp)
  ac0113:	48 89 44 24 38       	mov    %rax,0x38(%rsp)
  ac0118:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
  ac011d:	48 89 54 24 48       	mov    %rdx,0x48(%rsp)
  ac0122:	48 c7 44 24 50 01 00 	movq   $0x1,0x50(%rsp)
  ac0129:	00 00 
  ac012b:	48 8d 44 24 60       	lea    0x60(%rsp),%rax
  ac0130:	48 89 84 24 18 01 00 	mov    %rax,0x118(%rsp)
  ac0137:	00 
  ac0138:	48 8d 84 24 88 00 00 	lea    0x88(%rsp),%rax
  ac013f:	00 
  ac0140:	48 89 84 24 20 01 00 	mov    %rax,0x120(%rsp)
  ac0147:	00 
  ac0148:	48 8d 05 91 79 e0 00 	lea    0xe07991(%rip),%rax        # 18c7ae0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x200>
  ac014f:	48 89 84 24 28 01 00 	mov    %rax,0x128(%rsp)
  ac0156:	00 
  ac0157:	48 8d 44 24 30       	lea    0x30(%rsp),%rax
  ac015c:	48 89 84 24 30 01 00 	mov    %rax,0x130(%rsp)
  ac0163:	00 
  ac0164:	48 8d 44 24 58       	lea    0x58(%rsp),%rax
  ac0169:	48 89 84 24 38 01 00 	mov    %rax,0x138(%rsp)
  ac0170:	00 
  ac0171:	48 8d 05 88 79 e0 00 	lea    0xe07988(%rip),%rax        # 18c7b00 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x220>
  ac0178:	48 89 84 24 40 01 00 	mov    %rax,0x140(%rsp)
  ac017f:	00 
  ac0180:	48 8d 84 24 18 01 00 	lea    0x118(%rsp),%rax
  ac0187:	00 
  ac0188:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
  ac018d:	48 c7 44 24 20 02 00 	movq   $0x2,0x20(%rsp)
  ac0194:	00 00 
  ac0196:	4c 89 44 24 28       	mov    %r8,0x28(%rsp)
  ac019b:	48 8d 74 24 18       	lea    0x18(%rsp),%rsi
  ac01a0:	ff 15 aa db ea 00    	call   *0xeadbaa(%rip)        # 196dd50 <_GLOBAL_OFFSET_TABLE_+0x2cd0>
  ac01a6:	48 8d 05 c3 be eb 00 	lea    0xebbec3(%rip),%rax        # 197c070 <tracing_core::dispatcher::EXISTS>
  ac01ad:	0f b6 00             	movzbl (%rax),%eax
  ac01b0:	84 c0                	test   %al,%al
  ac01b2:	0f 85 fa fa ff ff    	jne    abfcb2 <virtual_mio::selector::Selector::run+0x122>
  ac01b8:	48 8d 05 a9 be eb 00 	lea    0xebbea9(%rip),%rax        # 197c068 <log::MAX_LOG_LEVEL_FILTER>
  ac01bf:	48 8b 00             	mov    (%rax),%rax
  ac01c2:	48 83 f8 04          	cmp    $0x4,%rax
  ac01c6:	0f 82 e6 fa ff ff    	jb     abfcb2 <virtual_mio::selector::Selector::run+0x122>
  ac01cc:	48 8b 1d bd 89 eb 00 	mov    0xeb89bd(%rip),%rbx        # 1978b90 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac01d3:	f3 0f 6f 43 20       	movdqu 0x20(%rbx),%xmm0
  ac01d8:	48 c7 84 24 d0 00 00 	movq   $0x4,0xd0(%rsp)
  ac01df:	00 04 00 00 00 
  ac01e4:	f3 0f 7f 84 24 d8 00 	movdqu %xmm0,0xd8(%rsp)
  ac01eb:	00 00 
  ac01ed:	ff 15 3d d9 ea 00    	call   *0xead93d(%rip)        # 196db30 <_GLOBAL_OFFSET_TABLE_+0x2ab0>
  ac01f3:	49 89 c6             	mov    %rax,%r14
  ac01f6:	48 89 d5             	mov    %rdx,%rbp
  ac01f9:	48 89 c7             	mov    %rax,%rdi
  ac01fc:	48 8d b4 24 d0 00 00 	lea    0xd0(%rsp),%rsi
  ac0203:	00 
  ac0204:	ff 52 18             	call   *0x18(%rdx)
  ac0207:	84 c0                	test   %al,%al
  ac0209:	0f 84 a3 fa ff ff    	je     abfcb2 <virtual_mio::selector::Selector::run+0x122>
  ac020f:	48 8b 84 24 e0 00 00 	mov    0xe0(%rsp),%rax
  ac0216:	00 
  ac0217:	48 89 84 24 00 01 00 	mov    %rax,0x100(%rsp)
  ac021e:	00 
  ac021f:	f3 0f 6f 84 24 d0 00 	movdqu 0xd0(%rsp),%xmm0
  ac0226:	00 00 
  ac0228:	66 0f 7f 84 24 f0 00 	movdqa %xmm0,0xf0(%rsp)
  ac022f:	00 00 
  ac0231:	48 89 df             	mov    %rbx,%rdi
  ac0234:	4c 89 f6             	mov    %r14,%rsi
  ac0237:	48 89 ea             	mov    %rbp,%rdx
  ac023a:	48 8d 8c 24 f0 00 00 	lea    0xf0(%rsp),%rcx
  ac0241:	00 
  ac0242:	4c 8d 44 24 18       	lea    0x18(%rsp),%r8
  ac0247:	ff 15 4b bf ea 00    	call   *0xeabf4b(%rip)        # 196c198 <_GLOBAL_OFFSET_TABLE_+0x1118>
  ac024d:	e9 60 fa ff ff       	jmp    abfcb2 <virtual_mio::selector::Selector::run+0x122>
  ac0252:	66 66 66 66 66 2e 0f 	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  ac0259:	1f 84 00 00 00 00 00 
  ac0260:	48 8d 05 09 be eb 00 	lea    0xebbe09(%rip),%rax        # 197c070 <tracing_core::dispatcher::EXISTS>
  ac0267:	0f b6 00             	movzbl (%rax),%eax
  ac026a:	84 c0                	test   %al,%al
  ac026c:	0f 85 40 fa ff ff    	jne    abfcb2 <virtual_mio::selector::Selector::run+0x122>
  ac0272:	48 8d 05 ef bd eb 00 	lea    0xebbdef(%rip),%rax        # 197c068 <log::MAX_LOG_LEVEL_FILTER>
  ac0279:	48 8b 00             	mov    (%rax),%rax
  ac027c:	48 83 f8 04          	cmp    $0x4,%rax
  ac0280:	0f 82 2c fa ff ff    	jb     abfcb2 <virtual_mio::selector::Selector::run+0x122>
  ac0286:	48 8b 1d 03 89 eb 00 	mov    0xeb8903(%rip),%rbx        # 1978b90 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac028d:	f3 0f 6f 43 20       	movdqu 0x20(%rbx),%xmm0
  ac0292:	48 c7 84 24 a0 01 00 	movq   $0x4,0x1a0(%rsp)
  ac0299:	00 04 00 00 00 
  ac029e:	f3 0f 7f 84 24 a8 01 	movdqu %xmm0,0x1a8(%rsp)
  ac02a5:	00 00 
  ac02a7:	ff 15 83 d8 ea 00    	call   *0xead883(%rip)        # 196db30 <_GLOBAL_OFFSET_TABLE_+0x2ab0>
  ac02ad:	49 89 c6             	mov    %rax,%r14
  ac02b0:	48 89 d5             	mov    %rdx,%rbp
  ac02b3:	48 89 c7             	mov    %rax,%rdi
  ac02b6:	48 8d b4 24 a0 01 00 	lea    0x1a0(%rsp),%rsi
  ac02bd:	00 
  ac02be:	ff 52 18             	call   *0x18(%rdx)
  ac02c1:	84 c0                	test   %al,%al
  ac02c3:	0f 84 e9 f9 ff ff    	je     abfcb2 <virtual_mio::selector::Selector::run+0x122>
  ac02c9:	48 8b 05 c0 88 eb 00 	mov    0xeb88c0(%rip),%rax        # 1978b90 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac02d0:	48 8b 48 38          	mov    0x38(%rax),%rcx
  ac02d4:	48 85 c9             	test   %rcx,%rcx
  ac02d7:	0f 84 da 13 00 00    	je     ac16b7 <virtual_mio::selector::Selector::run+0x1b27>
  ac02dd:	48 8b 78 30          	mov    0x30(%rax),%rdi
  ac02e1:	48 8b 50 40          	mov    0x40(%rax),%rdx
  ac02e5:	48 8b 70 48          	mov    0x48(%rax),%rsi
  ac02e9:	48 89 7c 24 60       	mov    %rdi,0x60(%rsp)
  ac02ee:	48 89 4c 24 68       	mov    %rcx,0x68(%rsp)
  ac02f3:	48 89 54 24 70       	mov    %rdx,0x70(%rsp)
  ac02f8:	48 89 74 24 78       	mov    %rsi,0x78(%rsp)
  ac02fd:	48 c7 84 24 80 00 00 	movq   $0x0,0x80(%rsp)
  ac0304:	00 00 00 00 00 
  ac0309:	4c 8d 05 c0 77 e0 00 	lea    0xe077c0(%rip),%r8        # 18c7ad0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x1f0>
  ac0310:	4c 89 84 24 88 00 00 	mov    %r8,0x88(%rsp)
  ac0317:	00 
  ac0318:	48 c7 84 24 90 00 00 	movq   $0x1,0x90(%rsp)
  ac031f:	00 01 00 00 00 
  ac0324:	48 c7 84 24 98 00 00 	movq   $0x8,0x98(%rsp)
  ac032b:	00 08 00 00 00 
  ac0330:	66 0f ef c0          	pxor   %xmm0,%xmm0
  ac0334:	f3 0f 7f 84 24 a0 00 	movdqu %xmm0,0xa0(%rsp)
  ac033b:	00 00 
  ac033d:	48 83 f9 01          	cmp    $0x1,%rcx
  ac0341:	0f 84 70 13 00 00    	je     ac16b7 <virtual_mio::selector::Selector::run+0x1b27>
  ac0347:	48 83 c0 30          	add    $0x30,%rax
  ac034b:	48 89 7c 24 30       	mov    %rdi,0x30(%rsp)
  ac0350:	48 89 4c 24 38       	mov    %rcx,0x38(%rsp)
  ac0355:	48 89 54 24 40       	mov    %rdx,0x40(%rsp)
  ac035a:	48 89 74 24 48       	mov    %rsi,0x48(%rsp)
  ac035f:	48 c7 44 24 50 01 00 	movq   $0x1,0x50(%rsp)
  ac0366:	00 00 
  ac0368:	48 8d 4c 24 60       	lea    0x60(%rsp),%rcx
  ac036d:	48 89 8c 24 18 01 00 	mov    %rcx,0x118(%rsp)
  ac0374:	00 
  ac0375:	48 8d 8c 24 88 00 00 	lea    0x88(%rsp),%rcx
  ac037c:	00 
  ac037d:	48 89 8c 24 20 01 00 	mov    %rcx,0x120(%rsp)
  ac0384:	00 
  ac0385:	48 8d 0d 54 77 e0 00 	lea    0xe07754(%rip),%rcx        # 18c7ae0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x200>
  ac038c:	48 89 8c 24 28 01 00 	mov    %rcx,0x128(%rsp)
  ac0393:	00 
  ac0394:	48 8d 4c 24 30       	lea    0x30(%rsp),%rcx
  ac0399:	48 89 8c 24 30 01 00 	mov    %rcx,0x130(%rsp)
  ac03a0:	00 
  ac03a1:	48 8d 4c 24 58       	lea    0x58(%rsp),%rcx
  ac03a6:	48 89 8c 24 38 01 00 	mov    %rcx,0x138(%rsp)
  ac03ad:	00 
  ac03ae:	48 8d 0d 4b 77 e0 00 	lea    0xe0774b(%rip),%rcx        # 18c7b00 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x220>
  ac03b5:	48 89 8c 24 40 01 00 	mov    %rcx,0x140(%rsp)
  ac03bc:	00 
  ac03bd:	48 8d 8c 24 18 01 00 	lea    0x118(%rsp),%rcx
  ac03c4:	00 
  ac03c5:	48 89 8c 24 d0 00 00 	mov    %rcx,0xd0(%rsp)
  ac03cc:	00 
  ac03cd:	48 c7 84 24 d8 00 00 	movq   $0x2,0xd8(%rsp)
  ac03d4:	00 02 00 00 00 
  ac03d9:	48 89 84 24 e0 00 00 	mov    %rax,0xe0(%rsp)
  ac03e0:	00 
  ac03e1:	48 8b 84 24 b0 01 00 	mov    0x1b0(%rsp),%rax
  ac03e8:	00 
  ac03e9:	48 89 84 24 00 01 00 	mov    %rax,0x100(%rsp)
  ac03f0:	00 
  ac03f1:	f3 0f 6f 84 24 a0 01 	movdqu 0x1a0(%rsp),%xmm0
  ac03f8:	00 00 
  ac03fa:	66 0f 7f 84 24 f0 00 	movdqa %xmm0,0xf0(%rsp)
  ac0401:	00 00 
  ac0403:	48 89 df             	mov    %rbx,%rdi
  ac0406:	4c 89 f6             	mov    %r14,%rsi
  ac0409:	48 89 ea             	mov    %rbp,%rdx
  ac040c:	48 8d 8c 24 f0 00 00 	lea    0xf0(%rsp),%rcx
  ac0413:	00 
  ac0414:	4c 8d 84 24 d0 00 00 	lea    0xd0(%rsp),%r8
  ac041b:	00 
  ac041c:	ff 15 76 bd ea 00    	call   *0xeabd76(%rip)        # 196c198 <_GLOBAL_OFFSET_TABLE_+0x1118>
  ac0422:	e9 8b f8 ff ff       	jmp    abfcb2 <virtual_mio::selector::Selector::run+0x122>
  ac0427:	48 8d 3d 7a 87 eb 00 	lea    0xeb877a(%rip),%rdi        # 1978ba8 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac042e:	ff 15 9c ef ea 00    	call   *0xeaef9c(%rip)        # 196f3d0 <_GLOBAL_OFFSET_TABLE_+0x4350>
  ac0434:	84 c0                	test   %al,%al
  ac0436:	0f 84 88 f9 ff ff    	je     abfdc4 <virtual_mio::selector::Selector::run+0x234>
  ac043c:	48 8b 3d 65 87 eb 00 	mov    0xeb8765(%rip),%rdi        # 1978ba8 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac0443:	0f b6 f0             	movzbl %al,%esi
  ac0446:	ff 15 0c 1b eb 00    	call   *0xeb1b0c(%rip)        # 1971f58 <_GLOBAL_OFFSET_TABLE_+0x6ed8>
  ac044c:	84 c0                	test   %al,%al
  ac044e:	0f 84 70 f9 ff ff    	je     abfdc4 <virtual_mio::selector::Selector::run+0x234>
  ac0454:	48 8b 3d 4d 87 eb 00 	mov    0xeb874d(%rip),%rdi        # 1978ba8 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac045b:	48 8b 47 38          	mov    0x38(%rdi),%rax
  ac045f:	48 85 c0             	test   %rax,%rax
  ac0462:	0f 84 6c 12 00 00    	je     ac16d4 <virtual_mio::selector::Selector::run+0x1b44>
  ac0468:	48 8b 77 30          	mov    0x30(%rdi),%rsi
  ac046c:	48 8b 4f 40          	mov    0x40(%rdi),%rcx
  ac0470:	48 8b 57 48          	mov    0x48(%rdi),%rdx
  ac0474:	48 89 b4 24 f0 00 00 	mov    %rsi,0xf0(%rsp)
  ac047b:	00 
  ac047c:	48 89 84 24 f8 00 00 	mov    %rax,0xf8(%rsp)
  ac0483:	00 
  ac0484:	48 89 8c 24 00 01 00 	mov    %rcx,0x100(%rsp)
  ac048b:	00 
  ac048c:	48 89 94 24 08 01 00 	mov    %rdx,0x108(%rsp)
  ac0493:	00 
  ac0494:	48 c7 84 24 10 01 00 	movq   $0x0,0x110(%rsp)
  ac049b:	00 00 00 00 00 
  ac04a0:	4c 8d 05 91 76 e0 00 	lea    0xe07691(%rip),%r8        # 18c7b38 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x258>
  ac04a7:	4c 89 84 24 18 01 00 	mov    %r8,0x118(%rsp)
  ac04ae:	00 
  ac04af:	48 c7 84 24 20 01 00 	movq   $0x1,0x120(%rsp)
  ac04b6:	00 01 00 00 00 
  ac04bb:	48 c7 84 24 28 01 00 	movq   $0x8,0x128(%rsp)
  ac04c2:	00 08 00 00 00 
  ac04c7:	66 0f ef c0          	pxor   %xmm0,%xmm0
  ac04cb:	f3 0f 7f 84 24 30 01 	movdqu %xmm0,0x130(%rsp)
  ac04d2:	00 00 
  ac04d4:	48 83 f8 01          	cmp    $0x1,%rax
  ac04d8:	0f 84 f6 11 00 00    	je     ac16d4 <virtual_mio::selector::Selector::run+0x1b44>
  ac04de:	48 89 74 24 60       	mov    %rsi,0x60(%rsp)
  ac04e3:	48 89 44 24 68       	mov    %rax,0x68(%rsp)
  ac04e8:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
  ac04ed:	48 89 54 24 78       	mov    %rdx,0x78(%rsp)
  ac04f2:	48 c7 84 24 80 00 00 	movq   $0x1,0x80(%rsp)
  ac04f9:	00 01 00 00 00 
  ac04fe:	4c 8d 44 24 58       	lea    0x58(%rsp),%r8
  ac0503:	4c 89 84 24 60 01 00 	mov    %r8,0x160(%rsp)
  ac050a:	00 
  ac050b:	48 83 f8 03          	cmp    $0x3,%rax
  ac050f:	0f 82 bf 11 00 00    	jb     ac16d4 <virtual_mio::selector::Selector::run+0x1b44>
  ac0515:	48 89 74 24 30       	mov    %rsi,0x30(%rsp)
  ac051a:	48 89 44 24 38       	mov    %rax,0x38(%rsp)
  ac051f:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
  ac0524:	48 89 54 24 48       	mov    %rdx,0x48(%rsp)
  ac0529:	48 8d 47 30          	lea    0x30(%rdi),%rax
  ac052d:	48 8d 8c 24 88 00 00 	lea    0x88(%rsp),%rcx
  ac0534:	00 
  ac0535:	48 89 8c 24 48 01 00 	mov    %rcx,0x148(%rsp)
  ac053c:	00 
  ac053d:	48 c7 84 24 50 01 00 	movq   $0x3,0x150(%rsp)
  ac0544:	00 03 00 00 00 
  ac0549:	48 89 84 24 58 01 00 	mov    %rax,0x158(%rsp)
  ac0550:	00 
  ac0551:	48 c7 44 24 50 02 00 	movq   $0x2,0x50(%rsp)
  ac0558:	00 00 
  ac055a:	48 8d 05 bd 83 98 00 	lea    0x9883bd(%rip),%rax        # 144891e <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3eb8>
  ac0561:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  ac0566:	48 8d 84 24 f0 00 00 	lea    0xf0(%rsp),%rax
  ac056d:	00 
  ac056e:	48 89 84 24 88 00 00 	mov    %rax,0x88(%rsp)
  ac0575:	00 
  ac0576:	48 8d 84 24 18 01 00 	lea    0x118(%rsp),%rax
  ac057d:	00 
  ac057e:	48 89 84 24 90 00 00 	mov    %rax,0x90(%rsp)
  ac0585:	00 
  ac0586:	48 8d 05 53 75 e0 00 	lea    0xe07553(%rip),%rax        # 18c7ae0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x200>
  ac058d:	48 89 84 24 98 00 00 	mov    %rax,0x98(%rsp)
  ac0594:	00 
  ac0595:	48 8d 44 24 60       	lea    0x60(%rsp),%rax
  ac059a:	48 89 84 24 a0 00 00 	mov    %rax,0xa0(%rsp)
  ac05a1:	00 
  ac05a2:	48 8d 84 24 60 01 00 	lea    0x160(%rsp),%rax
  ac05a9:	00 
  ac05aa:	48 89 84 24 a8 00 00 	mov    %rax,0xa8(%rsp)
  ac05b1:	00 
  ac05b2:	48 8d 05 8f 75 e0 00 	lea    0xe0758f(%rip),%rax        # 18c7b48 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x268>
  ac05b9:	48 89 84 24 b0 00 00 	mov    %rax,0xb0(%rsp)
  ac05c0:	00 
  ac05c1:	48 8d 44 24 30       	lea    0x30(%rsp),%rax
  ac05c6:	48 89 84 24 b8 00 00 	mov    %rax,0xb8(%rsp)
  ac05cd:	00 
  ac05ce:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  ac05d3:	48 89 84 24 c0 00 00 	mov    %rax,0xc0(%rsp)
  ac05da:	00 
  ac05db:	48 8d 05 86 75 e0 00 	lea    0xe07586(%rip),%rax        # 18c7b68 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x288>
  ac05e2:	48 89 84 24 c8 00 00 	mov    %rax,0xc8(%rsp)
  ac05e9:	00 
  ac05ea:	48 8d b4 24 48 01 00 	lea    0x148(%rsp),%rsi
  ac05f1:	00 
  ac05f2:	ff 15 58 d7 ea 00    	call   *0xead758(%rip)        # 196dd50 <_GLOBAL_OFFSET_TABLE_+0x2cd0>
  ac05f8:	48 8d 05 71 ba eb 00 	lea    0xebba71(%rip),%rax        # 197c070 <tracing_core::dispatcher::EXISTS>
  ac05ff:	0f b6 00             	movzbl (%rax),%eax
  ac0602:	84 c0                	test   %al,%al
  ac0604:	0f 85 86 00 00 00    	jne    ac0690 <virtual_mio::selector::Selector::run+0xb00>
  ac060a:	48 8d 05 57 ba eb 00 	lea    0xebba57(%rip),%rax        # 197c068 <log::MAX_LOG_LEVEL_FILTER>
  ac0611:	48 8b 00             	mov    (%rax),%rax
  ac0614:	48 83 f8 05          	cmp    $0x5,%rax
  ac0618:	75 76                	jne    ac0690 <virtual_mio::selector::Selector::run+0xb00>
  ac061a:	48 8b 1d 87 85 eb 00 	mov    0xeb8587(%rip),%rbx        # 1978ba8 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac0621:	f3 0f 6f 43 20       	movdqu 0x20(%rbx),%xmm0
  ac0626:	48 c7 44 24 18 05 00 	movq   $0x5,0x18(%rsp)
  ac062d:	00 00 
  ac062f:	f3 0f 7f 44 24 20    	movdqu %xmm0,0x20(%rsp)
  ac0635:	ff 15 f5 d4 ea 00    	call   *0xead4f5(%rip)        # 196db30 <_GLOBAL_OFFSET_TABLE_+0x2ab0>
  ac063b:	49 89 c6             	mov    %rax,%r14
  ac063e:	48 89 d5             	mov    %rdx,%rbp
  ac0641:	48 89 c7             	mov    %rax,%rdi
  ac0644:	48 8d 74 24 18       	lea    0x18(%rsp),%rsi
  ac0649:	ff 52 18             	call   *0x18(%rdx)
  ac064c:	84 c0                	test   %al,%al
  ac064e:	74 40                	je     ac0690 <virtual_mio::selector::Selector::run+0xb00>
  ac0650:	48 8b 44 24 28       	mov    0x28(%rsp),%rax
  ac0655:	48 89 84 24 e0 00 00 	mov    %rax,0xe0(%rsp)
  ac065c:	00 
  ac065d:	f3 0f 6f 44 24 18    	movdqu 0x18(%rsp),%xmm0
  ac0663:	66 0f 7f 84 24 d0 00 	movdqa %xmm0,0xd0(%rsp)
  ac066a:	00 00 
  ac066c:	48 89 df             	mov    %rbx,%rdi
  ac066f:	4c 89 f6             	mov    %r14,%rsi
  ac0672:	48 89 ea             	mov    %rbp,%rdx
  ac0675:	48 8d 8c 24 d0 00 00 	lea    0xd0(%rsp),%rcx
  ac067c:	00 
  ac067d:	4c 8d 84 24 48 01 00 	lea    0x148(%rsp),%r8
  ac0684:	00 
  ac0685:	ff 15 0d bb ea 00    	call   *0xeabb0d(%rip)        # 196c198 <_GLOBAL_OFFSET_TABLE_+0x1118>
  ac068b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  ac0690:	49 8b 7c 24 f0       	mov    -0x10(%r12),%rdi
  ac0695:	49 8b 44 24 f8       	mov    -0x8(%r12),%rax
  ac069a:	31 f6                	xor    %esi,%esi
  ac069c:	ff 50 20             	call   *0x20(%rax)
  ac069f:	41 f6 c5 04          	test   $0x4,%r13b
  ac06a3:	0f 84 e9 04 00 00    	je     ac0b92 <virtual_mio::selector::Selector::run+0x1002>
  ac06a9:	48 8d 05 e8 8e eb 00 	lea    0xeb8ee8(%rip),%rax        # 1979598 <tracing_core::metadata::MAX_LEVEL>
  ac06b0:	48 8b 00             	mov    (%rax),%rax
  ac06b3:	48 85 c0             	test   %rax,%rax
  ac06b6:	0f 84 3a 02 00 00    	je     ac08f6 <virtual_mio::selector::Selector::run+0xd66>
  ac06bc:	48 8d 05 ad b9 eb 00 	lea    0xebb9ad(%rip),%rax        # 197c070 <tracing_core::dispatcher::EXISTS>
  ac06c3:	0f b6 00             	movzbl (%rax),%eax
  ac06c6:	84 c0                	test   %al,%al
  ac06c8:	0f 85 b2 04 00 00    	jne    ac0b80 <virtual_mio::selector::Selector::run+0xff0>
  ac06ce:	48 8d 05 93 b9 eb 00 	lea    0xebb993(%rip),%rax        # 197c068 <log::MAX_LOG_LEVEL_FILTER>
  ac06d5:	48 8b 00             	mov    (%rax),%rax
  ac06d8:	48 83 f8 05          	cmp    $0x5,%rax
  ac06dc:	0f 85 9e 04 00 00    	jne    ac0b80 <virtual_mio::selector::Selector::run+0xff0>
  ac06e2:	4c 8b 35 d7 84 eb 00 	mov    0xeb84d7(%rip),%r14        # 1978bc0 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac06e9:	f3 41 0f 6f 46 20    	movdqu 0x20(%r14),%xmm0
  ac06ef:	48 c7 84 24 d0 01 00 	movq   $0x5,0x1d0(%rsp)
  ac06f6:	00 05 00 00 00 
  ac06fb:	f3 0f 7f 84 24 d8 01 	movdqu %xmm0,0x1d8(%rsp)
  ac0702:	00 00 
  ac0704:	ff 15 26 d4 ea 00    	call   *0xead426(%rip)        # 196db30 <_GLOBAL_OFFSET_TABLE_+0x2ab0>
  ac070a:	48 89 c3             	mov    %rax,%rbx
  ac070d:	48 89 d5             	mov    %rdx,%rbp
  ac0710:	48 89 c7             	mov    %rax,%rdi
  ac0713:	48 8d b4 24 d0 01 00 	lea    0x1d0(%rsp),%rsi
  ac071a:	00 
  ac071b:	ff 52 18             	call   *0x18(%rdx)
  ac071e:	84 c0                	test   %al,%al
  ac0720:	0f 84 5a 04 00 00    	je     ac0b80 <virtual_mio::selector::Selector::run+0xff0>
  ac0726:	48 8b 05 93 84 eb 00 	mov    0xeb8493(%rip),%rax        # 1978bc0 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac072d:	48 8b 48 38          	mov    0x38(%rax),%rcx
  ac0731:	48 85 c9             	test   %rcx,%rcx
  ac0734:	0f 84 86 0f 00 00    	je     ac16c0 <virtual_mio::selector::Selector::run+0x1b30>
  ac073a:	48 8b 78 30          	mov    0x30(%rax),%rdi
  ac073e:	48 8b 50 40          	mov    0x40(%rax),%rdx
  ac0742:	48 8b 70 48          	mov    0x48(%rax),%rsi
  ac0746:	48 89 bc 24 f0 00 00 	mov    %rdi,0xf0(%rsp)
  ac074d:	00 
  ac074e:	48 89 8c 24 f8 00 00 	mov    %rcx,0xf8(%rsp)
  ac0755:	00 
  ac0756:	48 89 94 24 00 01 00 	mov    %rdx,0x100(%rsp)
  ac075d:	00 
  ac075e:	48 89 b4 24 08 01 00 	mov    %rsi,0x108(%rsp)
  ac0765:	00 
  ac0766:	48 c7 84 24 10 01 00 	movq   $0x0,0x110(%rsp)
  ac076d:	00 00 00 00 00 
  ac0772:	4c 8d 05 bf 73 e0 00 	lea    0xe073bf(%rip),%r8        # 18c7b38 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x258>
  ac0779:	4c 89 84 24 18 01 00 	mov    %r8,0x118(%rsp)
  ac0780:	00 
  ac0781:	48 c7 84 24 20 01 00 	movq   $0x1,0x120(%rsp)
  ac0788:	00 01 00 00 00 
  ac078d:	48 c7 84 24 28 01 00 	movq   $0x8,0x128(%rsp)
  ac0794:	00 08 00 00 00 
  ac0799:	66 0f ef c0          	pxor   %xmm0,%xmm0
  ac079d:	f3 0f 7f 84 24 30 01 	movdqu %xmm0,0x130(%rsp)
  ac07a4:	00 00 
  ac07a6:	48 83 f9 01          	cmp    $0x1,%rcx
  ac07aa:	0f 84 10 0f 00 00    	je     ac16c0 <virtual_mio::selector::Selector::run+0x1b30>
  ac07b0:	48 89 7c 24 60       	mov    %rdi,0x60(%rsp)
  ac07b5:	48 89 4c 24 68       	mov    %rcx,0x68(%rsp)
  ac07ba:	48 89 54 24 70       	mov    %rdx,0x70(%rsp)
  ac07bf:	48 89 74 24 78       	mov    %rsi,0x78(%rsp)
  ac07c4:	48 c7 84 24 80 00 00 	movq   $0x1,0x80(%rsp)
  ac07cb:	00 01 00 00 00 
  ac07d0:	4c 8d 44 24 58       	lea    0x58(%rsp),%r8
  ac07d5:	4c 89 44 24 08       	mov    %r8,0x8(%rsp)
  ac07da:	48 83 f9 03          	cmp    $0x3,%rcx
  ac07de:	0f 82 dc 0e 00 00    	jb     ac16c0 <virtual_mio::selector::Selector::run+0x1b30>
  ac07e4:	48 89 7c 24 30       	mov    %rdi,0x30(%rsp)
  ac07e9:	48 89 4c 24 38       	mov    %rcx,0x38(%rsp)
  ac07ee:	48 89 54 24 40       	mov    %rdx,0x40(%rsp)
  ac07f3:	48 89 74 24 48       	mov    %rsi,0x48(%rsp)
  ac07f8:	48 83 c0 30          	add    $0x30,%rax
  ac07fc:	48 8d 8c 24 88 00 00 	lea    0x88(%rsp),%rcx
  ac0803:	00 
  ac0804:	48 89 4c 24 18       	mov    %rcx,0x18(%rsp)
  ac0809:	48 c7 44 24 20 03 00 	movq   $0x3,0x20(%rsp)
  ac0810:	00 00 
  ac0812:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  ac0817:	48 8b 84 24 e0 01 00 	mov    0x1e0(%rsp),%rax
  ac081e:	00 
  ac081f:	48 89 84 24 e0 00 00 	mov    %rax,0xe0(%rsp)
  ac0826:	00 
  ac0827:	48 c7 44 24 50 02 00 	movq   $0x2,0x50(%rsp)
  ac082e:	00 00 
  ac0830:	48 8d 05 e8 80 98 00 	lea    0x9880e8(%rip),%rax        # 144891f <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3eb9>
  ac0837:	48 89 84 24 48 01 00 	mov    %rax,0x148(%rsp)
  ac083e:	00 
  ac083f:	48 8d 84 24 f0 00 00 	lea    0xf0(%rsp),%rax
  ac0846:	00 
  ac0847:	48 89 84 24 88 00 00 	mov    %rax,0x88(%rsp)
  ac084e:	00 
  ac084f:	48 8d 84 24 18 01 00 	lea    0x118(%rsp),%rax
  ac0856:	00 
  ac0857:	48 89 84 24 90 00 00 	mov    %rax,0x90(%rsp)
  ac085e:	00 
  ac085f:	48 8d 05 7a 72 e0 00 	lea    0xe0727a(%rip),%rax        # 18c7ae0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x200>
  ac0866:	48 89 84 24 98 00 00 	mov    %rax,0x98(%rsp)
  ac086d:	00 
  ac086e:	48 8d 44 24 60       	lea    0x60(%rsp),%rax
  ac0873:	48 89 84 24 a0 00 00 	mov    %rax,0xa0(%rsp)
  ac087a:	00 
  ac087b:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  ac0880:	48 89 84 24 a8 00 00 	mov    %rax,0xa8(%rsp)
  ac0887:	00 
  ac0888:	48 8d 05 b9 72 e0 00 	lea    0xe072b9(%rip),%rax        # 18c7b48 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x268>
  ac088f:	48 89 84 24 b0 00 00 	mov    %rax,0xb0(%rsp)
  ac0896:	00 
  ac0897:	48 8d 44 24 30       	lea    0x30(%rsp),%rax
  ac089c:	48 89 84 24 b8 00 00 	mov    %rax,0xb8(%rsp)
  ac08a3:	00 
  ac08a4:	48 8d 84 24 48 01 00 	lea    0x148(%rsp),%rax
  ac08ab:	00 
  ac08ac:	48 89 84 24 c0 00 00 	mov    %rax,0xc0(%rsp)
  ac08b3:	00 
  ac08b4:	48 8d 05 ad 72 e0 00 	lea    0xe072ad(%rip),%rax        # 18c7b68 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x288>
  ac08bb:	48 89 84 24 c8 00 00 	mov    %rax,0xc8(%rsp)
  ac08c2:	00 
  ac08c3:	f3 0f 6f 84 24 d0 01 	movdqu 0x1d0(%rsp),%xmm0
  ac08ca:	00 00 
  ac08cc:	66 0f 7f 84 24 d0 00 	movdqa %xmm0,0xd0(%rsp)
  ac08d3:	00 00 
  ac08d5:	4c 89 f7             	mov    %r14,%rdi
  ac08d8:	48 89 de             	mov    %rbx,%rsi
  ac08db:	48 89 ea             	mov    %rbp,%rdx
  ac08de:	48 8d 8c 24 d0 00 00 	lea    0xd0(%rsp),%rcx
  ac08e5:	00 
  ac08e6:	4c 8d 44 24 18       	lea    0x18(%rsp),%r8
  ac08eb:	ff 15 a7 b8 ea 00    	call   *0xeab8a7(%rip)        # 196c198 <_GLOBAL_OFFSET_TABLE_+0x1118>
  ac08f1:	e9 8a 02 00 00       	jmp    ac0b80 <virtual_mio::selector::Selector::run+0xff0>
  ac08f6:	0f b6 05 d3 82 eb 00 	movzbl 0xeb82d3(%rip),%eax        # 1978bd0 <virtual_mio::selector::Selector::run::__CALLSITE+0x10>
  ac08fd:	84 c0                	test   %al,%al
  ac08ff:	0f 84 b7 fd ff ff    	je     ac06bc <virtual_mio::selector::Selector::run+0xb2c>
  ac0905:	0f b6 c8             	movzbl %al,%ecx
  ac0908:	83 f9 01             	cmp    $0x1,%ecx
  ac090b:	74 1e                	je     ac092b <virtual_mio::selector::Selector::run+0xd9b>
  ac090d:	83 f9 02             	cmp    $0x2,%ecx
  ac0910:	75 04                	jne    ac0916 <virtual_mio::selector::Selector::run+0xd86>
  ac0912:	b0 02                	mov    $0x2,%al
  ac0914:	eb 15                	jmp    ac092b <virtual_mio::selector::Selector::run+0xd9b>
  ac0916:	48 8d 3d a3 82 eb 00 	lea    0xeb82a3(%rip),%rdi        # 1978bc0 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac091d:	ff 15 ad ea ea 00    	call   *0xeaeaad(%rip)        # 196f3d0 <_GLOBAL_OFFSET_TABLE_+0x4350>
  ac0923:	84 c0                	test   %al,%al
  ac0925:	0f 84 91 fd ff ff    	je     ac06bc <virtual_mio::selector::Selector::run+0xb2c>
  ac092b:	48 8b 3d 8e 82 eb 00 	mov    0xeb828e(%rip),%rdi        # 1978bc0 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac0932:	0f b6 f0             	movzbl %al,%esi
  ac0935:	ff 15 1d 16 eb 00    	call   *0xeb161d(%rip)        # 1971f58 <_GLOBAL_OFFSET_TABLE_+0x6ed8>
  ac093b:	84 c0                	test   %al,%al
  ac093d:	0f 84 79 fd ff ff    	je     ac06bc <virtual_mio::selector::Selector::run+0xb2c>
  ac0943:	48 8b 3d 76 82 eb 00 	mov    0xeb8276(%rip),%rdi        # 1978bc0 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac094a:	48 8b 47 38          	mov    0x38(%rdi),%rax
  ac094e:	48 85 c0             	test   %rax,%rax
  ac0951:	0f 84 69 0d 00 00    	je     ac16c0 <virtual_mio::selector::Selector::run+0x1b30>
  ac0957:	48 8b 77 30          	mov    0x30(%rdi),%rsi
  ac095b:	48 8b 4f 40          	mov    0x40(%rdi),%rcx
  ac095f:	48 8b 57 48          	mov    0x48(%rdi),%rdx
  ac0963:	48 89 b4 24 f0 00 00 	mov    %rsi,0xf0(%rsp)
  ac096a:	00 
  ac096b:	48 89 84 24 f8 00 00 	mov    %rax,0xf8(%rsp)
  ac0972:	00 
  ac0973:	48 89 8c 24 00 01 00 	mov    %rcx,0x100(%rsp)
  ac097a:	00 
  ac097b:	48 89 94 24 08 01 00 	mov    %rdx,0x108(%rsp)
  ac0982:	00 
  ac0983:	48 c7 84 24 10 01 00 	movq   $0x0,0x110(%rsp)
  ac098a:	00 00 00 00 00 
  ac098f:	4c 8d 05 a2 71 e0 00 	lea    0xe071a2(%rip),%r8        # 18c7b38 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x258>
  ac0996:	4c 89 84 24 18 01 00 	mov    %r8,0x118(%rsp)
  ac099d:	00 
  ac099e:	48 c7 84 24 20 01 00 	movq   $0x1,0x120(%rsp)
  ac09a5:	00 01 00 00 00 
  ac09aa:	48 c7 84 24 28 01 00 	movq   $0x8,0x128(%rsp)
  ac09b1:	00 08 00 00 00 
  ac09b6:	66 0f ef c0          	pxor   %xmm0,%xmm0
  ac09ba:	f3 0f 7f 84 24 30 01 	movdqu %xmm0,0x130(%rsp)
  ac09c1:	00 00 
  ac09c3:	48 83 f8 01          	cmp    $0x1,%rax
  ac09c7:	0f 84 f3 0c 00 00    	je     ac16c0 <virtual_mio::selector::Selector::run+0x1b30>
  ac09cd:	48 89 74 24 60       	mov    %rsi,0x60(%rsp)
  ac09d2:	48 89 44 24 68       	mov    %rax,0x68(%rsp)
  ac09d7:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
  ac09dc:	48 89 54 24 78       	mov    %rdx,0x78(%rsp)
  ac09e1:	48 c7 84 24 80 00 00 	movq   $0x1,0x80(%rsp)
  ac09e8:	00 01 00 00 00 
  ac09ed:	4c 8d 44 24 58       	lea    0x58(%rsp),%r8
  ac09f2:	4c 89 84 24 60 01 00 	mov    %r8,0x160(%rsp)
  ac09f9:	00 
  ac09fa:	48 83 f8 03          	cmp    $0x3,%rax
  ac09fe:	0f 82 bc 0c 00 00    	jb     ac16c0 <virtual_mio::selector::Selector::run+0x1b30>
  ac0a04:	48 89 74 24 30       	mov    %rsi,0x30(%rsp)
  ac0a09:	48 89 44 24 38       	mov    %rax,0x38(%rsp)
  ac0a0e:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
  ac0a13:	48 89 54 24 48       	mov    %rdx,0x48(%rsp)
  ac0a18:	48 8d 47 30          	lea    0x30(%rdi),%rax
  ac0a1c:	48 8d 8c 24 88 00 00 	lea    0x88(%rsp),%rcx
  ac0a23:	00 
  ac0a24:	48 89 8c 24 48 01 00 	mov    %rcx,0x148(%rsp)
  ac0a2b:	00 
  ac0a2c:	48 c7 84 24 50 01 00 	movq   $0x3,0x150(%rsp)
  ac0a33:	00 03 00 00 00 
  ac0a38:	48 89 84 24 58 01 00 	mov    %rax,0x158(%rsp)
  ac0a3f:	00 
  ac0a40:	48 c7 44 24 50 02 00 	movq   $0x2,0x50(%rsp)
  ac0a47:	00 00 
  ac0a49:	48 8d 05 cf 7e 98 00 	lea    0x987ecf(%rip),%rax        # 144891f <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3eb9>
  ac0a50:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  ac0a55:	48 8d 84 24 f0 00 00 	lea    0xf0(%rsp),%rax
  ac0a5c:	00 
  ac0a5d:	48 89 84 24 88 00 00 	mov    %rax,0x88(%rsp)
  ac0a64:	00 
  ac0a65:	48 8d 84 24 18 01 00 	lea    0x118(%rsp),%rax
  ac0a6c:	00 
  ac0a6d:	48 89 84 24 90 00 00 	mov    %rax,0x90(%rsp)
  ac0a74:	00 
  ac0a75:	48 8d 05 64 70 e0 00 	lea    0xe07064(%rip),%rax        # 18c7ae0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x200>
  ac0a7c:	48 89 84 24 98 00 00 	mov    %rax,0x98(%rsp)
  ac0a83:	00 
  ac0a84:	48 8d 44 24 60       	lea    0x60(%rsp),%rax
  ac0a89:	48 89 84 24 a0 00 00 	mov    %rax,0xa0(%rsp)
  ac0a90:	00 
  ac0a91:	48 8d 84 24 60 01 00 	lea    0x160(%rsp),%rax
  ac0a98:	00 
  ac0a99:	48 89 84 24 a8 00 00 	mov    %rax,0xa8(%rsp)
  ac0aa0:	00 
  ac0aa1:	48 8d 05 a0 70 e0 00 	lea    0xe070a0(%rip),%rax        # 18c7b48 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x268>
  ac0aa8:	48 89 84 24 b0 00 00 	mov    %rax,0xb0(%rsp)
  ac0aaf:	00 
  ac0ab0:	48 8d 44 24 30       	lea    0x30(%rsp),%rax
  ac0ab5:	48 89 84 24 b8 00 00 	mov    %rax,0xb8(%rsp)
  ac0abc:	00 
  ac0abd:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  ac0ac2:	48 89 84 24 c0 00 00 	mov    %rax,0xc0(%rsp)
  ac0ac9:	00 
  ac0aca:	48 8d 05 97 70 e0 00 	lea    0xe07097(%rip),%rax        # 18c7b68 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x288>
  ac0ad1:	48 89 84 24 c8 00 00 	mov    %rax,0xc8(%rsp)
  ac0ad8:	00 
  ac0ad9:	48 8d b4 24 48 01 00 	lea    0x148(%rsp),%rsi
  ac0ae0:	00 
  ac0ae1:	ff 15 69 d2 ea 00    	call   *0xead269(%rip)        # 196dd50 <_GLOBAL_OFFSET_TABLE_+0x2cd0>
  ac0ae7:	48 8d 05 82 b5 eb 00 	lea    0xebb582(%rip),%rax        # 197c070 <tracing_core::dispatcher::EXISTS>
  ac0aee:	0f b6 00             	movzbl (%rax),%eax
  ac0af1:	84 c0                	test   %al,%al
  ac0af3:	0f 85 87 00 00 00    	jne    ac0b80 <virtual_mio::selector::Selector::run+0xff0>
  ac0af9:	48 8d 05 68 b5 eb 00 	lea    0xebb568(%rip),%rax        # 197c068 <log::MAX_LOG_LEVEL_FILTER>
  ac0b00:	48 8b 00             	mov    (%rax),%rax
  ac0b03:	48 83 f8 05          	cmp    $0x5,%rax
  ac0b07:	75 77                	jne    ac0b80 <virtual_mio::selector::Selector::run+0xff0>
  ac0b09:	48 8b 1d b0 80 eb 00 	mov    0xeb80b0(%rip),%rbx        # 1978bc0 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac0b10:	f3 0f 6f 43 20       	movdqu 0x20(%rbx),%xmm0
  ac0b15:	48 c7 44 24 18 05 00 	movq   $0x5,0x18(%rsp)
  ac0b1c:	00 00 
  ac0b1e:	f3 0f 7f 44 24 20    	movdqu %xmm0,0x20(%rsp)
  ac0b24:	ff 15 06 d0 ea 00    	call   *0xead006(%rip)        # 196db30 <_GLOBAL_OFFSET_TABLE_+0x2ab0>
  ac0b2a:	49 89 c6             	mov    %rax,%r14
  ac0b2d:	48 89 d5             	mov    %rdx,%rbp
  ac0b30:	48 89 c7             	mov    %rax,%rdi
  ac0b33:	48 8d 74 24 18       	lea    0x18(%rsp),%rsi
  ac0b38:	ff 52 18             	call   *0x18(%rdx)
  ac0b3b:	84 c0                	test   %al,%al
  ac0b3d:	74 41                	je     ac0b80 <virtual_mio::selector::Selector::run+0xff0>
  ac0b3f:	48 8b 44 24 28       	mov    0x28(%rsp),%rax
  ac0b44:	48 89 84 24 e0 00 00 	mov    %rax,0xe0(%rsp)
  ac0b4b:	00 
  ac0b4c:	f3 0f 6f 44 24 18    	movdqu 0x18(%rsp),%xmm0
  ac0b52:	66 0f 7f 84 24 d0 00 	movdqa %xmm0,0xd0(%rsp)
  ac0b59:	00 00 
  ac0b5b:	48 89 df             	mov    %rbx,%rdi
  ac0b5e:	4c 89 f6             	mov    %r14,%rsi
  ac0b61:	48 89 ea             	mov    %rbp,%rdx
  ac0b64:	48 8d 8c 24 d0 00 00 	lea    0xd0(%rsp),%rcx
  ac0b6b:	00 
  ac0b6c:	4c 8d 84 24 48 01 00 	lea    0x148(%rsp),%r8
  ac0b73:	00 
  ac0b74:	ff 15 1e b6 ea 00    	call   *0xeab61e(%rip)        # 196c198 <_GLOBAL_OFFSET_TABLE_+0x1118>
  ac0b7a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
  ac0b80:	49 8b 7c 24 f0       	mov    -0x10(%r12),%rdi
  ac0b85:	49 8b 44 24 f8       	mov    -0x8(%r12),%rax
  ac0b8a:	be 01 00 00 00       	mov    $0x1,%esi
  ac0b8f:	ff 50 20             	call   *0x20(%rax)
  ac0b92:	41 f6 c5 10          	test   $0x10,%r13b
  ac0b96:	75 28                	jne    ac0bc0 <virtual_mio::selector::Selector::run+0x1030>
  ac0b98:	44 89 e8             	mov    %r13d,%eax
  ac0b9b:	25 01 20 00 00       	and    $0x2001,%eax
  ac0ba0:	3d 01 20 00 00       	cmp    $0x2001,%eax
  ac0ba5:	74 19                	je     ac0bc0 <virtual_mio::selector::Selector::run+0x1030>
  ac0ba7:	41 83 fd 08          	cmp    $0x8,%r13d
  ac0bab:	74 13                	je     ac0bc0 <virtual_mio::selector::Selector::run+0x1030>
  ac0bad:	44 89 e8             	mov    %r13d,%eax
  ac0bb0:	83 e0 0c             	and    $0xc,%eax
  ac0bb3:	83 f8 0c             	cmp    $0xc,%eax
  ac0bb6:	0f 85 f6 04 00 00    	jne    ac10b2 <virtual_mio::selector::Selector::run+0x1522>
  ac0bbc:	0f 1f 40 00          	nopl   0x0(%rax)
  ac0bc0:	48 8d 05 d1 89 eb 00 	lea    0xeb89d1(%rip),%rax        # 1979598 <tracing_core::metadata::MAX_LEVEL>
  ac0bc7:	48 8b 00             	mov    (%rax),%rax
  ac0bca:	48 85 c0             	test   %rax,%rax
  ac0bcd:	0f 84 3a 02 00 00    	je     ac0e0d <virtual_mio::selector::Selector::run+0x127d>
  ac0bd3:	48 8d 05 96 b4 eb 00 	lea    0xebb496(%rip),%rax        # 197c070 <tracing_core::dispatcher::EXISTS>
  ac0bda:	0f b6 00             	movzbl (%rax),%eax
  ac0bdd:	84 c0                	test   %al,%al
  ac0bdf:	0f 85 bb 04 00 00    	jne    ac10a0 <virtual_mio::selector::Selector::run+0x1510>
  ac0be5:	48 8d 05 7c b4 eb 00 	lea    0xebb47c(%rip),%rax        # 197c068 <log::MAX_LOG_LEVEL_FILTER>
  ac0bec:	48 8b 00             	mov    (%rax),%rax
  ac0bef:	48 83 f8 05          	cmp    $0x5,%rax
  ac0bf3:	0f 85 a7 04 00 00    	jne    ac10a0 <virtual_mio::selector::Selector::run+0x1510>
  ac0bf9:	4c 8b 35 d8 7f eb 00 	mov    0xeb7fd8(%rip),%r14        # 1978bd8 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac0c00:	f3 41 0f 6f 46 20    	movdqu 0x20(%r14),%xmm0
  ac0c06:	48 c7 84 24 e8 01 00 	movq   $0x5,0x1e8(%rsp)
  ac0c0d:	00 05 00 00 00 
  ac0c12:	f3 0f 7f 84 24 f0 01 	movdqu %xmm0,0x1f0(%rsp)
  ac0c19:	00 00 
  ac0c1b:	ff 15 0f cf ea 00    	call   *0xeacf0f(%rip)        # 196db30 <_GLOBAL_OFFSET_TABLE_+0x2ab0>
  ac0c21:	48 89 c3             	mov    %rax,%rbx
  ac0c24:	48 89 d5             	mov    %rdx,%rbp
  ac0c27:	48 89 c7             	mov    %rax,%rdi
  ac0c2a:	48 8d b4 24 e8 01 00 	lea    0x1e8(%rsp),%rsi
  ac0c31:	00 
  ac0c32:	ff 52 18             	call   *0x18(%rdx)
  ac0c35:	84 c0                	test   %al,%al
  ac0c37:	0f 84 63 04 00 00    	je     ac10a0 <virtual_mio::selector::Selector::run+0x1510>
  ac0c3d:	48 8b 05 94 7f eb 00 	mov    0xeb7f94(%rip),%rax        # 1978bd8 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac0c44:	48 8b 48 38          	mov    0x38(%rax),%rcx
  ac0c48:	48 85 c9             	test   %rcx,%rcx
  ac0c4b:	0f 84 5d 0a 00 00    	je     ac16ae <virtual_mio::selector::Selector::run+0x1b1e>
  ac0c51:	48 8b 78 30          	mov    0x30(%rax),%rdi
  ac0c55:	48 8b 50 40          	mov    0x40(%rax),%rdx
  ac0c59:	48 8b 70 48          	mov    0x48(%rax),%rsi
  ac0c5d:	48 89 bc 24 f0 00 00 	mov    %rdi,0xf0(%rsp)
  ac0c64:	00 
  ac0c65:	48 89 8c 24 f8 00 00 	mov    %rcx,0xf8(%rsp)
  ac0c6c:	00 
  ac0c6d:	48 89 94 24 00 01 00 	mov    %rdx,0x100(%rsp)
  ac0c74:	00 
  ac0c75:	48 89 b4 24 08 01 00 	mov    %rsi,0x108(%rsp)
  ac0c7c:	00 
  ac0c7d:	48 c7 84 24 10 01 00 	movq   $0x0,0x110(%rsp)
  ac0c84:	00 00 00 00 00 
  ac0c89:	4c 8d 05 a8 6e e0 00 	lea    0xe06ea8(%rip),%r8        # 18c7b38 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x258>
  ac0c90:	4c 89 84 24 18 01 00 	mov    %r8,0x118(%rsp)
  ac0c97:	00 
  ac0c98:	48 c7 84 24 20 01 00 	movq   $0x1,0x120(%rsp)
  ac0c9f:	00 01 00 00 00 
  ac0ca4:	48 c7 84 24 28 01 00 	movq   $0x8,0x128(%rsp)
  ac0cab:	00 08 00 00 00 
  ac0cb0:	66 0f ef c0          	pxor   %xmm0,%xmm0
  ac0cb4:	f3 0f 7f 84 24 30 01 	movdqu %xmm0,0x130(%rsp)
  ac0cbb:	00 00 
  ac0cbd:	48 83 f9 01          	cmp    $0x1,%rcx
  ac0cc1:	0f 84 e7 09 00 00    	je     ac16ae <virtual_mio::selector::Selector::run+0x1b1e>
  ac0cc7:	48 89 7c 24 60       	mov    %rdi,0x60(%rsp)
  ac0ccc:	48 89 4c 24 68       	mov    %rcx,0x68(%rsp)
  ac0cd1:	48 89 54 24 70       	mov    %rdx,0x70(%rsp)
  ac0cd6:	48 89 74 24 78       	mov    %rsi,0x78(%rsp)
  ac0cdb:	48 c7 84 24 80 00 00 	movq   $0x1,0x80(%rsp)
  ac0ce2:	00 01 00 00 00 
  ac0ce7:	4c 8d 44 24 58       	lea    0x58(%rsp),%r8
  ac0cec:	4c 89 44 24 08       	mov    %r8,0x8(%rsp)
  ac0cf1:	48 83 f9 03          	cmp    $0x3,%rcx
  ac0cf5:	0f 82 b3 09 00 00    	jb     ac16ae <virtual_mio::selector::Selector::run+0x1b1e>
  ac0cfb:	48 89 7c 24 30       	mov    %rdi,0x30(%rsp)
  ac0d00:	48 89 4c 24 38       	mov    %rcx,0x38(%rsp)
  ac0d05:	48 89 54 24 40       	mov    %rdx,0x40(%rsp)
  ac0d0a:	48 89 74 24 48       	mov    %rsi,0x48(%rsp)
  ac0d0f:	48 83 c0 30          	add    $0x30,%rax
  ac0d13:	48 8d 8c 24 88 00 00 	lea    0x88(%rsp),%rcx
  ac0d1a:	00 
  ac0d1b:	48 89 4c 24 18       	mov    %rcx,0x18(%rsp)
  ac0d20:	48 c7 44 24 20 03 00 	movq   $0x3,0x20(%rsp)
  ac0d27:	00 00 
  ac0d29:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  ac0d2e:	48 8b 84 24 f8 01 00 	mov    0x1f8(%rsp),%rax
  ac0d35:	00 
  ac0d36:	48 89 84 24 e0 00 00 	mov    %rax,0xe0(%rsp)
  ac0d3d:	00 
  ac0d3e:	48 c7 44 24 50 02 00 	movq   $0x2,0x50(%rsp)
  ac0d45:	00 00 
  ac0d47:	48 8d 05 d2 7b 98 00 	lea    0x987bd2(%rip),%rax        # 1448920 <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3eba>
  ac0d4e:	48 89 84 24 48 01 00 	mov    %rax,0x148(%rsp)
  ac0d55:	00 
  ac0d56:	48 8d 84 24 f0 00 00 	lea    0xf0(%rsp),%rax
  ac0d5d:	00 
  ac0d5e:	48 89 84 24 88 00 00 	mov    %rax,0x88(%rsp)
  ac0d65:	00 
  ac0d66:	48 8d 84 24 18 01 00 	lea    0x118(%rsp),%rax
  ac0d6d:	00 
  ac0d6e:	48 89 84 24 90 00 00 	mov    %rax,0x90(%rsp)
  ac0d75:	00 
  ac0d76:	48 8d 05 63 6d e0 00 	lea    0xe06d63(%rip),%rax        # 18c7ae0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x200>
  ac0d7d:	48 89 84 24 98 00 00 	mov    %rax,0x98(%rsp)
  ac0d84:	00 
  ac0d85:	48 8d 44 24 60       	lea    0x60(%rsp),%rax
  ac0d8a:	48 89 84 24 a0 00 00 	mov    %rax,0xa0(%rsp)
  ac0d91:	00 
  ac0d92:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  ac0d97:	48 89 84 24 a8 00 00 	mov    %rax,0xa8(%rsp)
  ac0d9e:	00 
  ac0d9f:	48 8d 05 a2 6d e0 00 	lea    0xe06da2(%rip),%rax        # 18c7b48 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x268>
  ac0da6:	48 89 84 24 b0 00 00 	mov    %rax,0xb0(%rsp)
  ac0dad:	00 
  ac0dae:	48 8d 44 24 30       	lea    0x30(%rsp),%rax
  ac0db3:	48 89 84 24 b8 00 00 	mov    %rax,0xb8(%rsp)
  ac0dba:	00 
  ac0dbb:	48 8d 84 24 48 01 00 	lea    0x148(%rsp),%rax
  ac0dc2:	00 
  ac0dc3:	48 89 84 24 c0 00 00 	mov    %rax,0xc0(%rsp)
  ac0dca:	00 
  ac0dcb:	48 8d 05 96 6d e0 00 	lea    0xe06d96(%rip),%rax        # 18c7b68 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x288>
  ac0dd2:	48 89 84 24 c8 00 00 	mov    %rax,0xc8(%rsp)
  ac0dd9:	00 
  ac0dda:	f3 0f 6f 84 24 e8 01 	movdqu 0x1e8(%rsp),%xmm0
  ac0de1:	00 00 
  ac0de3:	66 0f 7f 84 24 d0 00 	movdqa %xmm0,0xd0(%rsp)
  ac0dea:	00 00 
  ac0dec:	4c 89 f7             	mov    %r14,%rdi
  ac0def:	48 89 de             	mov    %rbx,%rsi
  ac0df2:	48 89 ea             	mov    %rbp,%rdx
  ac0df5:	48 8d 8c 24 d0 00 00 	lea    0xd0(%rsp),%rcx
  ac0dfc:	00 
  ac0dfd:	4c 8d 44 24 18       	lea    0x18(%rsp),%r8
  ac0e02:	ff 15 90 b3 ea 00    	call   *0xeab390(%rip)        # 196c198 <_GLOBAL_OFFSET_TABLE_+0x1118>
  ac0e08:	e9 93 02 00 00       	jmp    ac10a0 <virtual_mio::selector::Selector::run+0x1510>
  ac0e0d:	0f b6 05 d4 7d eb 00 	movzbl 0xeb7dd4(%rip),%eax        # 1978be8 <virtual_mio::selector::Selector::run::__CALLSITE+0x10>
  ac0e14:	84 c0                	test   %al,%al
  ac0e16:	0f 84 b7 fd ff ff    	je     ac0bd3 <virtual_mio::selector::Selector::run+0x1043>
  ac0e1c:	0f b6 c8             	movzbl %al,%ecx
  ac0e1f:	83 f9 01             	cmp    $0x1,%ecx
  ac0e22:	74 1e                	je     ac0e42 <virtual_mio::selector::Selector::run+0x12b2>
  ac0e24:	83 f9 02             	cmp    $0x2,%ecx
  ac0e27:	75 04                	jne    ac0e2d <virtual_mio::selector::Selector::run+0x129d>
  ac0e29:	b0 02                	mov    $0x2,%al
  ac0e2b:	eb 15                	jmp    ac0e42 <virtual_mio::selector::Selector::run+0x12b2>
  ac0e2d:	48 8d 3d a4 7d eb 00 	lea    0xeb7da4(%rip),%rdi        # 1978bd8 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac0e34:	ff 15 96 e5 ea 00    	call   *0xeae596(%rip)        # 196f3d0 <_GLOBAL_OFFSET_TABLE_+0x4350>
  ac0e3a:	84 c0                	test   %al,%al
  ac0e3c:	0f 84 91 fd ff ff    	je     ac0bd3 <virtual_mio::selector::Selector::run+0x1043>
  ac0e42:	48 8b 3d 8f 7d eb 00 	mov    0xeb7d8f(%rip),%rdi        # 1978bd8 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac0e49:	0f b6 f0             	movzbl %al,%esi
  ac0e4c:	ff 15 06 11 eb 00    	call   *0xeb1106(%rip)        # 1971f58 <_GLOBAL_OFFSET_TABLE_+0x6ed8>
  ac0e52:	84 c0                	test   %al,%al
  ac0e54:	0f 84 79 fd ff ff    	je     ac0bd3 <virtual_mio::selector::Selector::run+0x1043>
  ac0e5a:	48 8b 3d 77 7d eb 00 	mov    0xeb7d77(%rip),%rdi        # 1978bd8 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac0e61:	48 8b 47 38          	mov    0x38(%rdi),%rax
  ac0e65:	48 85 c0             	test   %rax,%rax
  ac0e68:	0f 84 40 08 00 00    	je     ac16ae <virtual_mio::selector::Selector::run+0x1b1e>
  ac0e6e:	48 8b 77 30          	mov    0x30(%rdi),%rsi
  ac0e72:	48 8b 4f 40          	mov    0x40(%rdi),%rcx
  ac0e76:	48 8b 57 48          	mov    0x48(%rdi),%rdx
  ac0e7a:	48 89 b4 24 f0 00 00 	mov    %rsi,0xf0(%rsp)
  ac0e81:	00 
  ac0e82:	48 89 84 24 f8 00 00 	mov    %rax,0xf8(%rsp)
  ac0e89:	00 
  ac0e8a:	48 89 8c 24 00 01 00 	mov    %rcx,0x100(%rsp)
  ac0e91:	00 
  ac0e92:	48 89 94 24 08 01 00 	mov    %rdx,0x108(%rsp)
  ac0e99:	00 
  ac0e9a:	48 c7 84 24 10 01 00 	movq   $0x0,0x110(%rsp)
  ac0ea1:	00 00 00 00 00 
  ac0ea6:	4c 8d 05 8b 6c e0 00 	lea    0xe06c8b(%rip),%r8        # 18c7b38 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x258>
  ac0ead:	4c 89 84 24 18 01 00 	mov    %r8,0x118(%rsp)
  ac0eb4:	00 
  ac0eb5:	48 c7 84 24 20 01 00 	movq   $0x1,0x120(%rsp)
  ac0ebc:	00 01 00 00 00 
  ac0ec1:	48 c7 84 24 28 01 00 	movq   $0x8,0x128(%rsp)
  ac0ec8:	00 08 00 00 00 
  ac0ecd:	66 0f ef c0          	pxor   %xmm0,%xmm0
  ac0ed1:	f3 0f 7f 84 24 30 01 	movdqu %xmm0,0x130(%rsp)
  ac0ed8:	00 00 
  ac0eda:	48 83 f8 01          	cmp    $0x1,%rax
  ac0ede:	0f 84 ca 07 00 00    	je     ac16ae <virtual_mio::selector::Selector::run+0x1b1e>
  ac0ee4:	48 89 74 24 60       	mov    %rsi,0x60(%rsp)
  ac0ee9:	48 89 44 24 68       	mov    %rax,0x68(%rsp)
  ac0eee:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
  ac0ef3:	48 89 54 24 78       	mov    %rdx,0x78(%rsp)
  ac0ef8:	48 c7 84 24 80 00 00 	movq   $0x1,0x80(%rsp)
  ac0eff:	00 01 00 00 00 
  ac0f04:	4c 8d 44 24 58       	lea    0x58(%rsp),%r8
  ac0f09:	4c 89 84 24 60 01 00 	mov    %r8,0x160(%rsp)
  ac0f10:	00 
  ac0f11:	48 83 f8 03          	cmp    $0x3,%rax
  ac0f15:	0f 82 93 07 00 00    	jb     ac16ae <virtual_mio::selector::Selector::run+0x1b1e>
  ac0f1b:	48 89 74 24 30       	mov    %rsi,0x30(%rsp)
  ac0f20:	48 89 44 24 38       	mov    %rax,0x38(%rsp)
  ac0f25:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
  ac0f2a:	48 89 54 24 48       	mov    %rdx,0x48(%rsp)
  ac0f2f:	48 8d 47 30          	lea    0x30(%rdi),%rax
  ac0f33:	48 8d 8c 24 88 00 00 	lea    0x88(%rsp),%rcx
  ac0f3a:	00 
  ac0f3b:	48 89 8c 24 48 01 00 	mov    %rcx,0x148(%rsp)
  ac0f42:	00 
  ac0f43:	48 c7 84 24 50 01 00 	movq   $0x3,0x150(%rsp)
  ac0f4a:	00 03 00 00 00 
  ac0f4f:	48 89 84 24 58 01 00 	mov    %rax,0x158(%rsp)
  ac0f56:	00 
  ac0f57:	48 c7 44 24 50 02 00 	movq   $0x2,0x50(%rsp)
  ac0f5e:	00 00 
  ac0f60:	48 8d 05 b9 79 98 00 	lea    0x9879b9(%rip),%rax        # 1448920 <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3eba>
  ac0f67:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  ac0f6c:	48 8d 84 24 f0 00 00 	lea    0xf0(%rsp),%rax
  ac0f73:	00 
  ac0f74:	48 89 84 24 88 00 00 	mov    %rax,0x88(%rsp)
  ac0f7b:	00 
  ac0f7c:	48 8d 84 24 18 01 00 	lea    0x118(%rsp),%rax
  ac0f83:	00 
  ac0f84:	48 89 84 24 90 00 00 	mov    %rax,0x90(%rsp)
  ac0f8b:	00 
  ac0f8c:	48 8d 05 4d 6b e0 00 	lea    0xe06b4d(%rip),%rax        # 18c7ae0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x200>
  ac0f93:	48 89 84 24 98 00 00 	mov    %rax,0x98(%rsp)
  ac0f9a:	00 
  ac0f9b:	48 8d 44 24 60       	lea    0x60(%rsp),%rax
  ac0fa0:	48 89 84 24 a0 00 00 	mov    %rax,0xa0(%rsp)
  ac0fa7:	00 
  ac0fa8:	48 8d 84 24 60 01 00 	lea    0x160(%rsp),%rax
  ac0faf:	00 
  ac0fb0:	48 89 84 24 a8 00 00 	mov    %rax,0xa8(%rsp)
  ac0fb7:	00 
  ac0fb8:	48 8d 05 89 6b e0 00 	lea    0xe06b89(%rip),%rax        # 18c7b48 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x268>
  ac0fbf:	48 89 84 24 b0 00 00 	mov    %rax,0xb0(%rsp)
  ac0fc6:	00 
  ac0fc7:	48 8d 44 24 30       	lea    0x30(%rsp),%rax
  ac0fcc:	48 89 84 24 b8 00 00 	mov    %rax,0xb8(%rsp)
  ac0fd3:	00 
  ac0fd4:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  ac0fd9:	48 89 84 24 c0 00 00 	mov    %rax,0xc0(%rsp)
  ac0fe0:	00 
  ac0fe1:	48 8d 05 80 6b e0 00 	lea    0xe06b80(%rip),%rax        # 18c7b68 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x288>
  ac0fe8:	48 89 84 24 c8 00 00 	mov    %rax,0xc8(%rsp)
  ac0fef:	00 
  ac0ff0:	48 8d b4 24 48 01 00 	lea    0x148(%rsp),%rsi
  ac0ff7:	00 
  ac0ff8:	ff 15 52 cd ea 00    	call   *0xeacd52(%rip)        # 196dd50 <_GLOBAL_OFFSET_TABLE_+0x2cd0>
  ac0ffe:	48 8d 05 6b b0 eb 00 	lea    0xebb06b(%rip),%rax        # 197c070 <tracing_core::dispatcher::EXISTS>
  ac1005:	0f b6 00             	movzbl (%rax),%eax
  ac1008:	84 c0                	test   %al,%al
  ac100a:	0f 85 90 00 00 00    	jne    ac10a0 <virtual_mio::selector::Selector::run+0x1510>
  ac1010:	48 8d 05 51 b0 eb 00 	lea    0xebb051(%rip),%rax        # 197c068 <log::MAX_LOG_LEVEL_FILTER>
  ac1017:	48 8b 00             	mov    (%rax),%rax
  ac101a:	48 83 f8 05          	cmp    $0x5,%rax
  ac101e:	0f 85 7c 00 00 00    	jne    ac10a0 <virtual_mio::selector::Selector::run+0x1510>
  ac1024:	48 8b 1d ad 7b eb 00 	mov    0xeb7bad(%rip),%rbx        # 1978bd8 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac102b:	f3 0f 6f 43 20       	movdqu 0x20(%rbx),%xmm0
  ac1030:	48 c7 44 24 18 05 00 	movq   $0x5,0x18(%rsp)
  ac1037:	00 00 
  ac1039:	f3 0f 7f 44 24 20    	movdqu %xmm0,0x20(%rsp)
  ac103f:	ff 15 eb ca ea 00    	call   *0xeacaeb(%rip)        # 196db30 <_GLOBAL_OFFSET_TABLE_+0x2ab0>
  ac1045:	49 89 c6             	mov    %rax,%r14
  ac1048:	48 89 d5             	mov    %rdx,%rbp
  ac104b:	48 89 c7             	mov    %rax,%rdi
  ac104e:	48 8d 74 24 18       	lea    0x18(%rsp),%rsi
  ac1053:	ff 52 18             	call   *0x18(%rdx)
  ac1056:	84 c0                	test   %al,%al
  ac1058:	74 46                	je     ac10a0 <virtual_mio::selector::Selector::run+0x1510>
  ac105a:	48 8b 44 24 28       	mov    0x28(%rsp),%rax
  ac105f:	48 89 84 24 e0 00 00 	mov    %rax,0xe0(%rsp)
  ac1066:	00 
  ac1067:	f3 0f 6f 44 24 18    	movdqu 0x18(%rsp),%xmm0
  ac106d:	66 0f 7f 84 24 d0 00 	movdqa %xmm0,0xd0(%rsp)
  ac1074:	00 00 
  ac1076:	48 89 df             	mov    %rbx,%rdi
  ac1079:	4c 89 f6             	mov    %r14,%rsi
  ac107c:	48 89 ea             	mov    %rbp,%rdx
  ac107f:	48 8d 8c 24 d0 00 00 	lea    0xd0(%rsp),%rcx
  ac1086:	00 
  ac1087:	4c 8d 84 24 48 01 00 	lea    0x148(%rsp),%r8
  ac108e:	00 
  ac108f:	ff 15 03 b1 ea 00    	call   *0xeab103(%rip)        # 196c198 <_GLOBAL_OFFSET_TABLE_+0x1118>
  ac1095:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
  ac109c:	00 00 00 00 
  ac10a0:	49 8b 7c 24 f0       	mov    -0x10(%r12),%rdi
  ac10a5:	49 8b 44 24 f8       	mov    -0x8(%r12),%rax
  ac10aa:	be 02 00 00 00       	mov    $0x2,%esi
  ac10af:	ff 50 20             	call   *0x20(%rax)
  ac10b2:	41 f6 c5 08          	test   $0x8,%r13b
  ac10b6:	0f 84 f6 eb ff ff    	je     abfcb2 <virtual_mio::selector::Selector::run+0x122>
  ac10bc:	48 8d 05 d5 84 eb 00 	lea    0xeb84d5(%rip),%rax        # 1979598 <tracing_core::metadata::MAX_LEVEL>
  ac10c3:	48 8b 00             	mov    (%rax),%rax
  ac10c6:	48 85 c0             	test   %rax,%rax
  ac10c9:	0f 84 3a 02 00 00    	je     ac1309 <virtual_mio::selector::Selector::run+0x1779>
  ac10cf:	48 8d 05 9a af eb 00 	lea    0xebaf9a(%rip),%rax        # 197c070 <tracing_core::dispatcher::EXISTS>
  ac10d6:	0f b6 00             	movzbl (%rax),%eax
  ac10d9:	84 c0                	test   %al,%al
  ac10db:	0f 85 bf eb ff ff    	jne    abfca0 <virtual_mio::selector::Selector::run+0x110>
  ac10e1:	48 8d 05 80 af eb 00 	lea    0xebaf80(%rip),%rax        # 197c068 <log::MAX_LOG_LEVEL_FILTER>
  ac10e8:	48 8b 00             	mov    (%rax),%rax
  ac10eb:	48 83 f8 05          	cmp    $0x5,%rax
  ac10ef:	0f 85 ab eb ff ff    	jne    abfca0 <virtual_mio::selector::Selector::run+0x110>
  ac10f5:	4c 8b 35 f4 7a eb 00 	mov    0xeb7af4(%rip),%r14        # 1978bf0 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac10fc:	f3 41 0f 6f 46 20    	movdqu 0x20(%r14),%xmm0
  ac1102:	48 c7 84 24 00 02 00 	movq   $0x5,0x200(%rsp)
  ac1109:	00 05 00 00 00 
  ac110e:	f3 0f 7f 84 24 08 02 	movdqu %xmm0,0x208(%rsp)
  ac1115:	00 00 
  ac1117:	ff 15 13 ca ea 00    	call   *0xeaca13(%rip)        # 196db30 <_GLOBAL_OFFSET_TABLE_+0x2ab0>
  ac111d:	48 89 c3             	mov    %rax,%rbx
  ac1120:	48 89 d5             	mov    %rdx,%rbp
  ac1123:	48 89 c7             	mov    %rax,%rdi
  ac1126:	48 8d b4 24 00 02 00 	lea    0x200(%rsp),%rsi
  ac112d:	00 
  ac112e:	ff 52 18             	call   *0x18(%rdx)
  ac1131:	84 c0                	test   %al,%al
  ac1133:	0f 84 67 eb ff ff    	je     abfca0 <virtual_mio::selector::Selector::run+0x110>
  ac1139:	48 8b 05 b0 7a eb 00 	mov    0xeb7ab0(%rip),%rax        # 1978bf0 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac1140:	48 8b 48 38          	mov    0x38(%rax),%rcx
  ac1144:	48 85 c9             	test   %rcx,%rcx
  ac1147:	0f 84 7c 05 00 00    	je     ac16c9 <virtual_mio::selector::Selector::run+0x1b39>
  ac114d:	48 8b 78 30          	mov    0x30(%rax),%rdi
  ac1151:	48 8b 50 40          	mov    0x40(%rax),%rdx
  ac1155:	48 8b 70 48          	mov    0x48(%rax),%rsi
  ac1159:	48 89 bc 24 f0 00 00 	mov    %rdi,0xf0(%rsp)
  ac1160:	00 
  ac1161:	48 89 8c 24 f8 00 00 	mov    %rcx,0xf8(%rsp)
  ac1168:	00 
  ac1169:	48 89 94 24 00 01 00 	mov    %rdx,0x100(%rsp)
  ac1170:	00 
  ac1171:	48 89 b4 24 08 01 00 	mov    %rsi,0x108(%rsp)
  ac1178:	00 
  ac1179:	48 c7 84 24 10 01 00 	movq   $0x0,0x110(%rsp)
  ac1180:	00 00 00 00 00 
  ac1185:	4c 8d 05 ac 69 e0 00 	lea    0xe069ac(%rip),%r8        # 18c7b38 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x258>
  ac118c:	4c 89 84 24 18 01 00 	mov    %r8,0x118(%rsp)
  ac1193:	00 
  ac1194:	48 c7 84 24 20 01 00 	movq   $0x1,0x120(%rsp)
  ac119b:	00 01 00 00 00 
  ac11a0:	48 c7 84 24 28 01 00 	movq   $0x8,0x128(%rsp)
  ac11a7:	00 08 00 00 00 
  ac11ac:	66 0f ef c0          	pxor   %xmm0,%xmm0
  ac11b0:	f3 0f 7f 84 24 30 01 	movdqu %xmm0,0x130(%rsp)
  ac11b7:	00 00 
  ac11b9:	48 83 f9 01          	cmp    $0x1,%rcx
  ac11bd:	0f 84 06 05 00 00    	je     ac16c9 <virtual_mio::selector::Selector::run+0x1b39>
  ac11c3:	48 89 7c 24 60       	mov    %rdi,0x60(%rsp)
  ac11c8:	48 89 4c 24 68       	mov    %rcx,0x68(%rsp)
  ac11cd:	48 89 54 24 70       	mov    %rdx,0x70(%rsp)
  ac11d2:	48 89 74 24 78       	mov    %rsi,0x78(%rsp)
  ac11d7:	48 c7 84 24 80 00 00 	movq   $0x1,0x80(%rsp)
  ac11de:	00 01 00 00 00 
  ac11e3:	4c 8d 44 24 58       	lea    0x58(%rsp),%r8
  ac11e8:	4c 89 44 24 08       	mov    %r8,0x8(%rsp)
  ac11ed:	48 83 f9 03          	cmp    $0x3,%rcx
  ac11f1:	0f 82 d2 04 00 00    	jb     ac16c9 <virtual_mio::selector::Selector::run+0x1b39>
  ac11f7:	48 89 7c 24 30       	mov    %rdi,0x30(%rsp)
  ac11fc:	48 89 4c 24 38       	mov    %rcx,0x38(%rsp)
  ac1201:	48 89 54 24 40       	mov    %rdx,0x40(%rsp)
  ac1206:	48 89 74 24 48       	mov    %rsi,0x48(%rsp)
  ac120b:	48 83 c0 30          	add    $0x30,%rax
  ac120f:	48 8d 8c 24 88 00 00 	lea    0x88(%rsp),%rcx
  ac1216:	00 
  ac1217:	48 89 4c 24 18       	mov    %rcx,0x18(%rsp)
  ac121c:	48 c7 44 24 20 03 00 	movq   $0x3,0x20(%rsp)
  ac1223:	00 00 
  ac1225:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  ac122a:	48 8b 84 24 10 02 00 	mov    0x210(%rsp),%rax
  ac1231:	00 
  ac1232:	48 89 84 24 e0 00 00 	mov    %rax,0xe0(%rsp)
  ac1239:	00 
  ac123a:	48 c7 44 24 50 02 00 	movq   $0x2,0x50(%rsp)
  ac1241:	00 00 
  ac1243:	48 8d 05 d7 76 98 00 	lea    0x9876d7(%rip),%rax        # 1448921 <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3ebb>
  ac124a:	48 89 84 24 48 01 00 	mov    %rax,0x148(%rsp)
  ac1251:	00 
  ac1252:	48 8d 84 24 f0 00 00 	lea    0xf0(%rsp),%rax
  ac1259:	00 
  ac125a:	48 89 84 24 88 00 00 	mov    %rax,0x88(%rsp)
  ac1261:	00 
  ac1262:	48 8d 84 24 18 01 00 	lea    0x118(%rsp),%rax
  ac1269:	00 
  ac126a:	48 89 84 24 90 00 00 	mov    %rax,0x90(%rsp)
  ac1271:	00 
  ac1272:	48 8d 05 67 68 e0 00 	lea    0xe06867(%rip),%rax        # 18c7ae0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x200>
  ac1279:	48 89 84 24 98 00 00 	mov    %rax,0x98(%rsp)
  ac1280:	00 
  ac1281:	48 8d 44 24 60       	lea    0x60(%rsp),%rax
  ac1286:	48 89 84 24 a0 00 00 	mov    %rax,0xa0(%rsp)
  ac128d:	00 
  ac128e:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  ac1293:	48 89 84 24 a8 00 00 	mov    %rax,0xa8(%rsp)
  ac129a:	00 
  ac129b:	48 8d 05 a6 68 e0 00 	lea    0xe068a6(%rip),%rax        # 18c7b48 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x268>
  ac12a2:	48 89 84 24 b0 00 00 	mov    %rax,0xb0(%rsp)
  ac12a9:	00 
  ac12aa:	48 8d 44 24 30       	lea    0x30(%rsp),%rax
  ac12af:	48 89 84 24 b8 00 00 	mov    %rax,0xb8(%rsp)
  ac12b6:	00 
  ac12b7:	48 8d 84 24 48 01 00 	lea    0x148(%rsp),%rax
  ac12be:	00 
  ac12bf:	48 89 84 24 c0 00 00 	mov    %rax,0xc0(%rsp)
  ac12c6:	00 
  ac12c7:	48 8d 05 9a 68 e0 00 	lea    0xe0689a(%rip),%rax        # 18c7b68 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x288>
  ac12ce:	48 89 84 24 c8 00 00 	mov    %rax,0xc8(%rsp)
  ac12d5:	00 
  ac12d6:	f3 0f 6f 84 24 00 02 	movdqu 0x200(%rsp),%xmm0
  ac12dd:	00 00 
  ac12df:	66 0f 7f 84 24 d0 00 	movdqa %xmm0,0xd0(%rsp)
  ac12e6:	00 00 
  ac12e8:	4c 89 f7             	mov    %r14,%rdi
  ac12eb:	48 89 de             	mov    %rbx,%rsi
  ac12ee:	48 89 ea             	mov    %rbp,%rdx
  ac12f1:	48 8d 8c 24 d0 00 00 	lea    0xd0(%rsp),%rcx
  ac12f8:	00 
  ac12f9:	4c 8d 44 24 18       	lea    0x18(%rsp),%r8
  ac12fe:	ff 15 94 ae ea 00    	call   *0xeaae94(%rip)        # 196c198 <_GLOBAL_OFFSET_TABLE_+0x1118>
  ac1304:	e9 97 e9 ff ff       	jmp    abfca0 <virtual_mio::selector::Selector::run+0x110>
  ac1309:	0f b6 05 f0 78 eb 00 	movzbl 0xeb78f0(%rip),%eax        # 1978c00 <virtual_mio::selector::Selector::run::__CALLSITE+0x10>
  ac1310:	84 c0                	test   %al,%al
  ac1312:	0f 84 b7 fd ff ff    	je     ac10cf <virtual_mio::selector::Selector::run+0x153f>
  ac1318:	0f b6 c8             	movzbl %al,%ecx
  ac131b:	83 f9 01             	cmp    $0x1,%ecx
  ac131e:	74 1e                	je     ac133e <virtual_mio::selector::Selector::run+0x17ae>
  ac1320:	83 f9 02             	cmp    $0x2,%ecx
  ac1323:	75 04                	jne    ac1329 <virtual_mio::selector::Selector::run+0x1799>
  ac1325:	b0 02                	mov    $0x2,%al
  ac1327:	eb 15                	jmp    ac133e <virtual_mio::selector::Selector::run+0x17ae>
  ac1329:	48 8d 3d c0 78 eb 00 	lea    0xeb78c0(%rip),%rdi        # 1978bf0 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac1330:	ff 15 9a e0 ea 00    	call   *0xeae09a(%rip)        # 196f3d0 <_GLOBAL_OFFSET_TABLE_+0x4350>
  ac1336:	84 c0                	test   %al,%al
  ac1338:	0f 84 91 fd ff ff    	je     ac10cf <virtual_mio::selector::Selector::run+0x153f>
  ac133e:	48 8b 3d ab 78 eb 00 	mov    0xeb78ab(%rip),%rdi        # 1978bf0 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac1345:	0f b6 f0             	movzbl %al,%esi
  ac1348:	ff 15 0a 0c eb 00    	call   *0xeb0c0a(%rip)        # 1971f58 <_GLOBAL_OFFSET_TABLE_+0x6ed8>
  ac134e:	84 c0                	test   %al,%al
  ac1350:	0f 84 79 fd ff ff    	je     ac10cf <virtual_mio::selector::Selector::run+0x153f>
  ac1356:	48 8b 3d 93 78 eb 00 	mov    0xeb7893(%rip),%rdi        # 1978bf0 <virtual_mio::selector::Selector::run::__CALLSITE>
  ac135d:	48 8b 47 38          	mov    0x38(%rdi),%rax
  ac1361:	48 85 c0             	test   %rax,%rax
  ac1364:	0f 84 5f 03 00 00    	je     ac16c9 <virtual_mio::selector::Selector::run+0x1b39>
  ac136a:	48 8b 77 30          	mov    0x30(%rdi),%rsi
  ac136e:	48 8b 4f 40          	mov    0x40(%rdi),%rcx
  ac1372:	48 8b 57 48          	mov    0x48(%rdi),%rdx
  ac1376:	48 89 b4 24 f0 00 00 	mov    %rsi,0xf0(%rsp)
  ac137d:	00 
  ac137e:	48 89 84 24 f8 00 00 	mov    %rax,0xf8(%rsp)
  ac1385:	00 
  ac1386:	48 89 8c 24 00 01 00 	mov    %rcx,0x100(%rsp)
  ac138d:	00 
  ac138e:	48 89 94 24 08 01 00 	mov    %rdx,0x108(%rsp)
  ac1395:	00 
  ac1396:	48 c7 84 24 10 01 00 	movq   $0x0,0x110(%rsp)
  ac139d:	00 00 00 00 00 
  ac13a2:	4c 8d 05 8f 67 e0 00 	lea    0xe0678f(%rip),%r8        # 18c7b38 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x258>
  ac13a9:	4c 89 84 24 18 01 00 	mov    %r8,0x118(%rsp)
  ac13b0:	00 
  ac13b1:	48 c7 84 24 20 01 00 	movq   $0x1,0x120(%rsp)
  ac13b8:	00 01 00 00 00 
  ac13bd:	48 c7 84 24 28 01 00 	movq   $0x8,0x128(%rsp)
  ac13c4:	00 08 00 00 00 
  ac13c9:	66 0f ef c0          	pxor   %xmm0,%xmm0
  ac13cd:	f3 0f 7f 84 24 30 01 	movdqu %xmm0,0x130(%rsp)
  ac13d4:	00 00 
  ac13d6:	48 83 f8 01          	cmp    $0x1,%rax
  ac13da:	0f 84 e9 02 00 00    	je     ac16c9 <virtual_mio::selector::Selector::run+0x1b39>
  ac13e0:	48 89 74 24 60       	mov    %rsi,0x60(%rsp)
  ac13e5:	48 89 44 24 68       	mov    %rax,0x68(%rsp)
  ac13ea:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
  ac13ef:	48 89 54 24 78       	mov    %rdx,0x78(%rsp)
  ac13f4:	48 c7 84 24 80 00 00 	movq   $0x1,0x80(%rsp)
  ac13fb:	00 01 00 00 00 
  ac1400:	4c 8d 44 24 58       	lea    0x58(%rsp),%r8
  ac1405:	4c 89 84 24 60 01 00 	mov    %r8,0x160(%rsp)
  ac140c:	00 
  ac140d:	48 83 f8 02          	cmp    $0x2,%rax
  ac1411:	0f 86 b2 02 00 00    	jbe    ac16c9 <virtual_mio::selector::Selector::run+0x1b39>
  ac1417:	48 89 74 24 30       	mov    %rsi,0x30(%rsp)
  ac141c:	48 89 44 24 38       	mov    %rax,0x38(%rsp)
  ac1421:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
  ac1426:	48 89 54 24 48       	mov    %rdx,0x48(%rsp)
  ac142b:	48 8d 47 30          	lea    0x30(%rdi),%rax
  ac142f:	48 8d 8c 24 88 00 00 	lea    0x88(%rsp),%rcx
  ac1436:	00 
  ac1437:	48 89 8c 24 48 01 00 	mov    %rcx,0x148(%rsp)
  ac143e:	00 
  ac143f:	48 c7 84 24 50 01 00 	movq   $0x3,0x150(%rsp)
  ac1446:	00 03 00 00 00 
  ac144b:	48 89 84 24 58 01 00 	mov    %rax,0x158(%rsp)
  ac1452:	00 
  ac1453:	48 c7 44 24 50 02 00 	movq   $0x2,0x50(%rsp)
  ac145a:	00 00 
  ac145c:	48 8d 05 be 74 98 00 	lea    0x9874be(%rip),%rax        # 1448921 <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3ebb>
  ac1463:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  ac1468:	48 8d 84 24 f0 00 00 	lea    0xf0(%rsp),%rax
  ac146f:	00 
  ac1470:	48 89 84 24 88 00 00 	mov    %rax,0x88(%rsp)
  ac1477:	00 
  ac1478:	48 8d 84 24 18 01 00 	lea    0x118(%rsp),%rax
  ac147f:	00 
  ac1480:	48 89 84 24 90 00 00 	mov    %rax,0x90(%rsp)
  ac1487:	00 
  ac1488:	48 8d 05 51 66 e0 00 	lea    0xe06651(%rip),%rax        # 18c7ae0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x200>
  ac148f:	48 89 84 24 98 00 00 	mov    %rax,0x98(%rsp)
  ac1496:	00 
  ac1497:	48 8d 44 24 60       	lea    0x60(%rsp),%rax
  ac149c:	48 89 84 24 a0 00 00 	mov    %rax,0xa0(%rsp)
  ac14a3:	00 
  ac14a4:	48 8d 84 24 60 01 00 	lea    0x160(%rsp),%rax
  ac14ab:	00 
  ac14ac:	48 89 84 24 a8 00 00 	mov    %rax,0xa8(%rsp)
  ac14b3:	00 
  ac14b4:	48 8d 05 8d 66 e0 00 	lea    0xe0668d(%rip),%rax        # 18c7b48 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x268>
  ac14bb:	48 89 84 24 b0 00 00 	mov    %rax,0xb0(%rsp)
  ac14c2:	00 
  ac14c3:	48 8d 44 24 30       	lea    0x30(%rsp),%rax
  ac14c8:	48 89 84 24 b8 00 00 	mov    %rax,0xb8(%rsp)
  ac14cf:	00 
  ac14d0:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  ac14d5:	48 89 84 24 c0 00 00 	mov    %rax,0xc0(%rsp)
  ac14dc:	00 
  ac14dd:	48 8d 05 84 66 e0 00 	lea    0xe06684(%rip),%rax        # 18c7b68 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x288>
  ac14e4:	48 89 84 24 c8 00 00 	mov    %rax,0xc8(%rsp)
  ac14eb:	00 
  ac14ec:	48                   	rex.W
  ac14ed:	8d                   	.byte 0x8d
  ac14ee:	b4 24                	mov    $0x24,%ah
