module chainmaker.org/chainmaker/store/v2

go 1.16

require (
	chainmaker.org/chainmaker/common/v2 v2.4.0
	chainmaker.org/chainmaker/lws v1.2.1
	chainmaker.org/chainmaker/pb-go/v2 v2.4.0
	chainmaker.org/chainmaker/protocol/v2 v2.4.0
	chainmaker.org/chainmaker/store-badgerdb/v2 v2.4.0
	chainmaker.org/chainmaker/store-leveldb/v2 v2.4.0
	chainmaker.org/chainmaker/store-sqldb/v2 v2.4.0
	chainmaker.org/chainmaker/store-tikv/v2 v2.4.0
	chainmaker.org/chainmaker/utils/v2 v2.4.0
	github.com/RedisBloom/redisbloom-go v1.0.0
	github.com/allegro/bigcache/v3 v3.0.2
	github.com/bits-and-blooms/bloom/v3 v3.6.0
	github.com/fsnotify/fsnotify v1.6.0 // indirect
	github.com/gogo/protobuf v1.3.2
	github.com/golang/groupcache v0.0.0-20200121045136-8c9f03a8e57e
	github.com/golang/mock v1.6.0
	github.com/mitchellh/mapstructure v1.5.0
	github.com/panjf2000/ants/v2 v2.4.8
	github.com/pkg/errors v0.9.1
	github.com/spaolacci/murmur3 v1.1.0
	github.com/stretchr/testify v1.8.2
	github.com/test-go/testify v1.1.4
	github.com/tidwall/tinylru v1.1.0
	golang.org/x/sync v0.0.0-20210220032951-036812b2e83c
	golang.org/x/sys v0.0.0-20220908164124-27713097b956
)

replace (
	github.com/RedisBloom/redisbloom-go => chainmaker.org/third_party/redisbloom-go v1.0.0
	github.com/bits-and-blooms/bitset => ./third_party/forked/bitset
	github.com/bits-and-blooms/bloom/v3 => ./third_party/forked/bloom
	google.golang.org/grpc => google.golang.org/grpc v1.26.0
)
