import grpc

import binary_data_pb2
import binary_data_pb2_grpc


def file_server_validate(stub):
    # Assume these fixed values for now
    blob_size = 32
    chuck_count = 2

    blob_spec = binary_data_pb2.BlobSpec(blobSize=blob_size, chunkCount=chuck_count)
    validation = stub.ValidateFileServer(blob_spec)
    if validation.wasSuccess:
        print("Server can store the blob until %r" % validation.expiration)
    else:
        print("Sorry, server cannot store the blob")


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = binary_data_pb2_grpc.FileServerStub(channel)
    print("-------------- ValidateFileServer --------------")
    file_server_validate(stub)


if __name__ == '__main__':
    run()
