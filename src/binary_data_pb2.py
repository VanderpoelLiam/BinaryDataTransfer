# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: binary_data.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='binary_data.proto',
  package='binaryData',
  syntax='proto3',
  serialized_pb=_b('\n\x11\x62inary_data.proto\x12\nbinaryData\x1a\x1fgoogle/protobuf/timestamp.proto\"-\n\x08\x42lobSpec\x12\x0c\n\x04size\x18\x01 \x01(\x05\x12\x13\n\x0b\x63hunk_count\x18\x02 \x01(\x05\"[\n\x08\x42lobInfo\x12\x1e\n\x02id\x18\x01 \x01(\x0b\x32\x12.binaryData.BlobId\x12/\n\x0bvalid_until\x18\x02 \x01(\x0b\x32\x1a.binaryData.ExpirationTime\"1\n\x05\x45rror\x12\x13\n\x0bhas_occured\x18\x01 \x01(\x08\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\":\n\x0e\x45xpirationTime\x12(\n\x04time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x14\n\x06\x42lobId\x12\n\n\x02id\x18\x01 \x01(\x05\"\x97\x01\n\x08Response\x12 \n\x05\x65rror\x18\x01 \x01(\x0b\x32\x11.binaryData.Error\x12/\n\x0bvalid_until\x18\x02 \x01(\x0b\x32\x1a.binaryData.ExpirationTime\x12\'\n\tblob_info\x18\x03 \x01(\x0b\x32\x14.binaryData.BlobInfo\x12\x0f\n\x07payload\x18\x04 \x01(\x0c\"L\n\x05\x43hunk\x12#\n\x07\x62lob_id\x18\x01 \x01(\x0b\x32\x12.binaryData.BlobId\x12\r\n\x05index\x18\x02 \x01(\x05\x12\x0f\n\x07payload\x18\x03 \x01(\x0c\"?\n\tChunkSpec\x12#\n\x07\x62lob_id\x18\x01 \x01(\x0b\x32\x12.binaryData.BlobId\x12\r\n\x05index\x18\x02 \x01(\x05\x32\xaf\x01\n\x06Upload\x12\x38\n\nCreateBlob\x12\x14.binaryData.BlobSpec\x1a\x14.binaryData.Response\x12\x36\n\x0bUploadChunk\x12\x11.binaryData.Chunk\x1a\x14.binaryData.Response\x12\x33\n\nDeleteBlob\x12\x12.binaryData.BlobId\x1a\x11.binaryData.Error2\xe9\x01\n\nFileServer\x12@\n\x12ValidateFileServer\x12\x14.binaryData.BlobSpec\x1a\x14.binaryData.Response\x12/\n\x04Save\x12\x11.binaryData.Chunk\x1a\x14.binaryData.Response\x12\x37\n\x08\x44ownload\x12\x15.binaryData.ChunkSpec\x1a\x14.binaryData.Response\x12/\n\x06\x44\x65lete\x12\x12.binaryData.BlobId\x1a\x11.binaryData.Errorb\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,])




_BLOBSPEC = _descriptor.Descriptor(
  name='BlobSpec',
  full_name='binaryData.BlobSpec',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='size', full_name='binaryData.BlobSpec.size', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='chunk_count', full_name='binaryData.BlobSpec.chunk_count', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=66,
  serialized_end=111,
)


_BLOBINFO = _descriptor.Descriptor(
  name='BlobInfo',
  full_name='binaryData.BlobInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='binaryData.BlobInfo.id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='valid_until', full_name='binaryData.BlobInfo.valid_until', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=113,
  serialized_end=204,
)


_ERROR = _descriptor.Descriptor(
  name='Error',
  full_name='binaryData.Error',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='has_occured', full_name='binaryData.Error.has_occured', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='description', full_name='binaryData.Error.description', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=206,
  serialized_end=255,
)


_EXPIRATIONTIME = _descriptor.Descriptor(
  name='ExpirationTime',
  full_name='binaryData.ExpirationTime',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='time', full_name='binaryData.ExpirationTime.time', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=257,
  serialized_end=315,
)


_BLOBID = _descriptor.Descriptor(
  name='BlobId',
  full_name='binaryData.BlobId',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='binaryData.BlobId.id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=317,
  serialized_end=337,
)


_RESPONSE = _descriptor.Descriptor(
  name='Response',
  full_name='binaryData.Response',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='error', full_name='binaryData.Response.error', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='valid_until', full_name='binaryData.Response.valid_until', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='blob_info', full_name='binaryData.Response.blob_info', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='payload', full_name='binaryData.Response.payload', index=3,
      number=4, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=340,
  serialized_end=491,
)


_CHUNK = _descriptor.Descriptor(
  name='Chunk',
  full_name='binaryData.Chunk',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='blob_id', full_name='binaryData.Chunk.blob_id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='index', full_name='binaryData.Chunk.index', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='payload', full_name='binaryData.Chunk.payload', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=493,
  serialized_end=569,
)


_CHUNKSPEC = _descriptor.Descriptor(
  name='ChunkSpec',
  full_name='binaryData.ChunkSpec',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='blob_id', full_name='binaryData.ChunkSpec.blob_id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='index', full_name='binaryData.ChunkSpec.index', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=571,
  serialized_end=634,
)

_BLOBINFO.fields_by_name['id'].message_type = _BLOBID
_BLOBINFO.fields_by_name['valid_until'].message_type = _EXPIRATIONTIME
_EXPIRATIONTIME.fields_by_name['time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_RESPONSE.fields_by_name['error'].message_type = _ERROR
_RESPONSE.fields_by_name['valid_until'].message_type = _EXPIRATIONTIME
_RESPONSE.fields_by_name['blob_info'].message_type = _BLOBINFO
_CHUNK.fields_by_name['blob_id'].message_type = _BLOBID
_CHUNKSPEC.fields_by_name['blob_id'].message_type = _BLOBID
DESCRIPTOR.message_types_by_name['BlobSpec'] = _BLOBSPEC
DESCRIPTOR.message_types_by_name['BlobInfo'] = _BLOBINFO
DESCRIPTOR.message_types_by_name['Error'] = _ERROR
DESCRIPTOR.message_types_by_name['ExpirationTime'] = _EXPIRATIONTIME
DESCRIPTOR.message_types_by_name['BlobId'] = _BLOBID
DESCRIPTOR.message_types_by_name['Response'] = _RESPONSE
DESCRIPTOR.message_types_by_name['Chunk'] = _CHUNK
DESCRIPTOR.message_types_by_name['ChunkSpec'] = _CHUNKSPEC
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

BlobSpec = _reflection.GeneratedProtocolMessageType('BlobSpec', (_message.Message,), dict(
  DESCRIPTOR = _BLOBSPEC,
  __module__ = 'binary_data_pb2'
  # @@protoc_insertion_point(class_scope:binaryData.BlobSpec)
  ))
_sym_db.RegisterMessage(BlobSpec)

BlobInfo = _reflection.GeneratedProtocolMessageType('BlobInfo', (_message.Message,), dict(
  DESCRIPTOR = _BLOBINFO,
  __module__ = 'binary_data_pb2'
  # @@protoc_insertion_point(class_scope:binaryData.BlobInfo)
  ))
_sym_db.RegisterMessage(BlobInfo)

Error = _reflection.GeneratedProtocolMessageType('Error', (_message.Message,), dict(
  DESCRIPTOR = _ERROR,
  __module__ = 'binary_data_pb2'
  # @@protoc_insertion_point(class_scope:binaryData.Error)
  ))
_sym_db.RegisterMessage(Error)

ExpirationTime = _reflection.GeneratedProtocolMessageType('ExpirationTime', (_message.Message,), dict(
  DESCRIPTOR = _EXPIRATIONTIME,
  __module__ = 'binary_data_pb2'
  # @@protoc_insertion_point(class_scope:binaryData.ExpirationTime)
  ))
_sym_db.RegisterMessage(ExpirationTime)

BlobId = _reflection.GeneratedProtocolMessageType('BlobId', (_message.Message,), dict(
  DESCRIPTOR = _BLOBID,
  __module__ = 'binary_data_pb2'
  # @@protoc_insertion_point(class_scope:binaryData.BlobId)
  ))
_sym_db.RegisterMessage(BlobId)

Response = _reflection.GeneratedProtocolMessageType('Response', (_message.Message,), dict(
  DESCRIPTOR = _RESPONSE,
  __module__ = 'binary_data_pb2'
  # @@protoc_insertion_point(class_scope:binaryData.Response)
  ))
_sym_db.RegisterMessage(Response)

Chunk = _reflection.GeneratedProtocolMessageType('Chunk', (_message.Message,), dict(
  DESCRIPTOR = _CHUNK,
  __module__ = 'binary_data_pb2'
  # @@protoc_insertion_point(class_scope:binaryData.Chunk)
  ))
_sym_db.RegisterMessage(Chunk)

ChunkSpec = _reflection.GeneratedProtocolMessageType('ChunkSpec', (_message.Message,), dict(
  DESCRIPTOR = _CHUNKSPEC,
  __module__ = 'binary_data_pb2'
  # @@protoc_insertion_point(class_scope:binaryData.ChunkSpec)
  ))
_sym_db.RegisterMessage(ChunkSpec)



_UPLOAD = _descriptor.ServiceDescriptor(
  name='Upload',
  full_name='binaryData.Upload',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=637,
  serialized_end=812,
  methods=[
  _descriptor.MethodDescriptor(
    name='CreateBlob',
    full_name='binaryData.Upload.CreateBlob',
    index=0,
    containing_service=None,
    input_type=_BLOBSPEC,
    output_type=_RESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='UploadChunk',
    full_name='binaryData.Upload.UploadChunk',
    index=1,
    containing_service=None,
    input_type=_CHUNK,
    output_type=_RESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DeleteBlob',
    full_name='binaryData.Upload.DeleteBlob',
    index=2,
    containing_service=None,
    input_type=_BLOBID,
    output_type=_ERROR,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_UPLOAD)

DESCRIPTOR.services_by_name['Upload'] = _UPLOAD


_FILESERVER = _descriptor.ServiceDescriptor(
  name='FileServer',
  full_name='binaryData.FileServer',
  file=DESCRIPTOR,
  index=1,
  options=None,
  serialized_start=815,
  serialized_end=1048,
  methods=[
  _descriptor.MethodDescriptor(
    name='ValidateFileServer',
    full_name='binaryData.FileServer.ValidateFileServer',
    index=0,
    containing_service=None,
    input_type=_BLOBSPEC,
    output_type=_RESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Save',
    full_name='binaryData.FileServer.Save',
    index=1,
    containing_service=None,
    input_type=_CHUNK,
    output_type=_RESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Download',
    full_name='binaryData.FileServer.Download',
    index=2,
    containing_service=None,
    input_type=_CHUNKSPEC,
    output_type=_RESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Delete',
    full_name='binaryData.FileServer.Delete',
    index=3,
    containing_service=None,
    input_type=_BLOBID,
    output_type=_ERROR,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_FILESERVER)

DESCRIPTOR.services_by_name['FileServer'] = _FILESERVER

# @@protoc_insertion_point(module_scope)
