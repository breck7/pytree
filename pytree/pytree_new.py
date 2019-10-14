"""
Make a direct mapping between S-expressions and a TN

The TN

a b
 c d
   z
e f
 g
 h
 i

is mapped to

(nil
 ((a b)
  ((c d)
   (()
    ((z)))))
 ((e f)
  ((g))
  ((h))
  ((i))))

or in Python

[None,
 [[a, b],
  [[c, d],
   [[],
    [[z]]]]],
 [[e, f],
  [[g]],
  [[h]],
  [[i]]]]
"""

import math
from itertools import takewhile


def get_the_first_block(lines, edge_char):
    rest_lines = iter(lines)
    for i_line, line in enumerate(lines):
        x, y, z = line.partition(edge_char)
        if not x:
            # the line does not start with edge_char
            # implying the block has ended
            break
        else:
            # strip one edge_char from the left of the line
            # and add it to the returning block
            block_lines.append(z)

    return block_lines


def get_tn_from_str(str_, max_lvl=math.inf, node_break='\n', edge_char=' ', word_break=' '):
    lines = str_.split(node_break)
    for line in lines:
        lvl = sum(1 for _ in takewhile(lambda x: x == edge_char, line))


def main():
    x = ArrayTree()


if __name__ == '__main__':
    main()

# type tree
#   .get(0, 0, 0) -> tree
#   .root -> List[str]

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
