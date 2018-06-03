from concurrent import futures
import grpc
import time
import binary_data_pb2
import binary_data_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

# def generate_blob_id():
#     blob_id =  get_current_blob_id()
#     _COUNTER += 1
#     return blob_id
#
# def get_current_blob_id():
#     return binary_data_pb2.BlobId(id=_COUNTER)

def get_blob_info(valid_until):
    blob_id = generate_blob_id()
    blob_info = binary_data_pb2.BlobInfo(id=blob_id, valid_until=valid_until)
    return blob_info

class UploadServicer(binary_data_pb2_grpc.UploadServicer):
    """Interfaces exported by the server.
    """
    def __init__(self, file_server_stub):
        self.stub = file_server_stub
        self._COUNTER = 0

    def _generate_blob_id(self):
        blob_id = self._get_current_blob_id()
        self._COUNTER += 1
        return blob_id

    def _get_current_blob_id(self):
        return binary_data_pb2.BlobId(id=self._COUNTER)

    def CreateBlob(self, request, context):
        """Checks if we can create a Blob specified by BlobSpec on the FileServer
        and returns the BlobInfo to access the Blob. Returns an Error if there is
        not enough space.
        """
        blob_spec = request
        response = self.stub.ValidateFileServer(blob_spec)
        error = response.error
        if error.description == "":
            valid_until = response.valid_until
            blob_info = binary_data_pb2.BlobInfo(id=self._generate_blob_id(),
                                                 valid_until=valid_until)
            # blob_info = binary_data_pb2.BlobInfo(id=self._generate_blob_id(),
            #                                      valid_until=valid_until)
            return binary_data_pb2.Response(blob_info=blob_info)
        else:
            return binary_data_pb2.Response(error=error)

    def UploadChunk(self, request, context):
        """Uploads a Chunk to the server and returns the updated ExpirationTime
        Returns an Error if there if it fails for any reason.
        """
        # TODO implement error handling
        chunk = request
        response = self.stub.Save(chunk)
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    binary_data_pb2_grpc.add_UploadServicer_to_server(
        UploadServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            print("\nServer is ready...")
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
