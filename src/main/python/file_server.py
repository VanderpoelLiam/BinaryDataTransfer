from datetime import datetime, timedelta
from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp
import grpc
import time

import binary_data_pb2
import binary_data_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def get_validation(blob_spec):
    flag = has_space(blob_spec.blobSize)
    valid_until = binary_data_pb2.ExpirationTime(time=get_expiration())
    return binary_data_pb2.Validation(wasSuccess=flag, expiration=valid_until)

def has_space(blob_size):
    # Assume server has unlimited space
    return True

def get_expiration():
    # Assume server can store data for 1 year (365 days)
    expiration_date = Timestamp()
    expiration_date.FromDatetime(datetime.now() + timedelta(days=365))
    return expiration_date


class FileServerServicer(binary_data_pb2_grpc.FileServerServicer):
    """Provides methods that implement functionality of the file server.
    The functions follow the following format:
    Inputs:
            request - a binary_data_pb2 object request for the RPC
            context - grpc.ServicerContext object that provides RPC-specific
                      information such as timeout limits.
        Outputs:
            response - a binary_data_pb2 object response for the client
    """

    def ValidateFileServer(self, request, context):
        """request  - BlobSpec
           response - Validation
        """
        validation = get_validation(request)
        return validation

    def Save(self, request, context):
        """request  - Blob
           response - ErrorStatus
        """
        # TODO

    def Delete(self, request, context):
        """request  - BlobId
           response - ErrorStatus
        """
        # TODO

    def Download(self, request, context):
        """request  - BlobId
           response - ErrorStatus
        """
        # TODO


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    binary_data_pb2_grpc.add_FileServerServicer_to_server(
        FileServerServicer(), server)
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
