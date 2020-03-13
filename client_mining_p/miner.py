import hashlib
import requests

import sys
import os
import json

from time import time


def proof_of_work(block):
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """
    block_string = json.dumps(block, sort_keys=True).encode()
    proof = 0
    
    print("Proof search started...")
    start = time()
    while valid_proof(block_string, proof) is False:
        proof += 1
    end = time()
    print(f"Found viable proof in {end-start}s: {block_string}{proof}")
    return proof


def valid_proof(block_string, proof):
    """
    Validates the Proof:  Does hash(block_string, proof) contain 6
    leading zeroes?  Return true if the proof is valid
    :param block_string: <string> The stringified block to use to
    check in combination with `proof`
    :param proof: <int?> The value that when combined with the
    stringified previous block results in a hash that has the
    correct number of leading zeroes.
    :return: True if the resulting hash is a valid proof, False otherwise
    """
    guess = f"{block_string}{proof}".encode()
    guess_hash = hashlib.sha256(guess).hexdigest()

    return guess_hash[:6] == "000000"


if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    current_work_directory = os.getcwd()
    print(f"current_work_directory: {current_work_directory}")
    abs_work_directory = os.path.abspath(current_work_directory)
    print(f"current_work_directory (full path): {abs_work_directory}")

    filename = "my_id.txt"
    if not os.path.isfile(filename):
        print('It seems file "{}" not exists in directory: "{}"'.format(filename, current_work_directory))
        sys.exit(1)

    f = open(filename, "r")
    id = f.read()
    print("ID is", id)
    f.close()

    # initialize coin count
    coins = 0

    # Run forever until interrupted
    while True:
        r = requests.get(url=node + "/last_block")
        # Handle non-json response
        try:
            data = r.json()
        except TypeError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        print('line 87', data['last_block'])

        # TODO: Get the block from `data` and use it to look for a new proof
        new_proof = proof_of_work(data['last_block'])

        # When found, POST it to the server {"proof": new_proof, "id": id}
        post_data = {"proof": new_proof, "id": id}

        r = requests.post(url=node + "/mine", json=post_data)
        
        try:
            data = r.json()
        except ValueError:
            print('ValueError')
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        # TODO: If the server responds with a 'message' 'New Block Forged'
        # add 1 to the number of coins mined and print it.  Otherwise,
        # print the message from the server.
        if 'New Block Forged' in data['message']:
            coins += 1
            print(f"coins mined: {coins}")
        else:
            print(data['message'])

    print('Mining ended.')
