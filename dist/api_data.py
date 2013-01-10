# This file is a python script that describes the WiredTiger API.

class Error:
	def __init__(self, name, desc, long_desc=None, **flags):
		self.name = name
		self.desc = desc
		self.long_desc = long_desc
		self.flags = flags

errors = [
	Error('WT_DEADLOCK', 'conflict between concurrent operations', '''
		This error is generated when an operation cannot be completed
		due to a conflict with concurrent operations.  The operation
		may be retried; if a transaction is in progress, it should be
		rolled back and the operation retried in a new transaction.'''),
	Error('WT_DUPLICATE_KEY', 'attempt to insert an existing key', '''
		This error is generated when the application attempts to insert
		a record with the same key as an existing record without the
		'overwrite' configuration to WT_SESSION::open_cursor.'''),
	Error('WT_ERROR', 'non-specific WiredTiger error', '''
		This error is returned when an error is not covered by a
		specific error return.'''),
	Error('WT_NOTFOUND', 'cursor item not found', '''
		This error indicates a cursor operation did not find a
		record to return.  This includes search and other
		operations where no record matched the cursor's search
		key such as WT_CURSOR::update or WT_CURSOR::remove.'''),
	Error('WT_PANIC', 'WiredTiger library panic', '''
		This error indicates an underlying problem that requires the
		application exit and restart.'''),
	Error('WT_RESTART', 'restart the operation (internal)', undoc=True),
]

class Method:
	def __init__(self, config, **flags):
		self.config = config
		self.flags = flags

class Config:
	def __init__(self, name, default, desc, subconfig=None, **flags):
		self.name = name
		self.default = default
		self.desc = desc
		self.subconfig = subconfig
		self.flags = flags

	def __cmp__(self, other):
		return cmp(self.name, other.name)

# All schema objects can have column names (optional for simple tables).
column_meta = [
	Config('columns', '', r'''
		list of the column names.  Comma-separated list of the form
		<code>(column[,...])</code>.  For tables, the number of entries
		must match the total number of values in \c key_format and \c
		value_format.  For colgroups and indices, all column names must
		appear in the list of columns for the table''',
		type='list'),
]

source_meta = [
	Config('source', '', r'''
		override the default data source URI derived from the object
		name'''),
	Config('type', 'file', r'''
		set the data source type.  This setting overrides the URI
		prefix for the data source, if no \c source configuration
		setting is provided''',
		choices=['file', 'lsm']),
]

format_meta = column_meta + [
	Config('key_format', 'u', r'''
		the format of the data packed into key items.  See @ref
		schema_format_types for details.  By default, the key_format is
		\c 'u' and applications use WT_ITEM structures to manipulate
		raw byte arrays. By default, records are stored in row-store
		files: keys of type \c 'r' are record numbers and records
		referenced by record number are stored in column-store files''',
		type='format'),
	Config('value_format', 'u', r'''
		the format of the data packed into value items.  See @ref
		schema_format_types for details.  By default, the value_format
		is \c 'u' and applications use a WT_ITEM structure to
		manipulate raw byte arrays. Value items of type 't' are
		bitfields, and when configured with record number type keys,
		will be stored using a fixed-length store''',
		type='format'),
]

lsm_config = [
	Config('lsm_bloom', 'true', r'''
		create bloom filters on LSM tree chunks as they are merged''',
		type='boolean'),
	Config('lsm_bloom_config', '', r'''
		config string used when creating Bloom filter files, passed to
		WT_SESSION::create'''),
	Config('lsm_bloom_bit_count', '8', r'''
		the number of bits used per item for LSM bloom filters''',
		min='2', max='1000'),
	Config('lsm_bloom_hash_count', '4', r'''
		the number of hash values per item used for LSM bloom
		filters''',
		min='2', max='100'),
	Config('lsm_bloom_newest', 'false', r'''
		create a bloom filter on an LSM tree chunk before it's first merge.
		Only supported if bloom filters are enabled''',
		type='boolean'),
	Config('lsm_bloom_oldest', 'false', r'''
		create a bloom filter on the oldest LSM tree chunk. Only supported if
		bloom filters are enabled''',
		type='boolean'),
	Config('lsm_chunk_size', '2MB', r'''
		the maximum size of the in-memory chunk of an LSM tree''',
		min='512K', max='500MB'),
	Config('lsm_merge_max', '15', r'''
		the maximum number of chunks to include in a merge operation''',
		min='2', max='100'),
	Config('lsm_merge_threads', '1', r'''
		the number of thread to perform merge operations''',
		min='1', max='10'), # !!! max must match WT_LSM_MAX_WORKERS
]

