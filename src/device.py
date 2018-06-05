import math
import time

import binary_data_pb2
import binary_data_pb2_grpc
from google.protobuf.json_format import MessageToJson, Parse
from resources_files import read_db, write_db
import resources_server
import file_server

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def perform_measurement():
    # TODO measurement should just be opening the image of the puppy
    data = b'This is some data'
    size = 1
    return (data, size)


def save_blob_info(filename, blob_info):
    # print("Before read_db")
    # print(filename)
    # print(MessageToJson(blob_info))
    data = read_db(filename)
    # print("After read_db")
    blob_id = str(blob_info.id.id)
    data[blob_id] = MessageToJson(blob_info)
    write_db(filename, data)


def read_blob_info(filename, blob_id):
    data = read_db(filename)
    key = str(blob_id.id)
    temp = data[key]
    blob_info = Parse(data[key], binary_data_pb2.BlobInfo())
    return blob_info


def average_image_brightness(im):
    im_grey = im.convert('LA')  # convert to grayscale
    width, height = im.size

    total = 0
    for i in range(0, width):
        for j in range(0, height):
            total += img.getpixel((i, j))[0]

    mean = total / (width * height)
    return mean


class UploadServicer(binary_data_pb2_grpc.UploadServicer):
    """Interfaces exported by the server.
    """

    def __init__(self, file_server_stub, database_filename):
        self.stub = file_server_stub
        self._COUNTER = 0
        self._DATABASE_FILENAME = database_filename

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
        # print("Before ValidateFileServer")
        response = self.stub.ValidateFileServer(blob_spec)
        # print("After ValidateFileServer")
        error = response.error

        if error.has_occured:
            return binary_data_pb2.Response(error=error)
        else:
            # Create and Save the blob_info to the device
            valid_until = response.valid_until
            id = self._generate_blob_id()
            blob_info = binary_data_pb2.BlobInfo(id=id,
                                                 valid_until=valid_until,
                                                 spec=blob_spec)
            # print("Before save_blob_info")
            save_blob_info(self._DATABASE_FILENAME, blob_info)
            # print("After save_blob_info")
            return binary_data_pb2.Response(blob_info=blob_info)

    def UploadChunk(self, request, context):
        """Uploads a Chunk to the server and returns the updated ExpirationTime
        Returns an Error if there if it fails for any reason.
        """
        chunk = request
        response = self.stub.Save(chunk)
        return response

    def DeleteBlob(self, request, context):
        """Deletes the Blob associated with BlobId and returns an Error object
        containing a description of the error that occured, or an empty
        description if the deletion was a success.
        """
        try:
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
        blob_id = request
        blob_info = read_blob_info(self._DATABASE_FILENAME, blob_id)
        return blob_info

    def GetMeasurementData(self, request, context):
        """Performs an Action which generates a Blob on the server. Returns the
        associated BlobInfo, or an Error if something goes wrong. In this case
        the action is to get the measurement data of the device.
        """
        # Perform an action which generates the following bytes of data
        # and the size in bits
        data, size = perform_measurement()

        # max_chunk_size is likely a property of the server, but we simply fix it
        max_chunk_size = size

        # This is 1 due to above line
        chunk_count = math.ceil(size / max_chunk_size)

        # Define spec and create a blob to store this data on the server
        blob_spec = binary_data_pb2.BlobSpec(size=size, chunk_count=chunk_count)
        upload_servicer = UploadServicer(self.stub, self._DATABASE_FILENAME)
        creation_response = upload_servicer.CreateBlob(blob_spec, context)

        # Rename relevant variables
        blob_id = creation_response.blob_info.id
        valid_until = creation_response.blob_info.valid_until

        # Save the data to the server
        chunk = binary_data_pb2.Chunk(blob_id=blob_id, index=0, payload=data)
        upload_response = upload_servicer.UploadChunk(chunk, context)

        # Create a new response that is the same as the creation_response but
        # adds the above blob_spec to the blob_info
        blob_info = binary_data_pb2.BlobInfo(id=blob_id,
                                             valid_until=valid_until,
                                             spec=blob_spec)
        response = binary_data_pb2.Response(valid_until=valid_until,
                                            error=creation_response.error,
                                            blob_info=blob_info)

        return response


def serve():
    server = resources_server.get_grpc_server()
    stub = resources_server.get_file_server_stub()
    server_size = math.inf

    binary_data_pb2_grpc.add_FileServerServicer_to_server(
        file_server.FileServerServicer(server_size, 'files_db.json'), server)

    binary_data_pb2_grpc.add_UploadServicer_to_server(
        UploadServicer(stub, 'device_db.json'), server)

    binary_data_pb2_grpc.add_DownloadServicer_to_server(
        DownloadServicer(stub, 'device_db.json'), server)

    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            print("Device Ready...")
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
  serve()
