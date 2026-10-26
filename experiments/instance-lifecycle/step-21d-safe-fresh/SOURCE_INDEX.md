# 关键源码行号

所有行号以已提交source/vm为准。完整差异见source.patch和audit/fixture-adaptation.patch。

| 文件 | 函数/类型 | 行号 |
|---|---|---:|

| [source/vm/step21d_runtime_test.go](source/vm/step21d_runtime_test.go) | `func newDManager(policy string) *dManager` | 37 |

| [source/vm/step21d_runtime_test.go](source/vm/step21d_runtime_test.go) | `func dEvent(event string, fields map[string]interface` | 46 |

| [source/vm/step21d_runtime_test.go](source/vm/step21d_runtime_test.go) | `func (m *dManager) NewRuntimeInstance(_ protocol.TxSimContext, chain, method, path string, c *common.Contract, code []byte, _ protocol.Logger) (protocol.RuntimeInstance, error)` | 74 |

| [source/vm/step21d_runtime_test.go](source/vm/step21d_runtime_test.go) | `func (m *dManager) makeBundle(c *common.Contract, code []byte) (b *dBundle, err error)` | 84 |

| [source/vm/step21d_runtime_test.go](source/vm/step21d_runtime_test.go) | `func (m *dManager) closeBundle(b *dBundle) (err error)` | 153 |

| [source/vm/step21d_runtime_test.go](source/vm/step21d_runtime_test.go) | `func (m *dManager) Close() error` | 180 |

| [source/vm/step21d_runtime_test.go](source/vm/step21d_runtime_test.go) | `func (r *dRuntime) Invoke(c *common.Contract, method string, code []byte, params map[string][]byte, ctx protocol.TxSimContext, gasUsed uint64) (result *common.ContractResult, order protocol.ExecOrderTxType)` | 204 |

| [source/vm/step21d_compile.go](source/vm/step21d_compile.go) | `func dCompile(contractId *commonPb.Contract, byteCode []byte, log *logger.CMLogger) (*wasmergo.Store, *wasmergo.Module, error)` | 11 |

| [source/vm/step21d_checks_test.go](source/vm/step21d_checks_test.go) | `func dN(t *testing.T) int` | 14 |

| [source/vm/step21d_checks_test.go](source/vm/step21d_checks_test.go) | `func dOwner(t *testing.T) func()` | 21 |

| [source/vm/step21d_checks_test.go](source/vm/step21d_checks_test.go) | `func TestStep21DOwnerFailure(t *testing.T)` | 41 |

| [source/vm/step21d_checks_test.go](source/vm/step21d_checks_test.go) | `func TestStep21DCompute(t *testing.T)` | 83 |

| [source/vm/step21d_checks_test.go](source/vm/step21d_checks_test.go) | `func TestStep21DExchange(t *testing.T)` | 111 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (s *s21cStore) GetContractByName(name string) (*common.Contract, error)` | 64 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (s *s21cStore) GetContractBytecode(name string) ([]byte, error)` | 77 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (s *s21cStore) GetLastChainConfig() (*config.ChainConfig, error)` | 84 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (s *s21cSnapshot) GetBlockchainStore() protocol.BlockchainStore` | 92 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (s *s21cSnapshot) GetLastChainConfig() *config.ChainConfig` | 93 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (s *s21cSnapshot) GetBlockHeight() uint64` | 94 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (s *s21cSnapshot) GetKey(_ int, name string, key []byte) ([]byte, error)` | 95 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (s *s21cSnapshot) hash() string` | 98 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (s *s21cSnapshot) commit(rw *common.TxRWSet)` | 103 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (m *s21cMember) GetMemberId() string` | 124 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (m *s21cMember) GetOrgId() string` | 125 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (m *s21cMember) GetRole() protocol.Role` | 126 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (m *s21cMember) GetUid() string` | 127 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (m *s21cMember) GetPk() cmcrypto.PublicKey` | 128 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (m *s21cMember) GetMember() (*ac.Member, error)` | 129 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (m *s21cMember) Verify(_ string, _ []byte, _ []byte) error` | 130 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (a *s21cAC) GetHashAlg() string` | 139 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (a *s21cAC) NewMember(m *ac.Member) (protocol.Member, error)` | 140 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (a *s21cAC) VerifyTxPrincipal(_ *common.Transaction, _ string, _ uint32) (bool, error)` | 146 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func s21cEmit(row interface` | 161 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func s21cPrepare(t *testing.T, manifestPath, output string) *s21cFixture` | 169 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (f *s21cFixture) run(label, contract, method, txID string, input map[string]string) *s21cReceipt` | 252 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (f *s21cFixture) state(contract, key, field string) string` | 299 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func (f *s21cFixture) close()` | 302 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func s21cPreparedScenario(t *testing.T, manifest, output string)` | 309 |

| [source/vm/step21d_fixture_test.go](source/vm/step21d_fixture_test.go) | `func TestStep21CRealCrossContractPrepared(t *testing.T)` | 409 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `type managedEntry struct` | 10 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `type ManagedScope struct` | 14 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `func ManagedBeginOwner()` | 25 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `func ManagedAssert()` | 31 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `func ManagedOpen(label string) *ManagedScope` | 36 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `func (s *ManagedScope) Activate() func()` | 42 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `func managedSetFinalizer(obj, fn interface` | 51 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `func (s *ManagedScope) Close() (err error)` | 73 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `func ManagedCount() int` | 109 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `func ManagedEndOwner()` | 110 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `func (s *ManagedScope) Suspend()` | 118 |

| [source/vm/wasmer-go/managed.go](source/vm/wasmer-go/managed.go) | `func managedEnterFunction(f *Function) func()` | 130 |

| [source/vm/wasmer-go/import_object.go](source/vm/wasmer-go/import_object.go) | `func NewImportObject() *ImportObject` | 20 |

| [source/vm/wasmer-go/import_object.go](source/vm/wasmer-go/import_object.go) | `func (self *ImportObject) intoInner(module *Module) (*C.wasm_extern_vec_t, error)` | 26 |

| [source/vm/wasmer-go/import_object.go](source/vm/wasmer-go/import_object.go) | `func (self *ImportObject) ContainsNamespace(name string) bool` | 61 |

| [source/vm/wasmer-go/import_object.go](source/vm/wasmer-go/import_object.go) | `func (self *ImportObject) Register(namespaceName string, namespace map[string]IntoExtern)` | 92 |

| [source/vm/wasmer-go/import_object.go](source/vm/wasmer-go/import_object.go) | `func (self *ImportObject) Close()` | 105 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func newFunction(pointer *C.wasm_func_t, environment *functionEnvironment, ownedBy interface` | 44 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func NewFunction(store *Store, ty *FunctionType, function func([]Value) ([]Value, error)) *Function` | 89 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func function_trampoline(env unsafe.Pointer, args *C.wasm_val_vec_t, res *C.wasm_val_vec_t) *C.wasm_trap_t` | 111 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func NewFunctionWithEnvironment(store *Store, ty *FunctionType, userEnvironment interface` | 158 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func function_with_environment_trampoline(env unsafe.Pointer, args *C.wasm_val_vec_t, res *C.wasm_val_vec_t) *C.wasm_trap_t` | 181 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *Function) inner() *C.wasm_func_t` | 202 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *Function) ownedBy() interface` | 206 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *Function) IntoExtern() *Extern` | 218 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *Function) Type() *FunctionType` | 228 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *Function) ParameterArity() uint` | 244 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *Function) ResultArity() uint` | 252 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *Function) Call(parameters ...interface` | 260 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *Function) Native() NativeFunction` | 269 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *Function) Close()` | 349 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func function_environment_finalizer(_ unsafe.Pointer)` | 362 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *hostFunctions) load(index uint32) (*hostFunction, error)` | 376 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *hostFunctions) store(hostFunction *hostFunction) uint32` | 388 |