# Per-file configuration
file_config = format_meta + lsm_config + [
	Config('allocation_size', '512B', r'''
		the file unit allocation size, in bytes, must a power-of-two;
		smaller values decrease the file space required by overflow
		items, and the default value of 512B is a good choice absent
		requirements from the operating system or storage device''',
		min='512B', max='128MB'),
	Config('block_compressor', '', r'''
		configure a compressor for file blocks.  Permitted values are
		empty (off) or \c "bzip2", \c "snappy" or custom compression
		engine \c "name" created with WT_CONNECTION::add_compressor.
		See @ref compression for more information'''),
	Config('cache_resident', 'false', r'''
		do not ever evict the object's pages; see @ref
		tuning_cache_resident for more information''',
		type='boolean'),
	Config('checksum', 'on', r'''
		configure file block checksums; permitted values are
		<code>on</code> (checksum all file blocks),
		<code>off</code> (checksum no file blocks) and
		<code>uncompresssed</code> (checksum only file blocks
		which are not compressed for some reason).  The \c
		uncompressed value is for applications which can
		reasonably rely on decompression to fail if a block has
		been corrupted''',
		choices=['on', 'off', 'uncompressed']),
	Config('collator', '', r'''
		configure custom collation for keys.  Value must be a collator
		name created with WT_CONNECTION::add_collator'''),
	Config('dictionary', '0', r'''
		the maximum number of unique values remembered in the Btree
		row-store leaf page value dictionary; see
		@ref file_formats_compression for more information''',
		min='0'),
	Config('format', 'btree', r'''
		the file format''',
		choices=['btree']),
	Config('huffman_key', '', r'''
		configure Huffman encoding for keys.  Permitted values
		are empty (off), \c "english", \c "utf8<file>" or \c
		"utf16<file>".  See @ref huffman for more information'''),
	Config('huffman_value', '', r'''
		configure Huffman encoding for values.  Permitted values
		are empty (off), \c "english", \c "utf8<file>" or \c
		"utf16<file>".  See @ref huffman for more information'''),
	Config('internal_key_truncate', 'true', r'''
		configure internal key truncation, discarding unnecessary
		trailing bytes on internal keys (ignored for custom
		collators)''',
		type='boolean'),
	Config('internal_page_max', '2KB', r'''
		the maximum page size for internal nodes, in bytes; the size
		must be a multiple of the allocation size and is significant
		for applications wanting to avoid excessive L2 cache misses
		while searching the tree.  The page maximum is the bytes of
		uncompressed data, that is, the limit is applied before any
		block compression is done''',
		min='512B', max='512MB'),
	Config('internal_item_max', '0', r'''
		the maximum key size stored on internal nodes, in bytes.  If
		zero, a maximum is calculated to permit at least 8 keys per
		internal page''',
		min=0),
	Config('key_gap', '10', r'''
		the maximum gap between instantiated keys in a Btree leaf page,
		constraining the number of keys processed to instantiate a
		random Btree leaf page key''',
		min='0'),
	Config('leaf_page_max', '1MB', r'''
		the maximum page size for leaf nodes, in bytes; the size must
		be a multiple of the allocation size, and is significant for
		applications wanting to maximize sequential data transfer from
		a storage device.  The page maximum is the bytes of uncompressed
		data, that is, the limit is applied before any block compression
		is done''',
		min='512B', max='512MB'),
	Config('leaf_item_max', '0', r'''
		the maximum key or value size stored on leaf nodes, in bytes.
		If zero, a size is calculated to permit at least 8 items
		(values or row store keys) per leaf page''',
		min=0),
	Config('memory_page_max', '5MB', r'''
		the maximum size a page can grow to in memory before being
		reconciled to disk.  The specified size will be adjusted to a
		lower bound of <code>50 * leaf_page_max</code>.  This limit is
		soft - it is possible for pages to be temporarily larger than
		this value''',
		min='512B', max='10TB'),
	Config('prefix_compression', 'true', r'''
		configure row-store format key prefix compression''',
		type='boolean'),
	Config('split_pct', '75', r'''
		the Btree page split size as a percentage of the maximum Btree
		page size, that is, when a Btree page is split, it will be
		split into smaller pages, where each page is the specified
		percentage of the maximum Btree page size''',
		min='25', max='100'),
]

