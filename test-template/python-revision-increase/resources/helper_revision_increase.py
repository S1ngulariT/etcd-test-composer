import random, etcd3, string
import numpy as np

# Antithesis SDK
from antithesis.random import (
    random_choice,
    get_random,
)

# Antithesis SDK
from antithesis.assertions import (
    unreachable,
)


def put_request(c, key, value):
    try:
        c.put(key, value)
        return True, None
    except Exception as e:
        return False, e

def get_request(c, key):
    try:
        response, metadata = c.get(key)
        database_value = response.decode('utf-8')
        return True, None, database_value, metadata.response_header.revision
    except Exception as e:
        return False, str(e), None, metadata.response_header.revision

def generate_random_string():
    random_str = []
    for _ in range(8):
        random_str.append(random_choice(list(string.ascii_letters + string.digits)))
    return "".join(random_str)

def connect_to_host():
    host = random_choice(["etcd0", "etcd1", "etcd2"])
    try:
        client = etcd3.client(host=host, port=2379)
        print(f"Client: connected to {host}")
        return client
    except Exception as e:
        # Antithesis Assertion: client should always be able to connect to an etcd host
        unreachable("Client failed to connect to an etcd host", {"host":host, "error":e})
        print(f"Client: failed to connect to {host}. exiting")
        sys.exit(1)
