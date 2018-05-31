from datetime import datetime, timedelta
from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp

import grpc
import json
import time
import binary_data_pb2
import binary_data_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_DATABASE_FILENAME = 'binary_data_db.json'


def get_validation(blob_spec):
    flag = has_space(blob_spec.size)
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

def save_blob(filename, blob):
    try:
        write_blob(filename, blob)
        description="Sucessfully stored blob with id %i" % blob.id.id
        error_status = binary_data_pb2.ErrorStatus(wasError=False,
                                                    description=description)
    except Exception as e:
        error_status = binary_data_pb2.ErrorStatus(wasError=True,
                                                    description=str(e))
    return error_status

def download_blob(filename, blob_id):
    """
    Returns None if no blob with the given id is found.
    """
    try:
        payload = read_blob_payload(filename, blob_id)
    except Exception:
        return None

    if payload is None:
        return None
    else:
        return binary_data_pb2.Blob(id=blob_id, payload=payload)

def delete_blob(filename, blob_id):
    try:
        remove_blob(filename, blob_id)
        description="Sucessfully deleted blob with id %i" % blob_id.id
        error_status = binary_data_pb2.ErrorStatus(wasError=False, description=description)
    except Exception as e:
        error_status = binary_data_pb2.ErrorStatus(wasError=True,
                                                    description=str(e))
    return error_status

def remove_blob(filename, blob_id):
    remove_by_key_db(filename, str(blob_id.id))

def write_blob(filename, blob):
    data = read_db(filename)
    payload_as_string = blob.payload.decode("utf-8")
    data[str(blob.id.id)] = payload_as_string
    write_db(filename, data)

def read_blob_payload(filename, blob_id):
    """
    Returns None if no blob with the given id is found.
    """
    try:
        data = read_db(filename)
        payload_as_string = data[str(blob_id.id)]
        payload_as_bytes = payload_as_string.encode("utf-8")
        return payload_as_bytes
    except KeyError:
        return None

def read_db(filename):
    # print("\n" + filename)
    with open(filename) as fp:
        data = json.load(fp)
    return data

def write_db(filename, data):
    with open(filename, 'w') as fp:
        json.dump(data, fp)

def remove_by_key_db(filename, key):
    data = read_db(filename)
    del data[key]
    write_db(filename, data)


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
        status = save_blob(_DATABASE_FILENAME, request)
        return status

    def Delete(self, request, context):
        """request  - BlobId
           response - ErrorStatus
        """
        status = delete_blob(_DATABASE_FILENAME, request)
        return status

    def Download(self, request, context):
        """request  - BlobId
           response - ErrorStatus
        """
        status = download_blob(_DATABASE_FILENAME, request)
        return status


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
