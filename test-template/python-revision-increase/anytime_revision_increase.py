#!/usr/bin/env -S python3 -u

# This file serves as a parallel driver (https://antithesis.com/docs/test_templates/test_composer_reference/#parallel-driver). 
# It does between 1 and 100 random kv puts against a random etcd host in the cluster. We then check to see if successful puts persisted
# and are correct on another random etcd host.

# Antithesis SDK
from antithesis.assertions import (
    always,
    sometimes,
)

import sys
sys.path.append("/opt/antithesis/resources")
import helper_revision_increase as helper


def generate_put_request(key):
    """
        This function will first connect to an etcd host, then execute a certain number of put requests. 
        The key and value for each put request are generated using Antithesis randomness (check within the helper.py file). 
        We return the key/value pairs from successful requests.
    """
    
    # Generate random string for key
    value = helper.generate_random_string()

    client = helper.connect_to_host()

    # Response of the put request
    success, error = helper.put_request(client, key, value)

    # Antithesis Assertion: sometimes put requests are successful. A failed request is OK since we expect them to happen.
    sometimes(success, "Client can make successful put requests", {"error":error})

    if not success:
        print(f"Client: unsuccessful put with key '{key}', value '{value}', and error '{error}'")
        return False, value
    
    print(f"Client: successful put with key '{key}' and value '{value}'")
    return True, value
    
    

def get_revision_from_get_request(key, value):
    """
        This function will first connect to an etcd host, then perform a get request on each key in the key/value array. 
        For each successful response, we check that the get request value == value from the key/value array. 
        If we ever find a mismatch, we return it. 
    """
    client = helper.connect_to_host()

    success, error, database_value, revision = helper.get_request(client, key)

    # Antithesis Assertion: sometimes get requests are successful. A failed request is OK since we expect them to happen.
    sometimes(success, "Client can make successful get requests", {"error": error})

    if not success: 
        print(f"Client: unsuccessful get with key '{key}', and error '{error}'")
        return False, -1
    elif value != database_value:
        print(f"Client: a key value mismatch! This shouldn't happen.")
        return False, -1
    
    print(f"Client: successful get with key '{key}', and revision '{revision}'")
    return True, revision


if __name__ == "__main__":
    # The booleans store the success state of a step in this test. They are initialized to False
    first_put_success = False
    first_get_success = False
    second_put_success = False
    second_get_success = False

    # Generate random string for key
    key = helper.generate_random_string()

    first_put_success, original_value = generate_put_request(key)
    if first_put_success:
        first_get_success, first_revision = get_revision_from_get_request(key, original_value)
    if first_get_success:
        second_put_success, updated_value = generate_put_request(key)
    if second_put_success:
        second_get_success, second_revision = get_revision_from_get_request(key, updated_value)

    if second_get_success:
        # Antithesis Assertion: A successful put request will always increase the revision value
        # Note: This assertion should only trigger in the event that both get requests successfully udpate 
        # the KVStore
        always(
            second_revision > first_revision, 
            "Revision number was succesfully updated!", 
            {
                "key": key,
                "first_revision": first_revision,
                "second_revision": second_revision, 
            }
        )