# File metadata, including both configurable and non-configurable (internal)
file_meta = file_config + [
	Config('checkpoint', '', r'''
		the file checkpoint entries'''),
	Config('version', '(major=0,minor=0)', r'''
		the file version'''),
]

table_only_meta = [
	Config('colgroups', '', r'''
		comma-separated list of names of column groups.  Each column
		group is stored separately, keyed by the primary key of the
		table.  If no column groups are specified, all columns are
		stored together in a single file.  All value columns in the
		table must appear in at least one column group.  Each column
		group must be created with a separate call to
		WT_SESSION::create''', type='list'),
]

colgroup_meta = column_meta + source_meta

index_meta = format_meta + source_meta

table_meta = format_meta + table_only_meta

# Connection runtime config, shared by conn.reconfigure and wiredtiger_open
connection_runtime_config = [
	Config('shared_cache', '', r'''
		shared cache configuration options. A database should configure either
		a cache_size or a shared_cache not both''',
		type='category', subconfig=[
		Config('chunk', '10MB', r'''
			the granularity that a shared cache is redistributed''',
			min='1MB', max='10TB'),
		Config('min', '50MB', r'''
			minimum amount of cache a database in a shared cache can have''',
			min='10MB', max='10TB'),
		Config('name', '', r'''
			name of a cache that is shared between databases'''),
		Config('size', '500MB', r'''
			maximum memory to allocate for the shared cache. Setting this
			will update the value if one is already set''',
			min='1MB', max='10TB')
		]),
	Config('cache_size', '100MB', r'''
		maximum heap memory to allocate for the cache. A database should
		configure either a cache_size or a shared_cache not both''',
		min='1MB', max='10TB'),
	Config('error_prefix', '', r'''
		prefix string for error messages'''),
	Config('eviction_dirty_target', '80', r'''
		continue evicting until the cache has less dirty pages than this
		(as a percentage). Dirty pages will only be evicted if the cache
		is full enough to trigger eviction''',
		min=10, max=99),
	Config('eviction_target', '80', r'''
		continue evicting until the cache becomes less full than this
		(as a percentage).  Must be less than \c eviction_trigger''',
		min=10, max=99),
	Config('eviction_trigger', '95', r'''
		trigger eviction when the cache becomes this full (as a
		percentage)''',
		min=10, max=99),
	Config('verbose', '', r'''
		enable messages for various events.  Options are given as a
		list, such as <code>"verbose=[evictserver,read]"</code>''',
		type='list', choices=[
		    'block',
		    'shared_cache',
		    'ckpt',
		    'evict',
		    'evictserver',
		    'fileops',
		    'hazard',
		    'lsm',
		    'mutex',
		    'read',
		    'readserver',
		    'reconcile',
		    'salvage',
		    'verify',
		    'write']),
]

session_config = [
	Config('isolation', 'read-committed', r'''
		the default isolation level for operations in this session''',
		choices=['read-uncommitted', 'read-committed', 'snapshot']),
]

