import csv

import sys
import numpy as np

csv.field_size_limit(sys.maxsize)

class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text_a, text_b=None, label=None):
        """Constructs a InputExample.

        Args:
            guid: Unique id for the example.
            text_a: string. The untokenized text of the first sequence. For single
            sequence tasks, only this sequence must be specified.
            text_b: (Optional) string. The untokenized text of the second sequence.
            Only must be specified for sequence pair tasks.
            label: (Optional) string. The label of the example. This should be
            specified for train and dev examples, but not for test examples.
        """
        self.guid = guid
        self.text_a = text_a
        self.text_b = text_b
        self.label = label


class InputFeatures(object):
    """A single set of features of data."""

    def __init__(self, input_ids, input_mask, segment_ids, label_id):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_id = label_id


class AbstractProcessor(object):
    """Base class for data converters for sequence classification data sets."""

    def get_train_examples(self, data_dir):
        """
        Gets a collection of `InputExample`s for the train set
        :param data_dir:
        :return:
        """
        raise NotImplementedError()

    def get_dev_examples(self, data_dir):
        """
        Gets a collection of `InputExample`s for the dev set
        :param data_dir:
        :return:
        """
        raise NotImplementedError()

    def get_test_examples(self, data_dir):
        """
        Gets a collection of `InputExample`s for the test set
        :param data_dir:
        :return:
        """
        raise NotImplementedError()

    def get_labels(self):
        """
        Gets a list of possible labels in the dataset
        :return:
        """
        raise NotImplementedError()

    @classmethod
    def _read_tsv(cls, input_file, quotechar=None):
        """
        Reads a Tab Separated Values (TSV) file
        :param input_file:
        :param quotechar:
        :return:
        """
        with open(input_file, "r") as f:
            reader = csv.reader(f, delimiter="\t", quotechar=quotechar)
            lines = []
            for line in reader:
                if sys.version_info[0] == 2:
                    line = list(str(cell, 'utf-8') for cell in line)
                lines.append(line)
            return lines


def convert_examples_to_features(examples, max_seq_length, tokenizer,
                                 max_file, max_line, print_examples=False):
    """
    Loads a data file into a list of InputBatch objects
    :param examples:
    :param max_seq_length:
    :param tokenizer:
    :param print_examples:
    :return: a list of InputBatch objects
    """

    features = []
    for (ex_index, example) in enumerate(examples):
        tokens_a = []
        for i0, file in enumerate(example.text_a):
            if i0 >= max_file:
                break
            tokens_a_file = []
            for i1, line in enumerate(file):
                if i1 >= max_line:
                    break
                tokens_a_file.append(tokenizer.tokenize(line))
            tokens_a.append(tokens_a_file)

        tokens_b = None
        if example.text_b:
            tokens_b = [[tokenizer.tokenize(line) for line in file] for file in example.text_b]
            # Modifies `tokens_a` and `tokens_b` in place so that the total
            # length is less than the specified length.
            # Account for [CLS], [SEP], [SEP] with "- 3"
            _truncate_seq_pair(tokens_a, tokens_b, max_seq_length - 3)
        else:
            # Account for [CLS] and [SEP] with "- 2"
            for i0 in range(len(tokens_a)):
               for i1 in range(len(tokens_a[i0])):
                   if len(tokens_a[i0][i1]) > max_seq_length - 2:
                       tokens_a[i0][i1] = tokens_a[i0][i1][:(max_seq_length - 2)]

        # The convention in BERT is:
        # (a) For sequence pairs:
        #  tokens:   [CLS] is this jack ##son ##ville ? [SEP] no it is not . [SEP]
        #  type_ids: 0   0  0    0    0     0       0 0    1  1  1  1   1 1
        # (b) For single sequences:
        #  tokens:   [CLS] the dog is hairy . [SEP]
        #  type_ids: 0   0   0   0  0     0 0
        #
        # Where "type_ids" are used to indicate whether this is the first
        # sequence or the second sequence. The embedding vectors for `type=0` and
        # `type=1` were learned during pre-training and are added to the wordpiece
        # embedding vector (and position vector). This is not *strictly* necessary
        # since the [SEP] token unambigiously separates the sequences, but it makes
        # it easier for the model to learn the concept of sequences.
        #
        # For classification tasks, the first vector (corresponding to [CLS]) is
        # used as as the "sentence vector". Note that this only makes sense because
        # the entire model is fine-tuned.
        tokens = [[["[CLS]"] + line + ["[SEP]"] for line in file] for file in tokens_a]
        segment_ids = [[[0] * len(line) for line in file] for file in tokens]

        if tokens_b:
            tokens += tokens_b + ["[SEP]"]
            segment_ids += [1] * (len(tokens_b) + 1)

        input_ids = tokenizer.convert_tokens_to_hierarchical_ids(tokens)

        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [[[1] * len(ids) for ids in file] for file in input_ids]

        # Zero-pad up to the sequence length.
        padding = [[[0] * (max_seq_length - len(ids)) for ids in file] for file in input_ids]

        for i0 in range(len(input_ids)):
            for i1 in range(len(input_ids[i0])):
                input_ids[i0][i1] += padding[i0][i1]
                input_mask[i0][i1] += padding[i0][i1]
                segment_ids[i0][i1] += padding[i0][i1]

        label_id = [float(x) for x in example.label]

        if print_examples and ex_index < 5:
            print("tokens: %s" % " ".join([str(x) for x in tokens]))
            print("input_ids: %s" % " ".join([str(x) for x in input_ids]))
            print("input_mask: %s" % " ".join([str(x) for x in input_mask]))
            print("segment_ids: %s" % " ".join([str(x) for x in segment_ids]))
            print("label: %s" % example.label)

        features.append(InputFeatures(input_ids=input_ids,
                                      input_mask=input_mask,
                                      segment_ids=segment_ids,
                                      label_id=label_id))
    return features


def _truncate_seq_pair(tokens_a, tokens_b, max_length):
    """
    Truncates a sequence pair in place to the maximum length
    :param tokens_a:
    :param tokens_b:
    :param max_length:
    :return:
    """

    # This is a simple heuristic which will always truncate the longer sequence
    # one token at a time. This makes more sense than truncating an equal percent
    # of tokens from each, since if one sequence is very short then each token
    # that's truncated likely contains more information than a longer sequence.
    while True:
        total_length = len(tokens_a) + len(tokens_b)
        if total_length <= max_length:
            break
        if len(tokens_a) > len(tokens_b):
            tokens_a.pop()
        else:
            tokens_b.pop()