| [source/vm/wasmer-go/function.go](source/vm/wasmer-go/function.go) | `func (self *hostFunctions) remove(index uint32)` | 401 |

| [source/vm/wasmer-go/functiontype.go](source/vm/wasmer-go/functiontype.go) | `func newFunctionType(pointer *C.wasm_functype_t, ownedBy interface` | 18 |

| [source/vm/wasmer-go/functiontype.go](source/vm/wasmer-go/functiontype.go) | `func NewFunctionType(params []*ValueType, results []*ValueType) *FunctionType` | 36 |

| [source/vm/wasmer-go/functiontype.go](source/vm/wasmer-go/functiontype.go) | `func (self *FunctionType) inner() *C.wasm_functype_t` | 47 |

| [source/vm/wasmer-go/functiontype.go](source/vm/wasmer-go/functiontype.go) | `func (self *FunctionType) ownedBy() interface` | 51 |

| [source/vm/wasmer-go/functiontype.go](source/vm/wasmer-go/functiontype.go) | `func (self *FunctionType) Params() []*ValueType` | 66 |

| [source/vm/wasmer-go/functiontype.go](source/vm/wasmer-go/functiontype.go) | `func (self *FunctionType) Results() []*ValueType` | 77 |

| [source/vm/wasmer-go/functiontype.go](source/vm/wasmer-go/functiontype.go) | `func (self *FunctionType) IntoExternType() *ExternType` | 86 |

| [source/vm/wasmer-go/functiontype.go](source/vm/wasmer-go/functiontype.go) | `func (self *FunctionType) Close()` | 93 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self WasiVersion) String() string` | 87 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func GetWasiVersion(module *Module) WasiVersion` | 105 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func NewWasiStateBuilder(programName string) *WasiStateBuilder` | 118 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiStateBuilder) Argument(argument string) *WasiStateBuilder` | 134 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiStateBuilder) Environment(key string, value string) *WasiStateBuilder` | 147 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiStateBuilder) PreopenDirectory(preopenDirectory string) *WasiStateBuilder` | 168 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiStateBuilder) MapDirectory(alias string, directory string) *WasiStateBuilder` | 184 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiStateBuilder) InheritStdin() *WasiStateBuilder` | 198 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiStateBuilder) CaptureStdout() *WasiStateBuilder` | 211 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiStateBuilder) InheritStdout() *WasiStateBuilder` | 219 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiStateBuilder) CaptureStderr() *WasiStateBuilder` | 226 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiStateBuilder) InheritStderr() *WasiStateBuilder` | 234 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiStateBuilder) Finalize(store *C.wasm_store_t) (*WasiEnvironment, error)` | 252 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiStateBuilder) inner() *C.wasi_config_t` | 256 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func newWasiEnvironment(stateBuilder *WasiStateBuilder, store *C.wasm_store_t) (*WasiEnvironment, error)` | 268 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiEnvironment) inner() *C.wasi_env_t` | 291 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiEnvironment) Initialize(store *Store, instance *Instance) error` | 295 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func buildByteSliceFromCBuffer(buffer *C.char, length int) []byte` | 307 |

| [source/vm/wasmer-go/wasi.go](source/vm/wasmer-go/wasi.go) | `func (self *WasiEnvironment) GenerateImportObject(store *Store, module *Module) (*ImportObject, error)` | 367 |