methods = {
'file.meta' : Method(file_meta),

'colgroup.meta' : Method(colgroup_meta),

'index.meta' : Method(index_meta),

'table.meta' : Method(table_meta),

'cursor.close' : Method([]),

'session.close' : Method([]),

'session.compact' : Method([
	Config('trigger', '30', r'''
		Compaction will not be attempted unless the specified
		percentage of the underlying objects is expected to be
		recovered by compaction''',
		min='10', max='50'),
]),

'session.create' : Method(table_only_meta + file_config + source_meta + [
	Config('exclusive', 'false', r'''
		fail if the object exists.  When false (the default), if the
		object exists, check that its settings match the specified
		configuration''',
		type='boolean'),
]),

'session.drop' : Method([
	Config('force', 'false', r'''
		return success if the object does not exist''',
		type='boolean'),
	]),

'session.log_printf' : Method([]),

'session.open_cursor' : Method([
	Config('append', 'false', r'''
		append the value as a new record, creating a new record
		number key; valid only for cursors with record number keys''',
		type='boolean'),
	Config('bulk', 'false', r'''
		configure the cursor for bulk loads, a fast load path that may
		only be used for newly created objects. Cursors configured for
		bulk load only support the WT_CURSOR::insert and
		WT_CURSOR::close methods.  The value is usually a true/false
		flag, but the the special value \c "bitmap" is for use with
		fixed-length column stores, and allows chunks of a memory
		resident bitmap to be loaded directly into a file by passing a
		\c WT_ITEM to WT_CURSOR::set_value where the \c size field
		indicates the number of records in the bitmap (as specified by
		the file's \c value_format). Bulk load bitmap values must end
		on a byte boundary relative to the bit count - except for the
		last set of values loaded''',
		type='string'),
	Config('checkpoint', '', r'''
		the name of a checkpoint to open (the reserved name
		"WiredTigerCheckpoint" opens the most recent internal
		checkpoint taken for the object).  The cursor does not
		support data modification'''),
	Config('dump', '', r'''
		configure the cursor for dump format inputs and outputs:
		"hex" selects a simple hexadecimal format, "print"
		selects a format where only non-printing characters are
		hexadecimal encoded.  The cursor dump format is compatible
		with the @ref util_dump and @ref util_load commands''',
		choices=['hex', 'print']),
	Config('next_random', 'false', r'''
		configure the cursor to return a pseudo-random record from
		the object; valid only for row-store cursors.  Cursors
		configured with next_random only support the WT_CURSOR::next
		and WT_CURSOR::close methods.  See @ref cursor_random for
		details''',
		type='boolean'),
	Config('no_cache', 'false', r'''
		do not cache pages from the underlying object.  The cursor
		does not support data modification''',
		type='boolean', undoc=True),
	Config('overwrite', 'false', r'''
		change the behavior of the cursor's insert method to overwrite
		previously existing values''',
		type='boolean'),
	Config('raw', 'false', r'''
		ignore the encodings for the key and value, manage data as if
		the formats were \c "u".  See @ref cursor_raw for details''',
		type='boolean'),
	Config('statistics_clear', 'false', r'''
		reset statistics counters when the cursor is closed; valid
		only for statistics cursors''',
		type='boolean'),
	Config('statistics_fast', 'false', r'''
		only gather statistics that don't require traversing the tree;
		valid only for statistics cursors''',
		type='boolean'),
	Config('target', '', r'''
		if non-empty, backup the list of objects; valid only for a
		backup data source''',
		type='list'),
]),

'session.rename' : Method([]),
'session.salvage' : Method([
	Config('force', 'false', r'''
		force salvage even of files that do not appear to be WiredTiger
		files''',
		type='boolean'),
]),
'session.truncate' : Method([]),
'session.upgrade' : Method([]),
'session.verify' : Method([
	Config('dump_address', 'false', r'''
	Display addresses and page types as pages are verified, using
	the application's message handler, intended for debugging''',
	type='boolean'),
	Config('dump_blocks', 'false', r'''
	Display the contents of on-disk blocks as they are verified, using
	the application's message handler, intended for debugging''',
	type='boolean'),
	Config('dump_pages', 'false', r'''
	Display the contents of in-memory pages as they are verified, using
	the application's message handler, intended for debugging''',
	type='boolean')
]),

'session.begin_transaction' : Method([
	Config('isolation', '', r'''
		the isolation level for this transaction; defaults to the
		session's isolation level''',
		choices=['read-uncommitted', 'read-committed', 'snapshot']),
	Config('name', '', r'''
		name of the transaction for tracing and debugging'''),
	Config('priority', 0, r'''
		priority of the transaction for resolving conflicts.
		Transactions with higher values are less likely to abort''',
		min='-100', max='100'),
	Config('sync', 'full', r'''
		how to sync log records when the transaction commits''',
		choices=['full', 'flush', 'write', 'none']),
]),

'session.commit_transaction' : Method([]),
'session.rollback_transaction' : Method([]),

'session.checkpoint' : Method([
	Config('drop', '', r'''
		specify a list of checkpoints to drop.
		The list may additionally contain one of the following keys:
		\c "from=all" to drop all checkpoints,
		\c "from=<checkpoint>" to drop all checkpoints after and
		including the named checkpoint, or
		\c "to=<checkpoint>" to drop all checkpoints before and
		including the named checkpoint.  Checkpoints cannot be
		dropped while a hot backup is in progress or if open in
		a cursor''', type='list'),
	Config('force', 'false', r'''
		checkpoints may be skipped if the underlying object has not
		been modified, this option forces the checkpoint''',
		type='boolean'),
	Config('name', '', r'''
		if non-empty, specify a name for the checkpoint'''),
	Config('target', '', r'''
		if non-empty, checkpoint the list of objects''', type='list'),
]),

'connection.add_collator' : Method([]),
'connection.add_compressor' : Method([]),
'connection.add_data_source' : Method([]),
'connection.add_extractor' : Method([]),
'connection.close' : Method([]),
'connection.reconfigure' : Method(connection_runtime_config),

'connection.load_extension' : Method([
	Config('entry', 'wiredtiger_extension_init', r'''
		the entry point of the extension'''),
	Config('prefix', '', r'''
		a prefix for all names registered by this extension (e.g., to
		make namespaces distinct or during upgrades'''),
]),

'connection.open_session' : Method(session_config),

'session.reconfigure' : Method(session_config),

'wiredtiger_open' : Method(connection_runtime_config + [
	Config('buffer_alignment', '-1', r'''
		in-memory alignment (in bytes) for buffers used for I/O.  The default
		value of -1 indicates that a platform-specific alignment value should
		be used (512 bytes on Linux systems, zero elsewhere)''',
		min='-1', max='1MB'),
	Config('create', 'false', r'''
		create the database if it does not exist''',
		type='boolean'),
	Config('direct_io', '', r'''
		Use \c O_DIRECT to access files.  Options are given as a
		list, such as <code>"direct_io=[data]"</code>''',
		type='list', choices=['data', 'log']),
	Config('extensions', '', r'''
		list of shared library extensions to load (using dlopen).
		Optional values are passed as the \c config parameter to
		WT_CONNECTION::load_extension.  Complex paths may require
		quoting, for example,
		<code>extensions=("/path/ext.so"="entry=my_entry")</code>''',
		type='list'),
	Config('hazard_max', '1000', r'''
		maximum number of simultaneous hazard pointers per session
		handle''',
		min='15'),
	Config('logging', 'false', r'''
		enable logging''',
		type='boolean'),
	Config('lsm_merge', 'true', r'''
		merge LSM chunks where possible''',
		type='boolean'),
	Config('multiprocess', 'false', r'''
		permit sharing between processes (will automatically start an
		RPC server for primary processes and use RPC for secondary
		processes). <b>Not yet supported in WiredTiger</b>''',
		type='boolean'),
	Config('session_max', '50', r'''
		maximum expected number of sessions (including server
		threads)''',
		min='1'),
	Config('sync', 'true', r'''
		flush files to stable storage when closing or writing
		checkpoints''',
		type='boolean'),
	Config('transactional', 'true', r'''
		support transactional semantics''',
		type='boolean'),
	Config('use_environment_priv', 'false', r'''
		use the \c WIREDTIGER_CONFIG and \c WIREDTIGER_HOME environment
		variables regardless of whether or not the process is running
		with special privileges.  See @ref home for more information''',
		type='boolean'),
]),
}
