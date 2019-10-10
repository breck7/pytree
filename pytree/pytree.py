import re
import json
from typing import List

datasets = {}
datasets["iris"] = """sepal_length,sepal_width,petal_length,petal_width,species
6.1,3,4.9,1.8,virginica
5.6,2.7,4.2,1.3,versicolor
5.6,2.8,4.9,2,virginica
6.2,2.8,4.8,1.8,virginica
7.7,3.8,6.7,2.2,virginica
5.3,3.7,1.5,0.2,setosa
6.2,3.4,5.4,2.3,virginica
4.9,2.5,4.5,1.7,virginica
5.1,3.5,1.4,0.2,setosa
5,3.4,1.5,0.2,setosa"""

# TODO: xi -> edge_break
# TODO: yi -> node_break
# TODO: zi -> word_break
# TODO: finish converting from camelCase to snake_case


class ImmutablePytree():

    def __init__(self, children=None, line="", parent=None):
        self._parent = parent
        self._set_line(line)
        self._set_children(children)

    def _set_line(self, line=""):
        self._line = line
        if hasattr(self, "_words"):
            del (self._words)
        return self

    def get_zi(self):
        return " "

    def get_line(self, language=None):
        language = language or self
        return language.get_zi().join(self.get_words())

    def _get_line(self):
        return self._line

    def get_parent(self):
        return self._parent

    def _get_word(self, starts_from):
        if not hasattr(self, "_words"):
            self._words = self._get_line().split(self.get_zi())
        return self._words[starts_from:] if starts_from else self._words

    def get_words(self):
        return self._get_word(0)

    def clone(self):
        return type(self)(self.children_to_string(), self.get_line())

    def _clear_children(self):
        if hasattr(self, "_children"):
            del (self._children)

    def _set_line_and_children(self, line, children, index=None):
        if index is None:
            index = len(self)
        parse_class = self.parse_node_type(line)
        parsed_node = parse_class(children, line, self)
        adjusted_index = len(self) + index if index < 0 else index

        self._get_children_array().insert(adjusted_index, parsed_node)

        # t
        if self._has_index():
            self._make_index(adjusted_index)
        return parsed_node

    def get_keyword(self):
        return self.get_words()[0]

    def _has_index(self):
        return hasattr(self, "_index")

    def _make_index(self, start_at=0):
        if not self._has_index() or start_at == 0:
            self._index = {}
        nodes = self._get_children()
        length = len(nodes)

        for index in range(start_at, length):
            self._index[nodes[index].get_keyword()] = index

    def _set_children(self, content, circular_check_array=None):
        self._clear_children()
        if not content:
            return self

        # set from string
        if type(content) == str:
            return self._parse_string(content)

        # set from tree object
        if type(content) == Pytree:
            me = self
            for node in content._get_children():
                me._set_line_and_children(node.get_line(), node.children_to_string())
            return self

        # If we set from object, create an array of inserted objects to avoid circular loops
        if not circular_check_array:
            circular_check_array = [content]

        return self._set_from_object(content, circular_check_array)

    def _set_from_object(self, content, circular_check_array):
        for keyword in content:
            # filter out methods?
            self._append_from_object_tuple(keyword, content[keyword], circular_check_array)
        return self

    def _text_to_content_and_children_tuple(self, text):
        lines = text.split(self.get_yi_regex())
        first_line = lines.pop(0)
        xi = self.get_xi()
        if not len(lines):
            return [first_line, None]

        lines = list(map(lambda line: line if line[0:1] == xi else xi + line, lines))
        lines = list(map(lambda line: line[1:], lines))
        children = self.get_yi().join(lines)

        return [first_line, children]

    def _append_from_object_tuple(self, keyword, content, circular_check_array):
        line = ""
        xi = self.get_xi()
        children = None
        if content is None:
            line = keyword + xi + "None"
        elif content == "":
            line = keyword
        elif type(content) == str:
            the_tuple = self._text_to_content_and_children_tuple(content)
            line = keyword + xi + the_tuple[0]
            children = the_tuple[1]
        elif type(content) == Pytree:
            line = keyword
            children = Pytree(content.children_to_string(), content.get_line())
        elif type(content) in [int, float, complex, bool, bytes]:
            line = keyword + xi + str(content)
        elif content not in circular_check_array:
            circular_check_array.append(content)
            line = keyword
            if len(content):
                children = Pytree()._set_children(content, circular_check_array)
        else:
            # iirc self.is return early from circular
            return
        self._set_line_and_children(line, children)

    def get_yi_regex(self):
        # todo: return RegExp(self.getYI(), "g")
        return self.get_yi()

    def _get_indent_count(self, str_):
        level = 0
        edge_char = self.get_xi()
        length = len(str_)
        while level < length and str_[level] == edge_char:
            level += 1
        return level

    def _parse_string(self, str_):
        if not str_:
            return self
        lines = str_.split(self.get_yi_regex())
        parent_stack = []
        current_indent_count = -1
        last_node = self
        for line in lines:
            indent_count = self._get_indent_count(line)
            if indent_count > current_indent_count:
                current_indent_count += 1
                parent_stack.append(last_node)
            elif indent_count < current_indent_count:
                # pop things off stack
                while indent_count < current_indent_count:
                    parent_stack.pop()
                    current_indent_count -= 1

            line_content = line[current_indent_count:]
            parent = parent_stack[len(parent_stack) - 1]
            parse_class = parent.parseNodeType(line_content)
            last_node = parse_class(None, line_content, parent)
            parent._get_children_array().append(last_node)
        return self

    def parse_node_type(self, line_content):
        return Pytree

    def get_xi(self):
        return " "

    def get_yi(self):
        return "\n"

    def __len__(self):
        return len(self._get_children())

    def _children_to_string(self, indent_count=0, language=None):
        language = language or self
        res = map(lambda node: node.toString(indent_count, language), self._get_children())
        return language.getYI().join(res)

    def children_to_string(self):
        return self._children_to_string()

    def _get_children(self):
        return self._get_children_array()

    def _get_children_array(self):
        if not hasattr(self, "_children"):
            self._children = []
        return self._children

    def __getitem__(self, position):
        return self._get_children()[position]

    def append_line_and_children(self, line, children):
        return self._set_line_and_children(line, children)

    def has(self, keyword):
        return self._has_keyword(keyword)

    def __contains__(self, keyword):
        return self.has(keyword)

    def _get_index(self):
        # StringMap<int> {keyword: index}
        # When there are multiple tails with the same keyword, _index stores the last content.
        if not self._has_index():
            self._make_index()
        return self._index

    def _has_keyword(self, keyword):
        return keyword in self._get_index()

    def get(self, keyword_path):
        node = self._get_node_by_path(keyword_path)
        return None if node is None else node.getContent()

    def get_node(self, keyword_path):
        return self._get_node_by_path(keyword_path)

    def get_content(self):
        words = self.get_words_from(1)
        return self.get_zi().join(words) if len(words) else None

    def index_of_last(self, keyword):
        if keyword in self._get_index():
            return self._get_index()[keyword]
        return -1

    def _get_node_by_path(self, keyword_path):
        xi = self.get_xi()
        if not keyword_path.count(xi):
            index = self.index_of_last(keyword_path)
            return None if index == -1 else self[index]

        parts = keyword_path.split(xi)
        current = parts.pop(0)
        current_node = self[self.index_of_last(current)]
        return current_node._get_node_by_path(xi.join(parts)) if current_node else None

    def push_content_and_children(self, content, children):
        index = len(self)

        while self.has(str(index)):
            index += 1

        line = str(index) + ("" if content is None else self.get_zi() + content)
        return self.append_line_and_children(line, children)

    def __str__(self):
        return self.to_string()

    def to_string(self, indent_count=0, language=None):
        language = language or self
        if self.is_root():
            return self._children_to_string(indent_count, language)
        content = (self.get_xi() * indent_count) + self.get_line(language)
        value = content + (language.getYI() + self._children_to_string(indent_count + 1, language) if len(self) else "")
        return value

    def is_root(self, relative_to=None):
        return relative_to == self or not self.get_parent()

    def get_words_from(self, start_from):
        return self._get_word(start_from)

    def to_csv(self):
        return self.to_delimited(",")

    def _get_union_names(self):
        if len(self) != 0:
            return []

        obj = {}
        for node in self:
            if not len(node):
                continue
            for child in node:
                obj[child.get_keyword()] = 1
        return obj.keys()

    def to_delimited(self, delimiter, header=None):
        regex = re.compile('(\\n|\\"|\\' + delimiter + ')')

        def cell_fn(string, row, column):
            if regex.match(str(string)):
                return '"' + string.replace('"', '""') + '"'
            else:
                return string

        header = header or self._get_union_names()
        return self._to_delimited(delimiter, header, cell_fn)

    def _to_delimited(self, delimiter, header, cell_fn):
        (head_row, rows) = self._to_arrays(header, cell_fn)
        return delimiter.join(head_row) + "\n" + "\n".join(map(lambda row: delimiter.join(row), rows))

    def __bool__(self):
        return len(self) > 0 or len(self.get_line()) > 0

    def _to_arrays(self, header, cell_fn):
        skip_header_row = 1
        header_array = []
        for index, columnName in enumerate(header):
            header_array.append(cell_fn(columnName, 0, index))
        rows = []
        for row_number, node in enumerate(self):
            vals = []
            for column_index, columnName in enumerate(header):
                child_node = node.getNode(columnName)
                content = child_node.getContentWithChildren() if child_node else ""
                vals.append(cell_fn(content, row_number + skip_header_row, column_index))
            rows.append(vals)

        return header_array, rows

    def get_content_with_children(self):
        # todo: deprecate
        content = self.get_content()
        return (content if content else "") + (self.get_yi() + self._children_to_string() if len(self) else "")

    @staticmethod
    def from_csv(str_):
        return Pytree.from_delimited(str_, ",", '"')

    @staticmethod
    def from_json(str_):
        return Pytree(json.parse(str_))

    @staticmethod
    def from_ssv(str_):
        return Pytree.from_delimited(str_, " ", '"')

    @staticmethod
    def from_tsv(str_):
        return Pytree.from_delimited(str_, "\t", '"')

    @staticmethod
    def from_delimited(str_, delimiter, quote_char):
        rows = Pytree._get_escaped_rows(str_, delimiter, quote_char)
        return Pytree._rows_to_tree_node(rows, delimiter, True)

    @staticmethod
    def _get_escaped_rows(str_, delimiter: str, quote_char: str) -> List[List[str]]:
        if str_.count(quote_char):
            return Pytree._str_to_rows(str_, delimiter, quote_char)
        else:
            escaped_rows = []
            for line in str_.split("\n"):
                escaped_rows.append(line.split(delimiter))
            return escaped_rows

    @staticmethod
    def from_delimited_no_headers(str_, delimiter, quote_char):
        rows = Pytree._get_escaped_rows(str_, delimiter, quote_char)
        return Pytree._rows_to_tree_node(rows, delimiter, False)

    @staticmethod
    def _get_header(rows, has_headers):
        number_of_columns = len(rows[0])
        head_row = rows[0] if has_headers else []
        ZI = " "

        if has_headers:
            # Strip any ZIs from column names in the header row.
            # self.makes the mapping not quite 1 to 1 if there are any ZIs in names.
            index = 0
            while index < number_of_columns:
                head_row[index] = head_row[index].replace(ZI, "")
                index += 1
        else:
            # If str has no headers, create them as 0,1,2,3
            index = 0
            while index < number_of_columns:
                head_row.push(str(index))
                index += 1

        return head_row

    # Given an array return a tree
    @staticmethod
    def _rows_to_tree_node(rows, delimiter, has_headers):
        number_of_columns = len(rows[0])
        tree_node = Pytree()
        names = Pytree._get_header(rows, has_headers)

        row_count = len(rows)
        row_index = 1 if has_headers else 0
        while row_index < row_count:
            row_tree = Pytree()
            row = rows[row_index]
            # If the row contains too many columns, shift the extra columns onto the last one.
            # this allows you to not have to escape delimiter characters in the final column.
            if len(row) > number_of_columns:
                row[number_of_columns - 1] = delimiter.join(row[number_of_columns - 1:])
                row = row[0:number_of_columns]
            elif len(row) < number_of_columns:
                # If the row is missing columns add empty columns until it is full.
                # self.allows you to make including delimiters for empty ending columns in each row optional.
                while len(row) < number_of_columns:
                    row.append("")

            obj = {}
            for index, cellValue in enumerate(row):
                obj[names[index]] = cellValue

            tree_node.push_content_and_children(None, obj)
            row_index += 1

        return tree_node

    @staticmethod
    def iris():
        return Pytree.from_csv(datasets["iris"])

    @staticmethod
    def _str_to_rows(str_, delimiter, quote_char, new_line_char="\n"):
        rows = [[]]
        length = len(str_)
        current_cell = ""
        in_quote = str_[0:1] == quote_char
        current_position = 1 if in_quote else 0
        next_char = None
        is_last_char = None
        current_row = 0
        char = None
        is_next_char_a_quote = None

        while current_position < length:
            char = str_[current_position]
            is_last_char = current_position + 1 == length
            next_char = str_[current_position + 1]
            is_next_char_a_quote = next_char == quote_char

            if in_quote:
                if char != quote_char:
                    current_cell += char
                elif is_next_char_a_quote:
                    # Both the current and next char are ", so the " is escaped
                    current_cell += next_char
                    current_position += 1  # Jump 2
                else:
                    # If the current char is a " and the next char is not, it's the end of the quotes
                    in_quote = False
                    if is_last_char:
                        rows[current_row].append(current_cell)

            else:
                if char == delimiter:
                    rows[current_row].append(current_cell)
                    current_cell = ""
                    if is_next_char_a_quote:
                        in_quote = True
                        current_position += 1  # Jump 2
                elif char == new_line_char:
                    rows[current_row].append(current_cell)
                    current_cell = ""
                    current_row += 1
                    if next_char:
                        rows[current_row] = []
                    if is_next_char_a_quote:
                        in_quote = True
                        current_position += 1  # Jump 2
                elif is_last_char:
                    rows[current_row].append(current_cell + char)
                else:
                    current_cell += char
            current_position += 1
        return rows


class Pytree(ImmutablePytree):

    def set(self):
        return 1


epoch0 = """epoch
 id 0
 train_loss 0.32889
 train_f1 0.12164
 valid_loss 0.14605
 valid_f1 0.16386
 time 0 hr 23 min
 best_val_loss 0.14605
 best_val_f1 0.16386"""

if __name__ == '__main__':
    #tree = pytree("hello world this is a test\nit worked\nnest\n it")
    #print(str(tree))
    #    tree = pytree.iris()
    #    print(tree.clone()[0:2])

    tree = Pytree(epoch0)
    #    print(tree[0][1])

    #   print(tree.get("epoch train_loss"))

    tree = Pytree(epoch0)
    print(tree.to_csv())

    tree = Pytree.iris()
    print(tree.to_csv())

    # tree[0:2]
    # assert len(tree) == 10
