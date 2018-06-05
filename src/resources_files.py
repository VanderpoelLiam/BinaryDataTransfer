import json


def read_db(filename):
    with open(filename, 'rb') as fp:
        data = json.load(fp)
    return data


def write_db(filename, data):
    with open(filename, 'w') as fp:
        json.dump(data, fp)


def remove_by_key_db(filename, key):
    data = read_db(filename)
    del data[key]
    write_db(filename, data)


def wipe_json_file(filename):
    data = {}
    with open(filename, 'w') as fp:
        json.dump(data, fp)
