from concurrent import futures
from resources import read_db, write_db
from google.protobuf.json_format import MessageToJson, Parse
import grpc
import time
import math
import binary_data_pb2
import binary_data_pb2_grpc


_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def performMeasurement():
    data = b'This is some data'
    # TODO how get size of bytes object above in bits
    size = 1
    return (data, size)

def save_blob_info(filename, blob_info):
    data = read_db(filename)
    blob_id = str(blob_info.id.id)
    data[blob_id] = MessageToJson(blob_info)
    write_db(filename, data)

def read_blob_info(filename, blob_id):
    data = read_db(filename)
    key = str(blob_id.id)
    temp = data[key]
    blob_info = Parse(data[key], binary_data_pb2.BlobInfo())
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
        if error.has_occured:
            return binary_data_pb2.Response(error=error)
        else:
            valid_until = response.valid_until
            id = self._generate_blob_id()
            blob_info = binary_data_pb2.BlobInfo(id=id,
                                                 valid_until=valid_until)
            return binary_data_pb2.Response(blob_info=blob_info)

    def UploadChunk(self, request, context):
        """Uploads a Chunk to the server and returns the updated ExpirationTime
        Returns an Error if there if it fails for any reason.
        """
        # TODO implement error handling
        chunk = request
        response = self.stub.Save(chunk)
        return response

    def DeleteBlob(self, request, context):
        """Deletes the Blob associated with BlobId and returns an Error object
        containing a description of the error that occured, or an empty
        description if the deletion was a success.
        """
        try:
            # TODO how check type of request
            request.id
        except Exception:
            error = binary_data_pb2.Error(has_occured=True, description="Request was not of type BlobId")
        else:
            blob_id = request
            error = self.stub.Delete(blob_id)
        return error

    def GetAverageBrightness(self, request, context):
        """Performs a pre-defined analysis on the Blob associated with BlobId. In
        this case it gets the average brightness of an image.
        """
        return binary_data_pb2.Empty()


class DownloadServicer(binary_data_pb2_grpc.DownloadServicer):
    """Interfaces exported by the server.
    """
    def __init__(self, file_server_stub, database_filename):
        self.stub = file_server_stub
        self._DATABASE_FILENAME = database_filename

    def GetChunk(self, request, context):
        """Downloads the Chunk specified by ChunkSpec from the server and returns
        the associated Payload and ExpirationTime in the response. Returns an
        Error if it fails for any reason.
        """
        chunk_spec = request
        response = self.stub.Download(chunk_spec)
        return response

    def GetBlobInfo(self, request, context):
        """Gets the BlobInfo assiciated with the given BlobID
        """
        blob_info = request
        # TODO
        return

    def GetMeasurementData(self, request, context):
        """Performs an Action which generates a Blob on the server. Returns the
        associated BlobInfo, or an Error if something goes wrong. In this case
        the action is to get the measurement data of the device.
        """
        # Perform an action which generates the following bytes of data
        # and the size in bits
        data, size = performMeasurement()

        # max_chunk_size is likely a property of the server, but we simply fix it
        max_chunk_size = size

        # This is 1 due to above line
        chunk_count = math.ceil(size/max_chunk_size)

        # Define spec and create a blob to store this data on the server
        blob_spec = binary_data_pb2.BlobSpec(size=size, chunk_count=chunk_count)
        upload_servicer = UploadServicer(self.stub)
        creation_response = upload_servicer.CreateBlob(blob_spec, context)

        # Rename relevant variables
        blob_id = creation_response.blob_info.id
        valid_until = creation_response.blob_info.valid_until

        # Save the data to the server
        chunk = binary_data_pb2.Chunk(blob_id=blob_id, index=0, payload=data)
        upload_response = upload_servicer.UploadChunk(chunk, context)

        # Create and Save the blob_info to the device
        blob_info = binary_data_pb2.BlobInfo(id=blob_id,
                                                valid_until=valid_until,
                                                spec=blob_spec)
        save_blob_info(self._DATABASE_FILENAME, blob_info)

        # Create a new response that is the same as the creation_response but
        # adds the above blob_spec to the blob_info
        response = binary_data_pb2.Response(valid_until=valid_until,
                                            error=creation_response.error,
                                            blob_info=blob_info)

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
