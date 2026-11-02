TEXT chainmaker.org/chainmaker/vm-wasmer/v2.(*staticMemoryPlan).restore(SB) /home/frankie/mygitprojects/.worktrees/cvw-step38/experiments/instance-lifecycle/step-38-copy-range-cost/source/A/vm/step35_static.go
  step35_static.go:236	0x16feba0		4c8d6424a0			LEAQ -0x60(SP), R12											
  step35_static.go:236	0x16feba5		4d3b6610			CMPQ R12, 0x10(R14)											
  step35_static.go:236	0x16feba9		0f861b030000			JBE 0x16feeca												
  step35_static.go:236	0x16febaf		55				PUSHQ BP												
  step35_static.go:236	0x16febb0		4889e5				MOVQ SP, BP												
  step35_static.go:236	0x16febb3		4881ecd8000000			SUBQ $0xd8, SP												
  step35_static.go:236	0x16febba		4c89942420010000		MOVQ R10, 0x120(SP)											
  step35_static.go:237	0x16febc2		48898424e8000000		MOVQ AX, 0xe8(SP)											
  step35_static.go:237	0x16febca		48898c24f8000000		MOVQ CX, 0xf8(SP)											
  step35_static.go:237	0x16febd2		48395868			CMPQ 0x68(AX), BX											
  step35_static.go:237	0x16febd6		7407				JE 0x16febdf												
  step35_static.go:237	0x16febd8		ba01000000			MOVL $0x1, DX												
  step35_static.go:237	0x16febdd		eb64				JMP 0x16fec43												
  step35_static.go:237	0x16febdf		488b5028			MOVQ 0x28(AX), DX											
  step35_static.go:237	0x16febe3		4939d3				CMPQ R11, DX												
  step35_static.go:237	0x16febe6		7407				JE 0x16febef												
  step35_static.go:237	0x16febe8		ba01000000			MOVL $0x1, DX												
  step35_static.go:237	0x16febed		eb54				JMP 0x16fec43												
  step35_static.go:237	0x16febef		4c898c2418010000		MOVQ R9, 0x118(SP)											
  step35_static.go:237	0x16febf7		4c899c2428010000		MOVQ R11, 0x128(SP)											
  step35_static.go:237	0x16febff		4c89942420010000		MOVQ R10, 0x120(SP)											
  step35_static.go:237	0x16fec07		488b4020			MOVQ 0x20(AX), AX											
  step35_static.go:237	0x16fec0b		4c89d3				MOVQ R10, BX												
  step35_static.go:237	0x16fec0e		4889d1				MOVQ DX, CX												
  step35_static.go:237	0x16fec11		e82a423eff			CALL local.runtime.memequal(SB)										
  step35_static.go:237	0x16fec16		83f001				XORL $0x1, AX												
  step35_static.go:242	0x16fec19		488b8c24f8000000		MOVQ 0xf8(SP), CX											
  step35_static.go:237	0x16fec21		4c8b8c2418010000		MOVQ 0x118(SP), R9											
  step35_static.go:237	0x16fec29		4c8b942420010000		MOVQ 0x120(SP), R10											
  step35_static.go:237	0x16fec31		4c8b9c2428010000		MOVQ 0x128(SP), R11											
  step35_static.go:237	0x16fec39		89c2				MOVL AX, DX												
  step35_static.go:237	0x16fec3b		488b8424e8000000		MOVQ 0xe8(SP), AX											
  step35_static.go:237	0x16fec43		84d2				TESTL DL, DL												
  step35_static.go:237	0x16fec45		0f850f010000			JNE 0x16fed5a												
  step35_static.go:237	0x16fec4b		488d7c2468			LEAQ 0x68(SP), DI											
  step35_static.go:237	0x16fec50		488d7ff0			LEAQ -0x10(DI), DI											
  step35_static.go:237	0x16fec54		660f1f840000000000		NOPW 0(AX)(AX*1)											
  step35_static.go:237	0x16fec5d		0f1f00				NOPL 0(AX)												
  step35_static.go:237	0x16fec60		48896c24f0			MOVQ BP, -0x10(SP)											
  step35_static.go:237	0x16fec65		488d6c24f0			LEAQ -0x10(SP), BP											
  step35_static.go:237	0x16fec6a		e8d71847ff			CALL 0xb70546												
  step35_static.go:237	0x16fec6f		488b6d00			MOVQ 0(BP), BP												
  step35_static.go:237	0x16fec73		498b11				MOVQ 0(R9), DX												
  step35_static.go:237	0x16fec76		498b7108			MOVQ 0x8(R9), SI											
  step35_static.go:237	0x16fec7a		4889742470			MOVQ SI, 0x70(SP)											
  step35_static.go:237	0x16fec7f		4889542468			MOVQ DX, 0x68(SP)											
  step35_static.go:237	0x16fec84		48c784248000000001000000	MOVQ $0x1, 0x80(SP)											
  step35_static.go:237	0x16fec90		488d1561b39d00			LEAQ testing..stmp_7(SB), DX										
  step35_static.go:237	0x16fec97		4889542478			MOVQ DX, 0x78(SP)											
  step35_static.go:237	0x16fec9c		498b7110			MOVQ 0x10(R9), SI											
  step35_static.go:237	0x16feca0		4d8b4118			MOVQ 0x18(R9), R8											
  step35_static.go:237	0x16feca4		4c89842490000000		MOVQ R8, 0x90(SP)											
  step35_static.go:237	0x16fecac		4889b42488000000		MOVQ SI, 0x88(SP)											
  step35_static.go:237	0x16fecb4		48c78424a000000001000000	MOVQ $0x1, 0xa0(SP)											
  step35_static.go:237	0x16fecc0		4889942498000000		MOVQ DX, 0x98(SP)											
  step35_static.go:237	0x16fecc8		488b7010			MOVQ 0x10(AX), SI											
  step35_static.go:237	0x16feccc		4c8b4018			MOVQ 0x18(AX), R8											
  step35_static.go:237	0x16fecd0		4c898424b0000000		MOVQ R8, 0xb0(SP)											
  step35_static.go:237	0x16fecd8		4889b424a8000000		MOVQ SI, 0xa8(SP)											
  step35_static.go:237	0x16fece0		48c78424c000000001000000	MOVQ $0x1, 0xc0(SP)											
  step35_static.go:237	0x16fecec		48899424b8000000		MOVQ DX, 0xb8(SP)											
  step35_static.go:237	0x16fecf4		4c899c24d0000000		MOVQ R11, 0xd0(SP)											
  step35_static.go:237	0x16fecfc		4c899424c8000000		MOVQ R10, 0xc8(SP)											
  step35_static.go:237	0x16fed04		488d442428			LEAQ 0x28(SP), AX											
  step35_static.go:237	0x16fed09		488d5c2468			LEAQ 0x68(SP), BX											
  step35_static.go:237	0x16fed0e		b907000000			MOVL $0x7, CX												
  step35_static.go:237	0x16fed13		4889cf				MOVQ CX, DI												
  step35_static.go:237	0x16fed16		e825cd44ff			CALL local.runtime.concatbytes(SB)									
  step35_static.go:237	0x16fed1b		0f1f440000			NOPL 0(AX)(AX*1)											
  step35_static.go:237	0x16fed20		e8fbd8ffff			CALL chainmaker.org/chainmaker/vm-wasmer/v2.staticSHA(SB)						
  step35_static.go:237	0x16fed25		488b9424e8000000		MOVQ 0xe8(SP), DX											
  step35_static.go:237	0x16fed2d		488b4a08			MOVQ 0x8(DX), CX											
  step35_static.go:237	0x16fed31		4839cb				CMPQ BX, CX												
  step35_static.go:237	0x16fed34		7407				JE 0x16fed3d												
  step35_static.go:237	0x16fed36		b801000000			MOVL $0x1, AX												
  step35_static.go:237	0x16fed3b		eb19				JMP 0x16fed56												
  step35_static.go:237	0x16fed3d		488b12				MOVQ 0(DX), DX												
  step35_static.go:237	0x16fed40		4889c3				MOVQ AX, BX												
  step35_static.go:237	0x16fed43		4889d0				MOVQ DX, AX												
  step35_static.go:237	0x16fed46		e8f5403eff			CALL local.runtime.memequal(SB)										
  step35_static.go:237	0x16fed4b		83f001				XORL $0x1, AX												
  step35_static.go:247	0x16fed4e		488b9424e8000000		MOVQ 0xe8(SP), DX											
  step35_static.go:237	0x16fed56		84c0				TESTL AL, AL												
  step35_static.go:237	0x16fed58		7421				JE 0x16fed7b												
  step35_static.go:238	0x16fed5a		488d05c77e7200			LEAQ 0x727ec7(IP), AX											
  step35_static.go:238	0x16fed61		bb26000000			MOVL $_ZN3std11collections4hash3map11RandomState3new4KEYS7__getit5__KEY17hc510b8383306a22dE+30(SB), BX	
  step35_static.go:238	0x16fed66		31c9				XORL CX, CX												
  step35_static.go:238	0x16fed68		31ff				XORL DI, DI												
  step35_static.go:238	0x16fed6a		4889fe				MOVQ DI, SI												
  step35_static.go:238	0x16fed6d		e82e2851ff			CALL fmt.Errorf(SB)											
  step35_static.go:238	0x16fed72		4881c4d8000000			ADDQ $0xd8, SP												
  step35_static.go:238	0x16fed79		5d				POPQ BP													
  step35_static.go:238	0x16fed7a		c3				RET													
  step35_static.go:242	0x16fed7b		488b9424f8000000		MOVQ 0xf8(SP), DX											
  step35_static.go:242	0x16fed83		488b4208			MOVQ 0x8(DX), AX											
  step35_static.go:242	0x16fed87		488d1da5fb6e00			LEAQ 0x6efba5(IP), BX											
  step35_static.go:242	0x16fed8e		b906000000			MOVL $0x6, CX												
  step35_static.go:242	0x16fed93		e8e88696ff			CALL local.chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go.(*Exports).GetMemory(SB)			
  step35_static.go:243	0x16fed98		4885db				TESTQ BX, BX												
  step35_static.go:243	0x16fed9b		754b				JNE 0x16fede8												
  step35_static.go:243	0x16fed9d		0f1f00				NOPL 0(AX)												
  step35_static.go:246	0x16feda0		e87bda96ff			CALL chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go.(*Memory).Data(SB)				
  step35_static.go:247	0x16feda5		488b9424e8000000		MOVQ 0xe8(SP), DX											
  step35_static.go:247	0x16fedad		48395a38			CMPQ 0x38(DX), BX											
  step35_static.go:247	0x16fedb1		7514				JNE 0x16fedc7												
  step35_static.go:246	0x16fedb3		4889442458			MOVQ AX, 0x58(SP)											
  step35_static.go:246	0x16fedb8		48894c2448			MOVQ CX, 0x48(SP)											
  step35_static.go:250	0x16fedbd		488b7250			MOVQ 0x50(DX), SI											
  step35_static.go:250	0x16fedc1		488b7a58			MOVQ 0x58(DX), DI											
  step35_static.go:250	0x16fedc5		eb39				JMP 0x16fee00												
  step35_static.go:248	0x16fedc7		488d05807e7200			LEAQ 0x727e80(IP), AX											
  step35_static.go:248	0x16fedce		bb26000000			MOVL $_ZN3std11collections4hash3map11RandomState3new4KEYS7__getit5__KEY17hc510b8383306a22dE+30(SB), BX	
  step35_static.go:248	0x16fedd3		31c9				XORL CX, CX												
  step35_static.go:248	0x16fedd5		31ff				XORL DI, DI												
  step35_static.go:248	0x16fedd7		4889fe				MOVQ DI, SI												
  step35_static.go:248	0x16fedda		e8c12751ff			CALL fmt.Errorf(SB)											
  step35_static.go:248	0x16feddf		4881c4d8000000			ADDQ $0xd8, SP												
  step35_static.go:248	0x16fede6		5d				POPQ BP													
  step35_static.go:248	0x16fede7		c3				RET													
  step35_static.go:244	0x16fede8		4889d8				MOVQ BX, AX												
  step35_static.go:244	0x16fedeb		4889cb				MOVQ CX, BX												
  step35_static.go:244	0x16fedee		4881c4d8000000			ADDQ $0xd8, SP												
  step35_static.go:244	0x16fedf5		5d				POPQ BP													
  step35_static.go:244	0x16fedf6		c3				RET													
  step35_static.go:250	0x16fedf7		4883c610			ADDQ $0x10, SI												
  step35_static.go:250	0x16fedfb		48ffcf				DECQ DI													
  step35_static.go:250	0x16fedfe		6690				NOPW													
  step35_static.go:250	0x16fee00		4885ff				TESTQ DI, DI												
  step35_static.go:250	0x16fee03		0f8e92000000			JLE 0x16fee9b												
  step35_static.go:250	0x16fee09		4c8b4608			MOVQ 0x8(SI), R8											
  step35_static.go:251	0x16fee0d		4c39c1				CMPQ CX, R8												
  step35_static.go:251	0x16fee10		0f82a8000000			JB 0x16feebe												
  step35_static.go:250	0x16fee16		4c8b0e				MOVQ 0(SI), R9												
  step35_static.go:250	0x16fee19		0f1f8000000000			NOPL 0(AX)												
  step35_static.go:251	0x16fee20		4d39c1				CMPQ R9, R8												
  step35_static.go:251	0x16fee23		0f878a000000			JA 0x16feeb3												
  step35_static.go:251	0x16fee29		4d89ca				MOVQ R9, R10												
  step35_static.go:251	0x16fee2c		4929c9				SUBQ CX, R9												
  step35_static.go:251	0x16fee2f		49c1f93f			SARQ $0x3f, R9												
  step35_static.go:251	0x16fee33		4d21d1				ANDQ R10, R9												
  step35_static.go:251	0x16fee36		4c8b5a40			MOVQ 0x40(DX), R11											
  step35_static.go:251	0x16fee3a		4901c1				ADDQ AX, R9												
  step35_static.go:251	0x16fee3d		4d89c4				MOVQ R8, R12												
  step35_static.go:251	0x16fee40		4d29d0				SUBQ R10, R8												
  step35_static.go:251	0x16fee43		4d39e3				CMPQ R11, R12												
  step35_static.go:251	0x16fee46		7260				JB 0x16feea8												
  step35_static.go:251	0x16fee48		4c8b6230			MOVQ 0x30(DX), R12											
  step35_static.go:251	0x16fee4c		4d89d5				MOVQ R10, R13												
  step35_static.go:251	0x16fee4f		4d29da				SUBQ R11, R10												
  step35_static.go:251	0x16fee52		49c1fa3f			SARQ $0x3f, R10												
  step35_static.go:251	0x16fee56		4d21d5				ANDQ R10, R13												
  step35_static.go:251	0x16fee59		4b8d1c2c			LEAQ 0(R12)(R13*1), BX											
  step35_static.go:251	0x16fee5d		0f1f00				NOPL 0(AX)												
  step35_static.go:251	0x16fee60		4c39cb				CMPQ BX, R9												
  step35_static.go:251	0x16fee63		7492				JE 0x16fedf7												
  step35_static.go:250	0x16fee65		48897c2450			MOVQ DI, 0x50(SP)											
  step35_static.go:250	0x16fee6a		4889742460			MOVQ SI, 0x60(SP)											
  step35_static.go:251	0x16fee6f		4c89c8				MOVQ R9, AX												
  step35_static.go:251	0x16fee72		4c89c1				MOVQ R8, CX												
  step35_static.go:251	0x16fee75		e8a61d47ff			CALL local.runtime.memmove(SB)										
  step35_static.go:251	0x16fee7a		488b442458			MOVQ 0x58(SP), AX											
  step35_static.go:251	0x16fee7f		488b4c2448			MOVQ 0x48(SP), CX											
  step35_static.go:251	0x16fee84		488b9424e8000000		MOVQ 0xe8(SP), DX											
  step35_static.go:250	0x16fee8c		488b742460			MOVQ 0x60(SP), SI											
  step35_static.go:250	0x16fee91		488b7c2450			MOVQ 0x50(SP), DI											
  step35_static.go:251	0x16fee96		e95cffffff			JMP 0x16fedf7												
  step35_static.go:253	0x16fee9b		31c0				XORL AX, AX												
  step35_static.go:253	0x16fee9d		31db				XORL BX, BX												
  step35_static.go:253	0x16fee9f		4881c4d8000000			ADDQ $0xd8, SP												
  step35_static.go:253	0x16feea6		5d				POPQ BP													
  step35_static.go:253	0x16feea7		c3				RET													
  step35_static.go:251	0x16feea8		4c89e1				MOVQ R12, CX												
  step35_static.go:251	0x16feeab		4c89da				MOVQ R11, DX												
  step35_static.go:251	0x16feeae		e80d1447ff			CALL runtime.panicSliceAcap(SB)										
  step35_static.go:251	0x16feeb3		4c89c8				MOVQ R9, AX												
  step35_static.go:251	0x16feeb6		4c89c1				MOVQ R8, CX												
  step35_static.go:251	0x16feeb9		e8421447ff			CALL local.runtime.panicSliceB(SB)									
  step35_static.go:251	0x16feebe		4889ca				MOVQ CX, DX												
  step35_static.go:251	0x16feec1		4c89c1				MOVQ R8, CX												
  step35_static.go:251	0x16feec4		e8f71347ff			CALL runtime.panicSliceAcap(SB)										
  step35_static.go:251	0x16feec9		90				NOPL													
  step35_static.go:236	0x16feeca		4889442408			MOVQ AX, 0x8(SP)											
  step35_static.go:236	0x16feecf		48895c2410			MOVQ BX, 0x10(SP)											
  step35_static.go:236	0x16feed4		48894c2418			MOVQ CX, 0x18(SP)											
  step35_static.go:236	0x16feed9		48897c2420			MOVQ DI, 0x20(SP)											
  step35_static.go:236	0x16feede		4889742428			MOVQ SI, 0x28(SP)											
  step35_static.go:236	0x16feee3		4c89442430			MOVQ R8, 0x30(SP)											
  step35_static.go:236	0x16feee8		4c894c2438			MOVQ R9, 0x38(SP)											
  step35_static.go:236	0x16feeed		4c89542440			MOVQ R10, 0x40(SP)											
  step35_static.go:236	0x16feef2		4c895c2448			MOVQ R11, 0x48(SP)											
  step35_static.go:236	0x16feef7		e8c4f046ff			CALL local.runtime.morestack_noctxt.abi0(SB)								
  step35_static.go:236	0x16feefc		488b442408			MOVQ 0x8(SP), AX											
  step35_static.go:236	0x16fef01		488b5c2410			MOVQ 0x10(SP), BX											
  step35_static.go:236	0x16fef06		488b4c2418			MOVQ 0x18(SP), CX											
  step35_static.go:236	0x16fef0b		488b7c2420			MOVQ 0x20(SP), DI											
  step35_static.go:236	0x16fef10		488b742428			MOVQ 0x28(SP), SI											
  step35_static.go:236	0x16fef15		4c8b442430			MOVQ 0x30(SP), R8											
  step35_static.go:236	0x16fef1a		4c8b4c2438			MOVQ 0x38(SP), R9											
  step35_static.go:236	0x16fef1f		4c8b542440			MOVQ 0x40(SP), R10											
  step35_static.go:236	0x16fef24		4c8b5c2448			MOVQ 0x48(SP), R11											
  step35_static.go:236	0x16fef29		e972fcffff			JMP local.chainmaker.org/chainmaker/vm-wasmer/v2.(*staticMemoryPlan).restore(SB)			

