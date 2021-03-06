import json

import numpy as np


def split_string(string, max_length=2000):
    split_val = string.split()
    return split_val[:min(max_length, len(split_val))]


def split_json_string(string, max_length=8000):
    split_val = ' '.join(json.loads(string)).split()
    return split_val[:min(max_length, len(split_val))]


def split_json(string, max_length=10):
    split_val = json.loads(string)
    return split_val[:min(max_length, len(split_val))]


def remove_field(*args, **kwargs):
    return 0


def process_labels(string):
    """
    Returns the label string as a list of integers
    :param string:
    :return:
    """
    return [float(x) for x in string]


def get_padded_matrix(unpadded_matrix, mflimit, mllimit):
    """
    Returns a zero-padded matrix for a given jagged list
    :param unpadded_matrix: jagged list to be padded
    :return: zero-padded matrix
    """

    max_files = min(mflimit, max(len(x) for x in unpadded_matrix))
    max_lines = min(mllimit, max(max(len(x) for x in y) for y in unpadded_matrix))
    padded_matrix = np.zeros(
        [len(unpadded_matrix),
         max_files,
         max_lines,
         len(unpadded_matrix[0][0][0])]
     )

    for i0 in range(len(unpadded_matrix)):
        for i1 in range(len(unpadded_matrix[i0])):
            for i2 in range(len(unpadded_matrix[i0][i1])):
                padded_matrix[i0][i1][i2] = unpadded_matrix[i0][i1][i2]

    return padded_matrix

