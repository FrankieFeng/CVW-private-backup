package indexer

// ReadOptions holds the optional parameters for 'block file read operation'.
type ReadOptions struct {
	// read just from lastest file
	FromLatestFile bool
}

// ReadOption is used to set the optional parameters.
type ReadOption func(*ReadOptions)

// WithFromLatestFile read just from lastest file.
func WithFromLatestFile() ReadOption {
	return func(opt *ReadOptions) {
		opt.FromLatestFile = true
	}
}