TEXT local.chainmaker.org/chainmaker/vm-wasmer/v2.(*staticMemoryPlan).restore(SB) /home/frankie/mygitprojects/.worktrees/cvw-step38/experiments/instance-lifecycle/step-38-copy-range-cost/source/A/vm/step35_static.go
  step35_static.go:236	0x16feba0		4c8d6424a0			LEAQ -0x60(SP), R12											
  step35_static.go:236	0x16feba5		4d3b6610			CMPQ R12, 0x10(R14)											
  step35_static.go:236	0x16feba9		0f861b030000			JBE 0x16feeca												
  step35_static.go:236	0x16febaf		55				PUSHQ BP												
  step35_static.go:236	0x16febb0		4889e5				MOVQ SP, BP												
  step35_static.go:236	0x16febb3		4881ecd8000000			SUBQ $0xd8, SP												
  step35_static.go:236	0x16febba		4c89942420010000		MOVQ R10, 0x120(SP)											
  step35_static.go:237	0x16febc2		48898424e8000000		MOVQ AX, 0xe8(SP)											
  step35_static.go:237	0x16febca		48898c24f8000000		MOVQ CX, 0xf8(SP)											
  step35_static.go:237	0x16febd2		48395868			CMPQ 0x68(AX), BX											
  step35_static.go:237	0x16febd6		7407				JE 0x16febdf												
  step35_static.go:237	0x16febd8		ba01000000			MOVL $0x1, DX												
  step35_static.go:237	0x16febdd		eb64				JMP 0x16fec43												
  step35_static.go:237	0x16febdf		488b5028			MOVQ 0x28(AX), DX											
  step35_static.go:237	0x16febe3		4939d3				CMPQ R11, DX												
  step35_static.go:237	0x16febe6		7407				JE 0x16febef												
  step35_static.go:237	0x16febe8		ba01000000			MOVL $0x1, DX												
  step35_static.go:237	0x16febed		eb54				JMP 0x16fec43												
  step35_static.go:237	0x16febef		4c898c2418010000		MOVQ R9, 0x118(SP)											
  step35_static.go:237	0x16febf7		4c899c2428010000		MOVQ R11, 0x128(SP)											
  step35_static.go:237	0x16febff		4c89942420010000		MOVQ R10, 0x120(SP)											
  step35_static.go:237	0x16fec07		488b4020			MOVQ 0x20(AX), AX											
  step35_static.go:237	0x16fec0b		4c89d3				MOVQ R10, BX												
  step35_static.go:237	0x16fec0e		4889d1				MOVQ DX, CX												
  step35_static.go:237	0x16fec11		e82a423eff			CALL local.runtime.memequal(SB)										
  step35_static.go:237	0x16fec16		83f001				XORL $0x1, AX												
  step35_static.go:242	0x16fec19		488b8c24f8000000		MOVQ 0xf8(SP), CX											
  step35_static.go:237	0x16fec21		4c8b8c2418010000		MOVQ 0x118(SP), R9											
  step35_static.go:237	0x16fec29		4c8b942420010000		MOVQ 0x120(SP), R10											
  step35_static.go:237	0x16fec31		4c8b9c2428010000		MOVQ 0x128(SP), R11											
  step35_static.go:237	0x16fec39		89c2				MOVL AX, DX												
  step35_static.go:237	0x16fec3b		488b8424e8000000		MOVQ 0xe8(SP), AX											
  step35_static.go:237	0x16fec43		84d2				TESTL DL, DL												
  step35_static.go:237	0x16fec45		0f850f010000			JNE 0x16fed5a												
  step35_static.go:237	0x16fec4b		488d7c2468			LEAQ 0x68(SP), DI											
  step35_static.go:237	0x16fec50		488d7ff0			LEAQ -0x10(DI), DI											
  step35_static.go:237	0x16fec54		660f1f840000000000		NOPW 0(AX)(AX*1)											
  step35_static.go:237	0x16fec5d		0f1f00				NOPL 0(AX)												
  step35_static.go:237	0x16fec60		48896c24f0			MOVQ BP, -0x10(SP)											
  step35_static.go:237	0x16fec65		488d6c24f0			LEAQ -0x10(SP), BP											
  step35_static.go:237	0x16fec6a		e8d71847ff			CALL 0xb70546												
  step35_static.go:237	0x16fec6f		488b6d00			MOVQ 0(BP), BP												
  step35_static.go:237	0x16fec73		498b11				MOVQ 0(R9), DX												
  step35_static.go:237	0x16fec76		498b7108			MOVQ 0x8(R9), SI											
  step35_static.go:237	0x16fec7a		4889742470			MOVQ SI, 0x70(SP)											
  step35_static.go:237	0x16fec7f		4889542468			MOVQ DX, 0x68(SP)											
  step35_static.go:237	0x16fec84		48c784248000000001000000	MOVQ $0x1, 0x80(SP)											
  step35_static.go:237	0x16fec90		488d1561b39d00			LEAQ testing..stmp_7(SB), DX										
  step35_static.go:237	0x16fec97		4889542478			MOVQ DX, 0x78(SP)											
  step35_static.go:237	0x16fec9c		498b7110			MOVQ 0x10(R9), SI											
  step35_static.go:237	0x16feca0		4d8b4118			MOVQ 0x18(R9), R8											
  step35_static.go:237	0x16feca4		4c89842490000000		MOVQ R8, 0x90(SP)											
  step35_static.go:237	0x16fecac		4889b42488000000		MOVQ SI, 0x88(SP)											
  step35_static.go:237	0x16fecb4		48c78424a000000001000000	MOVQ $0x1, 0xa0(SP)											
  step35_static.go:237	0x16fecc0		4889942498000000		MOVQ DX, 0x98(SP)											
  step35_static.go:237	0x16fecc8		488b7010			MOVQ 0x10(AX), SI											
  step35_static.go:237	0x16feccc		4c8b4018			MOVQ 0x18(AX), R8											
  step35_static.go:237	0x16fecd0		4c898424b0000000		MOVQ R8, 0xb0(SP)											
  step35_static.go:237	0x16fecd8		4889b424a8000000		MOVQ SI, 0xa8(SP)											
  step35_static.go:237	0x16fece0		48c78424c000000001000000	MOVQ $0x1, 0xc0(SP)											
  step35_static.go:237	0x16fecec		48899424b8000000		MOVQ DX, 0xb8(SP)											
  step35_static.go:237	0x16fecf4		4c899c24d0000000		MOVQ R11, 0xd0(SP)											
  step35_static.go:237	0x16fecfc		4c899424c8000000		MOVQ R10, 0xc8(SP)											
  step35_static.go:237	0x16fed04		488d442428			LEAQ 0x28(SP), AX											
  step35_static.go:237	0x16fed09		488d5c2468			LEAQ 0x68(SP), BX											
  step35_static.go:237	0x16fed0e		b907000000			MOVL $0x7, CX												
  step35_static.go:237	0x16fed13		4889cf				MOVQ CX, DI												
  step35_static.go:237	0x16fed16		e825cd44ff			CALL local.runtime.concatbytes(SB)									
  step35_static.go:237	0x16fed1b		0f1f440000			NOPL 0(AX)(AX*1)											
  step35_static.go:237	0x16fed20		e8fbd8ffff			CALL chainmaker.org/chainmaker/vm-wasmer/v2.staticSHA(SB)						
  step35_static.go:237	0x16fed25		488b9424e8000000		MOVQ 0xe8(SP), DX											
  step35_static.go:237	0x16fed2d		488b4a08			MOVQ 0x8(DX), CX											
  step35_static.go:237	0x16fed31		4839cb				CMPQ BX, CX												
  step35_static.go:237	0x16fed34		7407				JE 0x16fed3d												
  step35_static.go:237	0x16fed36		b801000000			MOVL $0x1, AX												
  step35_static.go:237	0x16fed3b		eb19				JMP 0x16fed56												
  step35_static.go:237	0x16fed3d		488b12				MOVQ 0(DX), DX												
  step35_static.go:237	0x16fed40		4889c3				MOVQ AX, BX												
  step35_static.go:237	0x16fed43		4889d0				MOVQ DX, AX												
  step35_static.go:237	0x16fed46		e8f5403eff			CALL local.runtime.memequal(SB)										
  step35_static.go:237	0x16fed4b		83f001				XORL $0x1, AX												
  step35_static.go:247	0x16fed4e		488b9424e8000000		MOVQ 0xe8(SP), DX											
  step35_static.go:237	0x16fed56		84c0				TESTL AL, AL												
  step35_static.go:237	0x16fed58		7421				JE 0x16fed7b												
  step35_static.go:238	0x16fed5a		488d05c77e7200			LEAQ 0x727ec7(IP), AX											
  step35_static.go:238	0x16fed61		bb26000000			MOVL $_ZN3std11collections4hash3map11RandomState3new4KEYS7__getit5__KEY17hc510b8383306a22dE+30(SB), BX	
  step35_static.go:238	0x16fed66		31c9				XORL CX, CX												
  step35_static.go:238	0x16fed68		31ff				XORL DI, DI												
  step35_static.go:238	0x16fed6a		4889fe				MOVQ DI, SI												
  step35_static.go:238	0x16fed6d		e82e2851ff			CALL fmt.Errorf(SB)											
  step35_static.go:238	0x16fed72		4881c4d8000000			ADDQ $0xd8, SP												
  step35_static.go:238	0x16fed79		5d				POPQ BP													
  step35_static.go:238	0x16fed7a		c3				RET													
  step35_static.go:242	0x16fed7b		488b9424f8000000		MOVQ 0xf8(SP), DX											
  step35_static.go:242	0x16fed83		488b4208			MOVQ 0x8(DX), AX											
  step35_static.go:242	0x16fed87		488d1da5fb6e00			LEAQ 0x6efba5(IP), BX											
  step35_static.go:242	0x16fed8e		b906000000			MOVL $0x6, CX												
  step35_static.go:242	0x16fed93		e8e88696ff			CALL local.chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go.(*Exports).GetMemory(SB)			
  step35_static.go:243	0x16fed98		4885db				TESTQ BX, BX												
  step35_static.go:243	0x16fed9b		754b				JNE 0x16fede8												
  step35_static.go:243	0x16fed9d		0f1f00				NOPL 0(AX)												
  step35_static.go:246	0x16feda0		e87bda96ff			CALL chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go.(*Memory).Data(SB)				
  step35_static.go:247	0x16feda5		488b9424e8000000		MOVQ 0xe8(SP), DX											
  step35_static.go:247	0x16fedad		48395a38			CMPQ 0x38(DX), BX											
  step35_static.go:247	0x16fedb1		7514				JNE 0x16fedc7												
  step35_static.go:246	0x16fedb3		4889442458			MOVQ AX, 0x58(SP)											
  step35_static.go:246	0x16fedb8		48894c2448			MOVQ CX, 0x48(SP)											
  step35_static.go:250	0x16fedbd		488b7250			MOVQ 0x50(DX), SI											
  step35_static.go:250	0x16fedc1		488b7a58			MOVQ 0x58(DX), DI											
  step35_static.go:250	0x16fedc5		eb39				JMP 0x16fee00												
  step35_static.go:248	0x16fedc7		488d05807e7200			LEAQ 0x727e80(IP), AX											
  step35_static.go:248	0x16fedce		bb26000000			MOVL $_ZN3std11collections4hash3map11RandomState3new4KEYS7__getit5__KEY17hc510b8383306a22dE+30(SB), BX	
  step35_static.go:248	0x16fedd3		31c9				XORL CX, CX												
  step35_static.go:248	0x16fedd5		31ff				XORL DI, DI												
  step35_static.go:248	0x16fedd7		4889fe				MOVQ DI, SI												
  step35_static.go:248	0x16fedda		e8c12751ff			CALL fmt.Errorf(SB)											
  step35_static.go:248	0x16feddf		4881c4d8000000			ADDQ $0xd8, SP												
  step35_static.go:248	0x16fede6		5d				POPQ BP													
  step35_static.go:248	0x16fede7		c3				RET													
  step35_static.go:244	0x16fede8		4889d8				MOVQ BX, AX												
  step35_static.go:244	0x16fedeb		4889cb				MOVQ CX, BX												
  step35_static.go:244	0x16fedee		4881c4d8000000			ADDQ $0xd8, SP												
  step35_static.go:244	0x16fedf5		5d				POPQ BP													
  step35_static.go:244	0x16fedf6		c3				RET													
  step35_static.go:250	0x16fedf7		4883c610			ADDQ $0x10, SI												
  step35_static.go:250	0x16fedfb		48ffcf				DECQ DI													
  step35_static.go:250	0x16fedfe		6690				NOPW													
  step35_static.go:250	0x16fee00		4885ff				TESTQ DI, DI												
  step35_static.go:250	0x16fee03		0f8e92000000			JLE 0x16fee9b												
  step35_static.go:250	0x16fee09		4c8b4608			MOVQ 0x8(SI), R8											
  step35_static.go:251	0x16fee0d		4c39c1				CMPQ CX, R8												
  step35_static.go:251	0x16fee10		0f82a8000000			JB 0x16feebe												
  step35_static.go:250	0x16fee16		4c8b0e				MOVQ 0(SI), R9												
  step35_static.go:250	0x16fee19		0f1f8000000000			NOPL 0(AX)												
  step35_static.go:251	0x16fee20		4d39c1				CMPQ R9, R8												
  step35_static.go:251	0x16fee23		0f878a000000			JA 0x16feeb3												
  step35_static.go:251	0x16fee29		4d89ca				MOVQ R9, R10												
  step35_static.go:251	0x16fee2c		4929c9				SUBQ CX, R9												
  step35_static.go:251	0x16fee2f		49c1f93f			SARQ $0x3f, R9												
  step35_static.go:251	0x16fee33		4d21d1				ANDQ R10, R9												
  step35_static.go:251	0x16fee36		4c8b5a40			MOVQ 0x40(DX), R11											
  step35_static.go:251	0x16fee3a		4901c1				ADDQ AX, R9												
  step35_static.go:251	0x16fee3d		4d89c4				MOVQ R8, R12												
  step35_static.go:251	0x16fee40		4d29d0				SUBQ R10, R8												
  step35_static.go:251	0x16fee43		4d39e3				CMPQ R11, R12												
  step35_static.go:251	0x16fee46		7260				JB 0x16feea8												
  step35_static.go:251	0x16fee48		4c8b6230			MOVQ 0x30(DX), R12											
  step35_static.go:251	0x16fee4c		4d89d5				MOVQ R10, R13												
  step35_static.go:251	0x16fee4f		4d29da				SUBQ R11, R10												
  step35_static.go:251	0x16fee52		49c1fa3f			SARQ $0x3f, R10												
  step35_static.go:251	0x16fee56		4d21d5				ANDQ R10, R13												
  step35_static.go:251	0x16fee59		4b8d1c2c			LEAQ 0(R12)(R13*1), BX											
  step35_static.go:251	0x16fee5d		0f1f00				NOPL 0(AX)												
  step35_static.go:251	0x16fee60		4c39cb				CMPQ BX, R9												
  step35_static.go:251	0x16fee63		7492				JE 0x16fedf7												
  step35_static.go:250	0x16fee65		48897c2450			MOVQ DI, 0x50(SP)											
  step35_static.go:250	0x16fee6a		4889742460			MOVQ SI, 0x60(SP)											
  step35_static.go:251	0x16fee6f		4c89c8				MOVQ R9, AX												
  step35_static.go:251	0x16fee72		4c89c1				MOVQ R8, CX												
  step35_static.go:251	0x16fee75		e8a61d47ff			CALL local.runtime.memmove(SB)										
  step35_static.go:251	0x16fee7a		488b442458			MOVQ 0x58(SP), AX											
  step35_static.go:251	0x16fee7f		488b4c2448			MOVQ 0x48(SP), CX											
  step35_static.go:251	0x16fee84		488b9424e8000000		MOVQ 0xe8(SP), DX											
  step35_static.go:250	0x16fee8c		488b742460			MOVQ 0x60(SP), SI											
  step35_static.go:250	0x16fee91		488b7c2450			MOVQ 0x50(SP), DI											
  step35_static.go:251	0x16fee96		e95cffffff			JMP 0x16fedf7												
  step35_static.go:253	0x16fee9b		31c0				XORL AX, AX												
  step35_static.go:253	0x16fee9d		31db				XORL BX, BX												
  step35_static.go:253	0x16fee9f		4881c4d8000000			ADDQ $0xd8, SP												
  step35_static.go:253	0x16feea6		5d				POPQ BP													
  step35_static.go:253	0x16feea7		c3				RET													
  step35_static.go:251	0x16feea8		4c89e1				MOVQ R12, CX												
  step35_static.go:251	0x16feeab		4c89da				MOVQ R11, DX												
  step35_static.go:251	0x16feeae		e80d1447ff			CALL runtime.panicSliceAcap(SB)										
  step35_static.go:251	0x16feeb3		4c89c8				MOVQ R9, AX												
  step35_static.go:251	0x16feeb6		4c89c1				MOVQ R8, CX												
  step35_static.go:251	0x16feeb9		e8421447ff			CALL local.runtime.panicSliceB(SB)									
  step35_static.go:251	0x16feebe		4889ca				MOVQ CX, DX												
  step35_static.go:251	0x16feec1		4c89c1				MOVQ R8, CX												
  step35_static.go:251	0x16feec4		e8f71347ff			CALL runtime.panicSliceAcap(SB)										
  step35_static.go:251	0x16feec9		90				NOPL													
  step35_static.go:236	0x16feeca		4889442408			MOVQ AX, 0x8(SP)											
  step35_static.go:236	0x16feecf		48895c2410			MOVQ BX, 0x10(SP)											
  step35_static.go:236	0x16feed4		48894c2418			MOVQ CX, 0x18(SP)											
  step35_static.go:236	0x16feed9		48897c2420			MOVQ DI, 0x20(SP)											
  step35_static.go:236	0x16feede		4889742428			MOVQ SI, 0x28(SP)											
  step35_static.go:236	0x16feee3		4c89442430			MOVQ R8, 0x30(SP)											
  step35_static.go:236	0x16feee8		4c894c2438			MOVQ R9, 0x38(SP)											
  step35_static.go:236	0x16feeed		4c89542440			MOVQ R10, 0x40(SP)											
  step35_static.go:236	0x16feef2		4c895c2448			MOVQ R11, 0x48(SP)											
  step35_static.go:236	0x16feef7		e8c4f046ff			CALL local.runtime.morestack_noctxt.abi0(SB)								
  step35_static.go:236	0x16feefc		488b442408			MOVQ 0x8(SP), AX											
  step35_static.go:236	0x16fef01		488b5c2410			MOVQ 0x10(SP), BX											
  step35_static.go:236	0x16fef06		488b4c2418			MOVQ 0x18(SP), CX											
  step35_static.go:236	0x16fef0b		488b7c2420			MOVQ 0x20(SP), DI											
  step35_static.go:236	0x16fef10		488b742428			MOVQ 0x28(SP), SI											
  step35_static.go:236	0x16fef15		4c8b442430			MOVQ 0x30(SP), R8											
  step35_static.go:236	0x16fef1a		4c8b4c2438			MOVQ 0x38(SP), R9											
  step35_static.go:236	0x16fef1f		4c8b542440			MOVQ 0x40(SP), R10											
  step35_static.go:236	0x16fef24		4c8b5c2448			MOVQ 0x48(SP), R11											
  step35_static.go:236	0x16fef29		e972fcffff			JMP local.chainmaker.org/chainmaker/vm-wasmer/v2.(*staticMemoryPlan).restore(SB)			
