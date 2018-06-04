# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import binary_data_pb2 as binary__data__pb2


class UploadStub(object):
  """Interfaces exported by the server.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.CreateBlob = channel.unary_unary(
        '/binaryData.Upload/CreateBlob',
        request_serializer=binary__data__pb2.BlobSpec.SerializeToString,
        response_deserializer=binary__data__pb2.Response.FromString,
        )
    self.UploadChunk = channel.unary_unary(
        '/binaryData.Upload/UploadChunk',
        request_serializer=binary__data__pb2.Chunk.SerializeToString,
        response_deserializer=binary__data__pb2.Response.FromString,
        )
    self.DeleteBlob = channel.unary_unary(
        '/binaryData.Upload/DeleteBlob',
        request_serializer=binary__data__pb2.BlobId.SerializeToString,
        response_deserializer=binary__data__pb2.Error.FromString,
        )
    self.GetAverageBrightness = channel.unary_unary(
        '/binaryData.Upload/GetAverageBrightness',
        request_serializer=binary__data__pb2.BlobId.SerializeToString,
        response_deserializer=binary__data__pb2.Empty.FromString,
        )


class UploadServicer(object):
  """Interfaces exported by the server.
  """

  def CreateBlob(self, request, context):
    """Checks if we can create a Blob specified by BlobSpec on the FileServer
    and returns the BlobInfo to access the Blob. Returns an Error if there is
    not enough space.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def UploadChunk(self, request, context):
    """Uploads a Chunk to the server and returns the updated ExpirationTime
    Returns an Error if it fails for any reason.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def DeleteBlob(self, request, context):
    """Deletes the Blob associated with BlobId and returns an Error object
    containing a description of the error that occured, or an empty
    description if the deletion was a success.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetAverageBrightness(self, request, context):
    """Performs a pre-defined analysis on the Blob associated with BlobId. In
    this case it gets the average brightness of an image.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_UploadServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'CreateBlob': grpc.unary_unary_rpc_method_handler(
          servicer.CreateBlob,
          request_deserializer=binary__data__pb2.BlobSpec.FromString,
          response_serializer=binary__data__pb2.Response.SerializeToString,
      ),
      'UploadChunk': grpc.unary_unary_rpc_method_handler(
          servicer.UploadChunk,
          request_deserializer=binary__data__pb2.Chunk.FromString,
          response_serializer=binary__data__pb2.Response.SerializeToString,
      ),
      'DeleteBlob': grpc.unary_unary_rpc_method_handler(
          servicer.DeleteBlob,
          request_deserializer=binary__data__pb2.BlobId.FromString,
          response_serializer=binary__data__pb2.Error.SerializeToString,
      ),
      'GetAverageBrightness': grpc.unary_unary_rpc_method_handler(
          servicer.GetAverageBrightness,
          request_deserializer=binary__data__pb2.BlobId.FromString,
          response_serializer=binary__data__pb2.Empty.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'binaryData.Upload', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class DownloadStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetChunk = channel.unary_unary(
        '/binaryData.Download/GetChunk',
        request_serializer=binary__data__pb2.ChunkSpec.SerializeToString,
        response_deserializer=binary__data__pb2.Response.FromString,
        )
    self.GetBlobInfo = channel.unary_unary(
        '/binaryData.Download/GetBlobInfo',
        request_serializer=binary__data__pb2.BlobId.SerializeToString,
        response_deserializer=binary__data__pb2.BlobInfo.FromString,
        )


class DownloadServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetChunk(self, request, context):
    """Downloads the Chunk specified by ChunkSpec from the server and returns
    the associated Payload and ExpirationTime in the response. Returns an
    Error if it fails for any reason.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetBlobInfo(self, request, context):
    """Gets the BlobInfo assiciated with the given BlobID
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_DownloadServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetChunk': grpc.unary_unary_rpc_method_handler(
          servicer.GetChunk,
          request_deserializer=binary__data__pb2.ChunkSpec.FromString,
          response_serializer=binary__data__pb2.Response.SerializeToString,
      ),
      'GetBlobInfo': grpc.unary_unary_rpc_method_handler(
          servicer.GetBlobInfo,
          request_deserializer=binary__data__pb2.BlobId.FromString,
          response_serializer=binary__data__pb2.BlobInfo.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'binaryData.Download', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class FileServerStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.ValidateFileServer = channel.unary_unary(
        '/binaryData.FileServer/ValidateFileServer',
        request_serializer=binary__data__pb2.BlobSpec.SerializeToString,
        response_deserializer=binary__data__pb2.Response.FromString,
        )
    self.Save = channel.unary_unary(
        '/binaryData.FileServer/Save',
        request_serializer=binary__data__pb2.Chunk.SerializeToString,
        response_deserializer=binary__data__pb2.Response.FromString,
        )
    self.Download = channel.unary_unary(
        '/binaryData.FileServer/Download',
        request_serializer=binary__data__pb2.ChunkSpec.SerializeToString,
        response_deserializer=binary__data__pb2.Response.FromString,
        )
    self.Delete = channel.unary_unary(
        '/binaryData.FileServer/Delete',
        request_serializer=binary__data__pb2.BlobId.SerializeToString,
        response_deserializer=binary__data__pb2.Error.FromString,
        )


class FileServerServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def ValidateFileServer(self, request, context):
    """Checks if we can create a Blob specified by BlobSpec on the FileServer
    and returns the ExpirationTime until which the Blob is valid. Returns an
    Error if there is not enough space.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Save(self, request, context):
    """Saves a Chunk to the server and returns the updated ExpirationTime
    Returns an Error if there if it fails for any reason.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Download(self, request, context):
    """Downloads the Chunk specified by ChunkSpec from the server and returns
    the associated Payload and ExpirationTime in the response. Returns an
    Error if it fails for any reason.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Delete(self, request, context):
    """Deletes the Blob associated with BlobId and returns an Error object
    containing a description of the error that occured, or an empty
    description if the deletion was a success.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_FileServerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'ValidateFileServer': grpc.unary_unary_rpc_method_handler(
          servicer.ValidateFileServer,
          request_deserializer=binary__data__pb2.BlobSpec.FromString,
          response_serializer=binary__data__pb2.Response.SerializeToString,
      ),
      'Save': grpc.unary_unary_rpc_method_handler(
          servicer.Save,
          request_deserializer=binary__data__pb2.Chunk.FromString,
          response_serializer=binary__data__pb2.Response.SerializeToString,
      ),
      'Download': grpc.unary_unary_rpc_method_handler(
          servicer.Download,
          request_deserializer=binary__data__pb2.ChunkSpec.FromString,
          response_serializer=binary__data__pb2.Response.SerializeToString,
      ),
      'Delete': grpc.unary_unary_rpc_method_handler(
          servicer.Delete,
          request_deserializer=binary__data__pb2.BlobId.FromString,
          response_serializer=binary__data__pb2.Error.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'binaryData.FileServer', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
