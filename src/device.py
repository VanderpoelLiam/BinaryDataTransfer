from concurrent import futures
import grpc
import time
import binary_data_pb2
import binary_data_pb2_grpc

_COUNTER = 0
_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def generate_blob_id():
    blob_id =  binary_data_pb2.BlobId(id=_COUNTER)
    _COUNTER += 1
    return blob_id

def get_blob_info(valid_until):
    blob_id = generate_blob_id()
    blob_info = binary_data_pb2.BlobInfo(id=blob_id, valid_until=valid_until)
    return blob_info

class UploadServicer(binary_data_pb2_grpc.UploadServicer):
    """Interfaces exported by the server.
    """
    def __init__(self):
        channel = grpc.insecure_channel('localhost:50051')
        self.stub = binary_data_pb2_grpc.FileServerStub(channel)

    def CreateBlob(self, request, context):
        """Checks if we can create a Blob specified by BlobSpec on the FileServer
        and returns the BlobInfo to access the Blob. Returns an Error if there is
        not enough space.
        """
        print("Inside CreateBlob")
        blob_spec = request
        response = self.stub.ValidateFileServer(blob_spec)
        if response.has_error():
            return response
        else:
            valid_until = response.payload
            blob_info = get_blob_info(valid_until)
            return binary_data_pb2.Response(payload=blob_info)


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
