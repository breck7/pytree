"""
Make a direct mapping between S-expressions and a TN

((word0 word1 ... ) (...child0...) (...child1...) ...)

"""

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
    lines = str_.split(NODE_BREAK)
    return list(get_blocks(lines))


def tn_to_lines(tn, lvl=0):
    lines = []
    for node, *block in tn:
        lines.append(EDGE_CHAR * lvl + WORD_BREAK.join(node))
        lines += tn_to_lines(block, lvl + 1)
    return lines


def tn_to_str(tn, lvl=0):
    return '\n'.join(tn_to_lines(tn))


# to pass the swim test
# x.to_string()
# x.get_n_lines()
# x.as_rows_to_csv() -> may throw errors
# pytree.csv_to_rows(csv_str)
# x.get(0, 0, 0)
# x.set((0, 0, 0), 1, 'aloha')
# reverse: x.get(0, 0, 0).root = x.get(0, 0, 0).root.reverse
# x.get_n_words()
# x.count_word('hello')
# pytree.from_json(json_obj) # dict, array, and str only

# x.to_json()
# x.get_n_nodes()


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
        [],
        [
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
        ],
    ]

    print(example_tree)

    result = list(str_to_tn(example_tree))
    print(result)

    print(str(result) == str(answer))

    print(tn_to_str(result))


if __name__ == '__main__':
    test()
