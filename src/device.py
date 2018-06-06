import math
import os
import time

import binary_data_pb2
import binary_data_pb2_grpc
import file_server
import resources_server
from PIL import Image
from google.protobuf.json_format import MessageToJson, Parse
from resources_files import read_db, write_db

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_COUNTER = 0


def get_chunk_size(blob_spec):
    blob_size = blob_spec.size
    chunk_count = blob_spec.chunk_count
    chunk_size = math.ceil(blob_size/chunk_count)  # Overestimate chunk_size
    return chunk_size


def create_blob_spec(filename):
    blob_size = os.stat(filename).st_size # File size in bytes
    chunk_count = 10
    chunk_size = math.ceil(blob_size/chunk_count)  # Overestimate chunk_size
    blob_spec = binary_data_pb2.BlobSpec(size=blob_size, chunk_count=chunk_count)
    return blob_spec


def create_chunks(filename, chunk_count, chunk_size, blob_id):
    chunks = []
    with open(filename, "rb") as binary_file:
        for i in range(0, chunk_count):
            # Seek the ith chunk location and read chunk_size bytes
            binary_file.seek(i*chunk_size)
            payload = binary_file.read(chunk_size)

            # Create the corresponding chunk
            chunk = binary_data_pb2.Chunk(blob_id=blob_id, index=i,
                                          payload=payload)

            # Add it to the chunk array
            chunks.append(chunk)
    return chunks


def save_blob_info(filename, blob_info):
    data = read_db(filename)
    blob_id = str(blob_info.id.id)
    data[blob_id] = MessageToJson(blob_info)
    write_db(filename, data)


def delete_blob_info(filename, blob_id):
    try:
        file_server.remove_by_key_db(filename, str(blob_id.id))
    except KeyError:
        # Blob is non existant
        pass


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
            total += im.getpixel((i, j))[0]

    mean = total // (width * height)
    return mean


def bytes_to_int(bytes):
    return int.from_bytes(bytes, byteorder='big', signed=False)


def int_to_bytes(i):
    return i.to_bytes(1, byteorder='big', signed=False)


def upload_image(image_filename, stub, database_filename):
    blob_spec = create_blob_spec(image_filename)
    creation_response = _create_blob(stub, database_filename, blob_spec)
    if creation_response.error.has_occured:
        return binary_data_pb2.Response(error=creation_response.error)

    blob_info = creation_response.blob_info
    blob_id = blob_info.id
    blob_spec = blob_info.spec
    chunk_count = blob_spec.chunk_count
    chunk_size = get_chunk_size(blob_spec)

    # Create chunks
    chunks = create_chunks(image_filename, chunk_count, chunk_size, blob_id)

    # Save chunks to the server
    for i in range(0, chunk_count):
        chunk = chunks[i]
        upload_response = stub.Save(chunk)

        if upload_response.error.has_occured:
            return binary_data_pb2.Response(error=upload_response.error)


    return binary_data_pb2.Response(error=creation_response.error, blob_info=blob_info)


def _create_blob(stub, filename, blob_spec):
    response = stub.ValidateFileServer(blob_spec)
    error = response.error

    if error.has_occured:
        return binary_data_pb2.Response(error=error)
    else:
        # Create and Save the blob_info to the device
        valid_until = response.valid_until
        id = _generate_blob_id()
        blob_info = binary_data_pb2.BlobInfo(id=id,
                                             valid_until=valid_until,
                                             spec=blob_spec)
        save_blob_info(filename, blob_info)
        return binary_data_pb2.Response(blob_info=blob_info)


def _generate_blob_id():
    blob_id = _get_current_blob_id()
    global _COUNTER
    _COUNTER += 1
    return blob_id


def _get_current_blob_id():
    return binary_data_pb2.BlobId(id=_COUNTER)


