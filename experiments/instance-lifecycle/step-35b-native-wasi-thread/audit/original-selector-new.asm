
CVW/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/wasmer-go/packaged/lib/linux-amd64/libwasmer.so:     file format elf64-x86-64


Disassembly of section .text:

0000000000abec00 <virtual_mio::selector::Selector::new>:
  abec00:	55                   	push   %rbp
  abec01:	41 57                	push   %r15
  abec03:	41 56                	push   %r14
  abec05:	41 54                	push   %r12
  abec07:	53                   	push   %rbx
  abec08:	48 81 ec c0 00 00 00 	sub    $0xc0,%rsp
  abec0f:	48 8d 7c 24 30       	lea    0x30(%rsp),%rdi
  abec14:	ff 15 76 dd ea 00    	call   *0xeadd76(%rip)        # 196c990 <_GLOBAL_OFFSET_TABLE_+0x1910>
  abec1a:	83 7c 24 30 00       	cmpl   $0x0,0x30(%rsp)
  abec1f:	0f 85 5a 02 00 00    	jne    abee7f <virtual_mio::selector::Selector::new+0x27f>
  abec25:	8b 44 24 34          	mov    0x34(%rsp),%eax
  abec29:	89 44 24 0c          	mov    %eax,0xc(%rsp)
  abec2d:	48 8d 7c 24 30       	lea    0x30(%rsp),%rdi
  abec32:	48 8d 74 24 0c       	lea    0xc(%rsp),%rsi
  abec37:	ff 15 53 da ea 00    	call   *0xeada53(%rip)        # 196c690 <_GLOBAL_OFFSET_TABLE_+0x1610>
  abec3d:	83 7c 24 30 00       	cmpl   $0x0,0x30(%rsp)
  abec42:	0f 85 6b 02 00 00    	jne    abeeb3 <virtual_mio::selector::Selector::new+0x2b3>
  abec48:	8b 6c 24 34          	mov    0x34(%rsp),%ebp
  abec4c:	48 8d 7c 24 30       	lea    0x30(%rsp),%rdi
  abec51:	48 8d 74 24 0c       	lea    0xc(%rsp),%rsi
  abec56:	31 d2                	xor    %edx,%edx
  abec58:	ff 15 6a 02 eb 00    	call   *0xeb026a(%rip)        # 196eec8 <_GLOBAL_OFFSET_TABLE_+0x3e48>
  abec5e:	83 7c 24 30 00       	cmpl   $0x0,0x30(%rsp)
  abec63:	0f 85 7b 02 00 00    	jne    abeee4 <virtual_mio::selector::Selector::new+0x2e4>
  abec69:	44 8b 74 24 34       	mov    0x34(%rsp),%r14d
  abec6e:	66 48 8d 3d a2 22 eb 	data16 lea 0xeb22a2(%rip),%rdi        # 1970f18 <_GLOBAL_OFFSET_TABLE_+0x5e98>
  abec75:	00 
  abec76:	66 66 48 e8 c2 13 6a 	data16 data16 rex.W call 160040 <__tls_get_addr@plt>
  abec7d:	ff 
  abec7e:	48 83 38 00          	cmpq   $0x0,(%rax)
  abec82:	74 1a                	je     abec9e <virtual_mio::selector::Selector::new+0x9e>
  abec84:	66 48 8d 3d 8c 22 eb 	data16 lea 0xeb228c(%rip),%rdi        # 1970f18 <_GLOBAL_OFFSET_TABLE_+0x5e98>
  abec8b:	00 
  abec8c:	66 66 48 e8 ac 13 6a 	data16 data16 rex.W call 160040 <__tls_get_addr@plt>
  abec93:	ff 
  abec94:	48 8b 58 08          	mov    0x8(%rax),%rbx
  abec98:	4c 8b 78 10          	mov    0x10(%rax),%r15
  abec9c:	eb 2b                	jmp    abecc9 <virtual_mio::selector::Selector::new+0xc9>
  abec9e:	ff 15 a4 11 eb 00    	call   *0xeb11a4(%rip)        # 196fe48 <_GLOBAL_OFFSET_TABLE_+0x4dc8>
  abeca4:	48 89 c3             	mov    %rax,%rbx
  abeca7:	49 89 d7             	mov    %rdx,%r15
  abecaa:	66 48 8d 3d 66 22 eb 	data16 lea 0xeb2266(%rip),%rdi        # 1970f18 <_GLOBAL_OFFSET_TABLE_+0x5e98>
  abecb1:	00 
  abecb2:	66 66 48 e8 86 13 6a 	data16 data16 rex.W call 160040 <__tls_get_addr@plt>
  abecb9:	ff 
  abecba:	48 c7 00 01 00 00 00 	movq   $0x1,(%rax)
  abecc1:	48 89 58 08          	mov    %rbx,0x8(%rax)
  abecc5:	4c 89 78 10          	mov    %r15,0x10(%rax)
  abecc9:	4c 8d 63 01          	lea    0x1(%rbx),%r12
  abeccd:	66 48 8d 3d 43 22 eb 	data16 lea 0xeb2243(%rip),%rdi        # 1970f18 <_GLOBAL_OFFSET_TABLE_+0x5e98>
  abecd4:	00 
  abecd5:	66 66 48 e8 63 13 6a 	data16 data16 rex.W call 160040 <__tls_get_addr@plt>
  abecdc:	ff 
  abecdd:	4c 89 60 08          	mov    %r12,0x8(%rax)
  abece1:	0f 10 05 08 8d e0 00 	movups 0xe08d08(%rip),%xmm0        # 18c79f0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x110>
  abece8:	0f 11 84 24 b0 00 00 	movups %xmm0,0xb0(%rsp)
  abecef:	00 
  abecf0:	0f 10 05 e9 8c e0 00 	movups 0xe08ce9(%rip),%xmm0        # 18c79e0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x100>
  abecf7:	0f 11 84 24 a0 00 00 	movups %xmm0,0xa0(%rsp)
  abecfe:	00 
  abecff:	48 c7 44 24 30 01 00 	movq   $0x1,0x30(%rsp)
  abed06:	00 00 
  abed08:	48 c7 44 24 38 01 00 	movq   $0x1,0x38(%rsp)
  abed0f:	00 00 
  abed11:	48 c7 44 24 40 01 00 	movq   $0x1,0x40(%rsp)
  abed18:	00 00 
  abed1a:	c7 44 24 48 00 00 00 	movl   $0x0,0x48(%rsp)
  abed21:	00 
  abed22:	c6 44 24 4c 00       	movb   $0x0,0x4c(%rsp)
  abed27:	0f 10 84 24 9d 00 00 	movups 0x9d(%rsp),%xmm0
  abed2e:	00 
  abed2f:	0f 11 44 24 4d       	movups %xmm0,0x4d(%rsp)
  abed34:	0f 10 84 24 ad 00 00 	movups 0xad(%rsp),%xmm0
  abed3b:	00 
  abed3c:	0f 11 44 24 5d       	movups %xmm0,0x5d(%rsp)
  abed41:	8b 84 24 bc 00 00 00 	mov    0xbc(%rsp),%eax
  abed48:	89 44 24 6c          	mov    %eax,0x6c(%rsp)
  abed4c:	48 89 5c 24 70       	mov    %rbx,0x70(%rsp)
  abed51:	4c 89 7c 24 78       	mov    %r15,0x78(%rsp)
  abed56:	48 c7 84 24 80 00 00 	movq   $0xa,0x80(%rsp)
  abed5d:	00 0a 00 00 00 
  abed62:	89 ac 24 88 00 00 00 	mov    %ebp,0x88(%rsp)
  abed69:	44 89 b4 24 90 00 00 	mov    %r14d,0x90(%rsp)
  abed70:	00 
  abed71:	48 8d 05 0a a9 eb 00 	lea    0xeba90a(%rip),%rax        # 1979682 <__rust_no_alloc_shim_is_unstable>
  abed78:	0f b6 00             	movzbl (%rax),%eax
  abed7b:	bf 68 00 00 00       	mov    $0x68,%edi
  abed80:	be 08 00 00 00       	mov    $0x8,%esi
  abed85:	ff 15 8d 25 eb 00    	call   *0xeb258d(%rip)        # 1971318 <_GLOBAL_OFFSET_TABLE_+0x6298>
  abed8b:	48 85 c0             	test   %rax,%rax
  abed8e:	0f 84 81 01 00 00    	je     abef15 <virtual_mio::selector::Selector::new+0x315>
  abed94:	48 8b 8c 24 90 00 00 	mov    0x90(%rsp),%rcx
  abed9b:	00 
  abed9c:	48 89 48 60          	mov    %rcx,0x60(%rax)
  abeda0:	0f 10 84 24 80 00 00 	movups 0x80(%rsp),%xmm0
  abeda7:	00 
  abeda8:	0f 11 40 50          	movups %xmm0,0x50(%rax)
  abedac:	0f 10 44 24 70       	movups 0x70(%rsp),%xmm0
  abedb1:	0f 11 40 40          	movups %xmm0,0x40(%rax)
  abedb5:	0f 10 44 24 30       	movups 0x30(%rsp),%xmm0
  abedba:	0f 10 4c 24 40       	movups 0x40(%rsp),%xmm1
  abedbf:	0f 10 54 24 50       	movups 0x50(%rsp),%xmm2
  abedc4:	0f 10 5c 24 60       	movups 0x60(%rsp),%xmm3
  abedc9:	0f 11 58 30          	movups %xmm3,0x30(%rax)
  abedcd:	0f 11 50 20          	movups %xmm2,0x20(%rax)
  abedd1:	0f 11 48 10          	movups %xmm1,0x10(%rax)
  abedd5:	0f 11 00             	movups %xmm0,(%rax)
  abedd8:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  abeddd:	f0 48 ff 00          	lock incq (%rax)
  abede1:	0f 8e 6f 01 00 00    	jle    abef56 <virtual_mio::selector::Selector::new+0x356>
  abede7:	8b 4c 24 0c          	mov    0xc(%rsp),%ecx
  abedeb:	48 ba 00 00 00 00 00 	movabs $0x8000000000000000,%rdx
  abedf2:	00 00 80 
  abedf5:	48 89 54 24 40       	mov    %rdx,0x40(%rsp)
  abedfa:	48 c7 44 24 30 00 00 	movq   $0x0,0x30(%rsp)
  abee01:	00 00 
  abee03:	48 8d 7c 24 10       	lea    0x10(%rsp),%rdi
  abee08:	48 8d 74 24 30       	lea    0x30(%rsp),%rsi
  abee0d:	48 89 c2             	mov    %rax,%rdx
  abee10:	e8 db 5e 00 00       	call   ac4cf0 <std::thread::Builder::spawn_unchecked>
  abee15:	48 83 7c 24 10 00    	cmpq   $0x0,0x10(%rsp)
  abee1b:	0f 84 06 01 00 00    	je     abef27 <virtual_mio::selector::Selector::new+0x327>
  abee21:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
  abee26:	48 89 44 24 40       	mov    %rax,0x40(%rsp)
  abee2b:	0f 10 44 24 10       	movups 0x10(%rsp),%xmm0
  abee30:	0f 29 44 24 30       	movaps %xmm0,0x30(%rsp)
  abee35:	48 8d 7c 24 40       	lea    0x40(%rsp),%rdi
  abee3a:	ff 15 58 f1 ea 00    	call   *0xeaf158(%rip)        # 196df98 <_GLOBAL_OFFSET_TABLE_+0x2f18>
  abee40:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
  abee45:	f0 48 ff 08          	lock decq (%rax)
  abee49:	75 0a                	jne    abee55 <virtual_mio::selector::Selector::new+0x255>
  abee4b:	48 8d 7c 24 30       	lea    0x30(%rsp),%rdi
  abee50:	e8 8b 53 00 00       	call   ac41e0 <alloc::sync::Arc<T,A>::drop_slow>
  abee55:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
  abee5a:	f0 48 ff 08          	lock decq (%rax)
  abee5e:	75 0a                	jne    abee6a <virtual_mio::selector::Selector::new+0x26a>
  abee60:	48 8d 7c 24 38       	lea    0x38(%rsp),%rdi
  abee65:	e8 06 54 00 00       	call   ac4270 <alloc::sync::Arc<T,A>::drop_slow>
  abee6a:	48 8b 44 24 28       	mov    0x28(%rsp),%rax
  abee6f:	48 81 c4 c0 00 00 00 	add    $0xc0,%rsp
  abee76:	5b                   	pop    %rbx
  abee77:	41 5c                	pop    %r12
  abee79:	41 5e                	pop    %r14
  abee7b:	41 5f                	pop    %r15
  abee7d:	5d                   	pop    %rbp
  abee7e:	c3                   	ret
  abee7f:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
  abee84:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
  abee89:	48 8d 3d 38 99 98 00 	lea    0x989938(%rip),%rdi        # 14487c8 <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3d62>
  abee90:	48 8d 0d c1 8a e0 00 	lea    0xe08ac1(%rip),%rcx        # 18c7958 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x78>
  abee97:	4c 8d 05 fa 8a e0 00 	lea    0xe08afa(%rip),%r8        # 18c7998 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0xb8>
  abee9e:	48 8d 54 24 10       	lea    0x10(%rsp),%rdx
  abeea3:	be 2b 00 00 00       	mov    $0x2b,%esi
  abeea8:	ff 15 c2 ee ea 00    	call   *0xeaeec2(%rip)        # 196dd70 <_GLOBAL_OFFSET_TABLE_+0x2cf0>
  abeeae:	e9 a3 00 00 00       	jmp    abef56 <virtual_mio::selector::Selector::new+0x356>
  abeeb3:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
  abeeb8:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
  abeebd:	48 8d 3d 4d 99 98 00 	lea    0x98994d(%rip),%rdi        # 1448811 <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3dab>
  abeec4:	48 8d 0d 8d 8a e0 00 	lea    0xe08a8d(%rip),%rcx        # 18c7958 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x78>
  abeecb:	4c 8d 05 de 8a e0 00 	lea    0xe08ade(%rip),%r8        # 18c79b0 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0xd0>
  abeed2:	48 8d 54 24 10       	lea    0x10(%rsp),%rdx
  abeed7:	be 25 00 00 00       	mov    $0x25,%esi
  abeedc:	ff 15 8e ee ea 00    	call   *0xeaee8e(%rip)        # 196dd70 <_GLOBAL_OFFSET_TABLE_+0x2cf0>
  abeee2:	eb 72                	jmp    abef56 <virtual_mio::selector::Selector::new+0x356>
  abeee4:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
  abeee9:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
  abeeee:	48 8d 3d d3 98 98 00 	lea    0x9898d3(%rip),%rdi        # 14487c8 <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3d62>
  abeef5:	48 8d 0d 5c 8a e0 00 	lea    0xe08a5c(%rip),%rcx        # 18c7958 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x78>
  abeefc:	4c 8d 05 c5 8a e0 00 	lea    0xe08ac5(%rip),%r8        # 18c79c8 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0xe8>
  abef03:	48 8d 54 24 10       	lea    0x10(%rsp),%rdx
  abef08:	be 2b 00 00 00       	mov    $0x2b,%esi
  abef0d:	ff 15 5d ee ea 00    	call   *0xeaee5d(%rip)        # 196dd70 <_GLOBAL_OFFSET_TABLE_+0x2cf0>
  abef13:	eb 41                	jmp    abef56 <virtual_mio::selector::Selector::new+0x356>
  abef15:	bf 08 00 00 00       	mov    $0x8,%edi
  abef1a:	be 68 00 00 00       	mov    $0x68,%esi
  abef1f:	ff 15 c3 e7 ea 00    	call   *0xeae7c3(%rip)        # 196d6e8 <_GLOBAL_OFFSET_TABLE_+0x2668>
  abef25:	eb 2f                	jmp    abef56 <virtual_mio::selector::Selector::new+0x356>
  abef27:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
  abef2c:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  abef31:	48 8d 3d fe 98 98 00 	lea    0x9898fe(%rip),%rdi        # 1448836 <anon.130bac118c5e3889bb7f0386c08a42c2.0.llvm.16697966254283140102+0x3dd0>
  abef38:	48 8d 0d 19 8a e0 00 	lea    0xe08a19(%rip),%rcx        # 18c7958 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x78>
  abef3f:	4c 8d 05 ba 8a e0 00 	lea    0xe08aba(%rip),%r8        # 18c7a00 <<wasmer_wasix_types::wasi::wasix_manual::EpollCtl as wasmer::utils::native::convert::FromToNativeWasmType>::from_native::__CALLSITE::META+0x120>
  abef46:	48 8d 54 24 30       	lea    0x30(%rsp),%rdx
  abef4b:	be 16 00 00 00       	mov    $0x16,%esi
  abef50:	ff 15 1a ee ea 00    	call   *0xeaee1a(%rip)        # 196dd70 <_GLOBAL_OFFSET_TABLE_+0x2cf0>
  abef56:	0f 0b                	ud2
  abef58:	48 89 c3             	mov    %rax,%rbx
  abef5b:	44 89 f7             	mov    %r14d,%edi
  abef5e:	ff 15 2c d8 ea 00    	call   *0xead82c(%rip)        # 196c790 <close@GLIBC_2.2.5>
  abef64:	e9 86 00 00 00       	jmp    abefef <virtual_mio::selector::Selector::new+0x3ef>
  abef69:	48 89 c3             	mov    %rax,%rbx
  abef6c:	eb 18                	jmp    abef86 <virtual_mio::selector::Selector::new+0x386>
  abef6e:	48 89 c3             	mov    %rax,%rbx
  abef71:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
  abef76:	f0 48 ff 08          	lock decq (%rax)
  abef7a:	75 0a                	jne    abef86 <virtual_mio::selector::Selector::new+0x386>
  abef7c:	48 8d 7c 24 30       	lea    0x30(%rsp),%rdi
  abef81:	e8 5a 52 00 00       	call   ac41e0 <alloc::sync::Arc<T,A>::drop_slow>
  abef86:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
  abef8b:	f0 48 ff 08          	lock decq (%rax)
  abef8f:	0f 85 b6 00 00 00    	jne    abf04b <virtual_mio::selector::Selector::new+0x44b>
  abef95:	48 8d 7c 24 38       	lea    0x38(%rsp),%rdi
  abef9a:	e8 d1 52 00 00       	call   ac4270 <alloc::sync::Arc<T,A>::drop_slow>
  abef9f:	e9 a7 00 00 00       	jmp    abf04b <virtual_mio::selector::Selector::new+0x44b>
  abefa4:	ff 15 be c3 ea 00    	call   *0xeac3be(%rip)        # 196b368 <_GLOBAL_OFFSET_TABLE_+0x2e8>
  abefaa:	48 89 c3             	mov    %rax,%rbx
  abefad:	48 8d 7c 24 30       	lea    0x30(%rsp),%rdi
  abefb2:	e8 f9 fa ff ff       	call   abeab0 <core::ptr::drop_in_place<std::io::error::Error>>
  abefb7:	e9 8f 00 00 00       	jmp    abf04b <virtual_mio::selector::Selector::new+0x44b>
  abefbc:	ff 15 a6 c3 ea 00    	call   *0xeac3a6(%rip)        # 196b368 <_GLOBAL_OFFSET_TABLE_+0x2e8>
  abefc2:	48 89 c3             	mov    %rax,%rbx
  abefc5:	48 8d 7c 24 30       	lea    0x30(%rsp),%rdi
  abefca:	e8 a1 fb ff ff       	call   abeb70 <core::ptr::drop_in_place<alloc::sync::ArcInner<virtual_mio::selector::Selector>>>
  abefcf:	eb 50                	jmp    abf021 <virtual_mio::selector::Selector::new+0x421>
  abefd1:	ff 15 91 c3 ea 00    	call   *0xeac391(%rip)        # 196b368 <_GLOBAL_OFFSET_TABLE_+0x2e8>
  abefd7:	48 89 c3             	mov    %rax,%rbx
  abefda:	48 8d 7c 24 10       	lea    0x10(%rsp),%rdi
  abefdf:	e8 cc fa ff ff       	call   abeab0 <core::ptr::drop_in_place<std::io::error::Error>>
  abefe4:	eb 09                	jmp    abefef <virtual_mio::selector::Selector::new+0x3ef>
  abefe6:	ff 15 7c c3 ea 00    	call   *0xeac37c(%rip)        # 196b368 <_GLOBAL_OFFSET_TABLE_+0x2e8>
  abefec:	48 89 c3             	mov    %rax,%rbx
  abefef:	89 ef                	mov    %ebp,%edi
  abeff1:	ff 15 99 d7 ea 00    	call   *0xead799(%rip)        # 196c790 <close@GLIBC_2.2.5>
  abeff7:	8b 7c 24 0c          	mov    0xc(%rsp),%edi
  abeffb:	ff 15 8f d7 ea 00    	call   *0xead78f(%rip)        # 196c790 <close@GLIBC_2.2.5>
  abf001:	48 89 df             	mov    %rbx,%rdi
  abf004:	e8 47 10 6a ff       	call   160050 <_Unwind_Resume@plt>
  abf009:	48 89 c3             	mov    %rax,%rbx
  abf00c:	48 8d 7c 24 10       	lea    0x10(%rsp),%rdi
  abf011:	e8 9a fa ff ff       	call   abeab0 <core::ptr::drop_in_place<std::io::error::Error>>
  abf016:	eb 09                	jmp    abf021 <virtual_mio::selector::Selector::new+0x421>
  abf018:	ff 15 4a c3 ea 00    	call   *0xeac34a(%rip)        # 196b368 <_GLOBAL_OFFSET_TABLE_+0x2e8>
  abf01e:	48 89 c3             	mov    %rax,%rbx
  abf021:	8b 7c 24 0c          	mov    0xc(%rsp),%edi
  abf025:	ff 15 65 d7 ea 00    	call   *0xead765(%rip)        # 196c790 <close@GLIBC_2.2.5>
  abf02b:	48 89 df             	mov    %rbx,%rdi
  abf02e:	e8 1d 10 6a ff       	call   160050 <_Unwind_Resume@plt>
  abf033:	48 89 c3             	mov    %rax,%rbx
  abf036:	48 8d 7c 24 10       	lea    0x10(%rsp),%rdi
  abf03b:	e8 70 fa ff ff       	call   abeab0 <core::ptr::drop_in_place<std::io::error::Error>>
  abf040:	eb 1e                	jmp    abf060 <virtual_mio::selector::Selector::new+0x460>
  abf042:	ff 15 20 c3 ea 00    	call   *0xeac320(%rip)        # 196b368 <_GLOBAL_OFFSET_TABLE_+0x2e8>
  abf048:	48 89 c3             	mov    %rax,%rbx
  abf04b:	48 8b 44 24 28       	mov    0x28(%rsp),%rax
  abf050:	f0 48 ff 08          	lock decq (%rax)
  abf054:	75 0a                	jne    abf060 <virtual_mio::selector::Selector::new+0x460>
  abf056:	48 8d 7c 24 28       	lea    0x28(%rsp),%rdi
  abf05b:	e8 e0 53 00 00       	call   ac4440 <alloc::sync::Arc<T,A>::drop_slow>
  abf060:	48 89 df             	mov    %rbx,%rdi
  abf063:	e8 e8 0f 6a ff       	call   160050 <_Unwind_Resume@plt>
  abf068:	ff 15 fa c2 ea 00    	call   *0xeac2fa(%rip)        # 196b368 <_GLOBAL_OFFSET_TABLE_+0x2e8>
  abf06e:	66 90                	xchg   %ax,%ax
