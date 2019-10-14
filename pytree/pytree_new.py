"""Make a direct mapping between S-expressions and a TN

((word0 word1 ... ) (...child0...) (...child1...) ...)
"""
import pandas as pd

EDGE_CHAR = ' '
WORD_BREAK = ' '
NODE_BREAK = '\n'


def get_the_first_block(lines):
    if not lines:
        raise ValueError('lines is empty')

    lines_iter = iter(lines)
    block_lines = []
    rest_lines = []

    node = next(lines_iter)

    # keep adding the line with the first edge_char trimmed to the list of
    # block_lines, until we hit a line that does not start with edge_char
    for line in lines_iter:
        if line.startswith(EDGE_CHAR):
            block_lines.append(line[len(EDGE_CHAR):])
        else:
            rest_lines.append(line)
            break

    rest_lines.extend(lines_iter)

    return node, block_lines, rest_lines


def get_blocks(lines):
    rest_lines = lines
    while rest_lines:
        node, block_lines, rest_lines = get_the_first_block(rest_lines)
        blocks = list(get_blocks(block_lines))
        yield [node.split(WORD_BREAK)] + blocks


def str_to_tn(str_):
    """Fully parses str_.

    A full parse might not be necessary. Both blocks and the nodes can be (and
    probably should be) parsed lazily.
    """
    lines = str_.split(NODE_BREAK)
    return list(get_blocks(lines))


def tn_to_lines(tn, lvl=0):
    lines = []
    for node, *blocks in tn:
        lines.append(EDGE_CHAR * lvl + WORD_BREAK.join(node))
        lines += tn_to_lines(blocks, lvl + 1)
    return lines


def to_str(tn):
    return '\n'.join(tn_to_lines(tn))


def count_n_nodes(tn):
    return sum(1 + count_n_nodes(blocks) for _, *blocks in tn)


def get_node_in(tn, indices):
    blocks = tn
    for index in indices:
        node, *blocks = blocks[index]
    return node


def reverse(tn):
    """Reverse the root level.

    I don't think reversing the entire TN recursively is practically useful.
    Even if it were, one could easily implement it.
    """
    return reversed(tn)


def count_n_words(tn):
    return sum(len(node) + count_n_words(blocks) for node, *blocks in tn)


def tn_to_dict(tn):
    """Turns a type of TN into a dict.

    Example:

    foo 1
    bar 2

    gets turned into

    {
      "foo": "1",
      "bar": "2",
    }

    """
    d = {}
    for node, *_ in tn:
        k, *v = node
        d[k] = WORD_BREAK.join(v)
    return d


def records_to_df(tn):
    records = []
    for index, *record_tn in tn:
        records.append(tn_to_dict(record_tn))

    return pd.DataFrame.from_records(records)


def records_to_csv(tn, index=False):
    return records_to_df(tn).to_csv(index=index)


# to pass the swim test
# x.to_string()
# x.count_n_nodes()
# x.get_n_words()
# x.get(0, 0, 0)
# x.set((0, 0, 0), 1, 'aloha')
# reverse: x.get(0, 0, 0).root = x.get(0, 0, 0).root.reverse
# x.count_word('hello')
# pytree.from_json(json_obj) # dict, array, and str only
# pytree.csv_to_rows(csv_str)
# x.as_rows_to_csv() -> may throw errors

# x.to_json()
# x.count_n_nodes()


def test():
    example_tree = """\
a b
 c d
  e
  f
g
   h
   i
   j"""

    answer = [
        [
            ['a', 'b'],
            [
                ['c', 'd'],
                [
                    ['e'],
                ],
                [
                    ['f'],
                ],
            ],
        ],
        [
            ['g'],
            [
                ['', '', 'h'],
                [
                    ['', 'i'],
                    [
                        ['j'],
                    ],
                ],
            ],
        ],
    ]

    print(example_tree)

    result = list(str_to_tn(example_tree))
    print(result)

    print(str(result) == str(answer))

    print(to_str(result))
    print(count_n_nodes(answer))  # 8
    print(count_n_words(answer))  # 13
    print(get_node_in(answer, [0, 0, 1]))
    tn2_str = """\
0
 foo 1
 bar 2
1
 foo 41
 bar 42
2
 x 12"""
    tn2 = str_to_tn(tn2_str)
    print(tn2)
    print(records_to_csv(tn2))


if __name__ == '__main__':
    test()