class UploadServicer(binary_data_pb2_grpc.UploadServicer):
    """Interfaces exported by the server.
    """

    def __init__(self, file_server_stub, database_filename):
        self.stub = file_server_stub
        self._DATABASE_FILENAME = database_filename

    def CreateBlob(self, request, context):
        """Checks if we can create a Blob specified by BlobSpec on the FileServer
        and returns the BlobInfo to access the Blob. Returns an Error if there is
        not enough space.
        """
        blob_spec = request
        return _create_blob(self.stub, self._DATABASE_FILENAME, blob_spec)

    def UploadChunk(self, request, context):
        """Uploads a Chunk to the server and returns the updated ExpirationTime
        Returns an Error if there if it fails for any reason.
        """
        chunk = request
        response = self.stub.Save(chunk)
        return response

    def DeleteBlob(self, request, context):
        """Deletes the Blob associated with BlobId and returns an Error object
        where the has_occured field is set to True if an error occured and False ]
        otherwise.
        """
        try:
            request.id
        except Exception:
            error = binary_data_pb2.Error(has_occured=True, description="Request was not of type BlobId")
        else:
            blob_id = request
            error = self.stub.Delete(blob_id)
            delete_blob_info(self._DATABASE_FILENAME, blob_id)

        return binary_data_pb2.Response(error=error)

    def GetAverageBrightness(self, request, context):
        """Performs a pre-defined analysis on the Blob associated with BlobId. In
        this case it gets the average brightness of an image.
        """
        blob_id = request

        # Get the chunk_count and blob_size
        try:
            blob_info = read_blob_info(self._DATABASE_FILENAME, blob_id)
        except KeyError:
            error = binary_data_pb2.Error(has_occured=True,
                                          description="No blob with that id exists")
            return binary_data_pb2.Response(error=error)

        # Download all chunks associated with the blob_id
        data = []
        chunk_count = blob_info.spec.chunk_count
        for i in range(0, chunk_count):
            chunk_spec = binary_data_pb2.ChunkSpec(blob_id=blob_id, index=i)
            download_response = self.stub.Download(chunk_spec)

            if download_response.error.has_occured:
                return binary_data_pb2.Response(error=download_response.error)

            # Store the payload
            payload = download_response.payload
            data.append(payload)

        # Figure out the correct filename
        image_filename = "images/recreated_image.png"
        try:
            with open(image_filename, "wb") as binary_file:
                binary_file.seek(0)
        except FileNotFoundError:
            image_filename = "../images/recreated_image.png"


        # Write the payload data to a recreated cat image file
        chunk_size = get_chunk_size(blob_info.spec)

        with open(image_filename, "wb") as binary_file:
            for i in range(0, chunk_count):
                payload = data[i]
                # Seek the ith chunk location and read chunk_size bytes
                binary_file.seek(i*chunk_size)
                binary_file.write(payload)

        # Open the image and call average_image_brightness
        im = Image.open(image_filename)

        result = average_image_brightness(im)

        # Convert result to bytes and return it in the payload
        payload = int_to_bytes(result)

        return binary_data_pb2.Response(payload=payload)


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
        try:
            blob_info = read_blob_info(self._DATABASE_FILENAME, blob_id)
        except KeyError:
            error = binary_data_pb2.Error(has_occured=True,
                                          description="No blob with that id was found")
            return binary_data_pb2.Response(error=error)
        return binary_data_pb2.Response(blob_info=blob_info)

    def GetMeasurementData(self, request, context):
        """Performs an Action which generates a Blob on the server. Returns the
        associated BlobInfo, or an Error if something goes wrong. In this case
        the action is to get the measurement data of the device.
        """
        image_filename = 'images/puppy.jpg'

        # Figure out the correct filename
        try:
            with open(image_filename, "wb") as binary_file:
                pass
        except FileNotFoundError:
            image_filename = '../images/puppy.jpg'

        upload_response = upload_image(image_filename, self.stub,
                                                   self._DATABASE_FILENAME)
        return upload_response



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
