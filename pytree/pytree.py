#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Main module."""

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

class ImmutablePytree():

    def __init__(self, children=None, line="", parent=None):
        self._parent = parent
        self._setLine(line)
        self._setChildren(children)

    def _setLine(self, line = ""):
        self._line = line
        if hasattr(self, "_words"):
            del(self._words)
        return self

    def getZI(self):
        return " "

    def getLine(self, language = None):
        language = language or self
        return language.getZI().join(self.getWords())

    def _getLine(self):
        return self._line

    def getParent(self):
        return self._parent

    def _getWords(self, startFrom):
        if not hasattr(self, "_words"):
            self._words = self._getLine().split(self.getZI())
        return self._words.slice(startFrom) if startFrom else self._words
  
    def getWords(self):
        return self._getWords(0)

    def clone(self) :
        return type(self)(self.childrenToString(), self.getLine())

    def _clearChildren(self):
        if hasattr(self, "_children"):
            del(self._children)

    def _setLineAndChildren(self, line, children, index = None) :
        if index == None:
            index = len(self)
        parserClass = self.parseNodeType(line)
        parsedNode = parserClass(children, line, self)
        adjustedIndex = len(self) + index if index < 0 else index

        self._getChildrenArray().insert(adjustedIndex, parsedNode)

        # t
        if self._hasIndex():
            self._makeIndex(adjustedIndex)
        return parsedNode

    def getKeyword(self) :
        return self.getWords()[0]

    def _hasIndex(self):
        return hasattr(self, "_index")

    def _makeIndex(self, startAt = 0) :
        if not self._hasIndex() or startAt == 0:
            self._index = {}
        nodes = self._getChildren()
        length = len(nodes)

        for index in range(startAt, length):
          self._index[nodes[index].getKeyword()] = index

    def _setChildren(self, content, circularCheckArray = None) :
        self._clearChildren()
        if not content:
            return self

        # set from string
        if type(content) == str:
            return self._parseString(content)

        # set from tree object
        if type(content) == pytree:
          me = self
          for node in content._getChildren():
            me._setLineAndChildren(node.getLine(), node.childrenToString())
          return self

        # If we set from object, create an array of inserted objects to avoid circular loops
        if not circularCheckArray:
            circularCheckArray = [content]

        return self._setFromObject(content, circularCheckArray)


    def _setFromObject(self, content, circularCheckArray) :
      for keyword in content:
        # filter out methods?
        self._appendFromObjectTuple(keyword, content[keyword], circularCheckArray)
      return self
  
    def _textToContentAndChildrenTuple(self, text) :
      lines = text.split(self.getYIRegex())
      firstLine = lines.pop(-1)
      xi = self.getXI()
      if not len(lines):
          return [firstLine, None]
  
      lines = list(map(lambda line : line if line[0:1] == xi else xi + line, lines))
      lines = list(map(lambda line : line[1:], lines))
      children = self.getYI().join(lines)
  
      return [firstLine, children]

    def _appendFromObjectTuple(self, keyword, content, circularCheckArray) :
     line = ""
     xi = self.getXI()
     children = None
     if content == None:
        line = keyword + xi + "None"
     elif content == "":
        line = keyword
     elif type(content) == str:
       theTuple = self._textToContentAndChildrenTuple(content)
       line = keyword + xi + theTuple[0]
       children = theTuple[1]
     elif type(content) == pytree:
       line = keyword
       children = pytree(content.childrenToString(), content.getLine())
     elif type(content) in [int, float, complex, bool, bytes]:
        line = keyword + xi + str(content)
     elif content not in circularCheckArray:
       circularCheckArray.append(content)
       line = keyword
       if len(content):
         children = pytree()._setChildren(content, circularCheckArray)
     else:
       # iirc self.is return early from circular
       return
     self._setLineAndChildren(line, children)



    def getYIRegex(self) :
        # todo: return RegExp(self.getYI(), "g")
        return self.getYI()

    def _getIndentCount(self, str):
        level = 0
        edgeChar = self.getXI()
        length = len(str)
        while level < length and str[level] == edgeChar:
          level += 1
        return level

    def _parseString(self, str) :
        if not str:
            return self
        lines = str.split(self.getYIRegex())
        parentStack = []
        currentIndentCount = -1
        lastNode = self
        for line in lines:
          indentCount = self._getIndentCount(line)
          if indentCount > currentIndentCount:
            currentIndentCount += 1
            parentStack.append(lastNode)
          elif indentCount < currentIndentCount:
            # pop things off stack
            while indentCount < currentIndentCount:
              parentStack.pop()
              currentIndentCount -= 1
          
          lineContent = line[currentIndentCount:]
          parent = parentStack[len(parentStack) - 1]
          parserClass = parent.parseNodeType(lineContent)
          lastNode = parserClass(None, lineContent, parent)
          parent._getChildrenArray().append(lastNode)
        return self

    def parseNodeType(self, lineContent):
        return pytree

    def getXI(self):
        return " "

    def getYI(self) :
        return "\n"

    def __len__(self):
        return len(self._getChildren())

    def _childrenToString(self, indentCount = 0, language = None):
        language = language or self
        res = map(lambda node : node.toString(indentCount, language), self._getChildren())
        return language.getYI().join(res)

    def childrenToString(self) :
        return self._childrenToString()

    def _getChildren(self):
        return self._getChildrenArray()

    def _getChildrenArray(self) :
        if not hasattr(self, "_children"):
            self._children = []
        return self._children

    def __getitem__(self, position):
        return self._getChildren()[position]

    def appendLineAndChildren(self, line, children) :
        return self._setLineAndChildren(line, children)

    def has(self, keyword) :
        return self._hasKeyword(keyword)

    def __contains__(self, keyword):
        return self.has(keyword)

    def _getIndex(self) :
        # StringMap<int> {keyword: index}
        # When there are multiple tails with the same keyword, _index stores the last content.
        if not self._hasIndex():
            self._makeIndex()
        return self._index

    def _hasKeyword(self, keyword):
        return keyword in self._getIndex()

    def pushContentAndChildren(self, content, children) :
        index = len(self)

        while self.has(str(index)):
          index += 1

        line = str(index) + ("" if content == None else self.getZI() + content)
        return self.appendLineAndChildren(line, children)

    def __str__(self):
        return self.toString()

    def toString(self, indentCount = 0, language = None):
        language = language or self
        if self.isRoot():
            return self._childrenToString(indentCount, language)
        content = (self.getXI() * indentCount) + self.getLine(language)
        value = content + (language.getYI() + self._childrenToString(indentCount + 1, language) if len(self) else "")
        return value
  
    def isRoot(self, relativeTo = None):
        return relativeTo == self or not self.getParent()

    def getWordsFrom(self, startFrom):
        return self._getWords(startFrom)
 
    @staticmethod
    def fromCsv(str):
        return pytree.fromDelimited(str, ",", '"')

    @staticmethod
    def fromJson(str):
        return pytree(JSON.parse(str))

    @staticmethod
    def fromSsv(str):
        return pytree.fromDelimited(str, " ", '"')

    @staticmethod
    def fromTsv(str):
        return pytree.fromDelimited(str, "\t", '"')

    @staticmethod
    def fromDelimited(str, delimiter, quoteChar):
        rows = pytree._getEscapedRows(str, delimiter, quoteChar)
        return pytree._rowsToTreeNode(rows, delimiter, True)

    @staticmethod
    def _getEscapedRows(str, delimiter, quoteChar):
        return pytree._strToRows(str, delimiter, quoteChar) if str.count(quoteChar) else list(map(lambda line: line.split(delimiter), str.split("\n")))

    @staticmethod
    def fromDelimitedNoHeaders(str, delimiter, quoteChar):
        rows = pytree._getEscapedRows(str, delimiter, quoteChar)
        return pytree._rowsToTreeNode(rows, delimiter, false)

    @staticmethod
    def _getHeader(rows, hasHeaders):
      numberOfColumns = len(rows[0])
      headerRow = rows[0] if hasHeaders else []
      ZI = " "

      if hasHeaders:
        # Strip any ZIs from column names in the header row.
        # self.makes the mapping not quite 1 to 1 if there are any ZIs in names.
        index = 0
        while index < numberOfColumns:
          headerRow[index] = headerRow[index].replace(ZI, "")
          index += 1
      else:
        # If str has no headers, create them as 0,1,2,3
        index = 0
        while index < numberOfColumns:
          headerRow.push(str(index))
          index += 1

      return headerRow
  
    # Given an array return a tree
    @staticmethod
    def _rowsToTreeNode(rows, delimiter, hasHeaders):
        numberOfColumns = len(rows[0])
        treeNode = pytree()
        names = pytree._getHeader(rows, hasHeaders)

        rowCount = len(rows)
        rowIndex = 1 if hasHeaders else 0
        while rowIndex < rowCount:
          rowTree = pytree()
          row = rows[rowIndex]
          # If the row contains too many columns, shift the extra columns onto the last one.
          # this allows you to not have to escape delimiter characters in the final column.
          if len(row) > numberOfColumns:
            row[numberOfColumns - 1] = delimiter.join(row.slice[numberOfColumns - 1:])
            row = row.slice[0: numberOfColumns]
          elif len(row) < numberOfColumns:
            # If the row is missing columns add empty columns until it is full.
            # self.allows you to make including delimiters for empty ending columns in each row optional.
            while len(row) < numberOfColumns:
              row.append("")

          obj = {}
          for index, cellValue in enumerate(row):
            obj[names[index]] = cellValue

          treeNode.pushContentAndChildren(None, obj)
          rowIndex += 1

        return treeNode

    @staticmethod
    def iris():
        return pytree.fromCsv(datasets["iris"])

    @staticmethod
    def _strToRows(str, delimiter, quoteChar, newLineChar = "\n"):
        rows = [[]]
        length = len(str)
        currentCell = ""
        inQuote = str[0:1] == quoteChar
        currentPosition = 1 if inQuote else 0
        nextChar = None
        isLastChar = None
        currentRow = 0
        char = None
        isNextCharAQuote = None

        while currentPosition < length:
          char = str[currentPosition]
          isLastChar = currentPosition + 1 == length
          nextChar = str[currentPosition + 1]
          isNextCharAQuote = nextChar == quoteChar

          if inQuote:
            if char != quoteChar:
                currentCell += char
            elif isNextCharAQuote:
              # Both the current and next char are ", so the " is escaped
              currentCell += nextChar
              currentPosition += 1 # Jump 2
            else:
              # If the current char is a " and the next char is not, it's the end of the quotes
              inQuote = false
              if isLastChar:
                rows[currentRow].append(currentCell)
            
          else:
            if char == delimiter:
              rows[currentRow].append(currentCell)
              currentCell = ""
              if isNextCharAQuote:
                inQuote = True
                currentPosition += 1 # Jump 2
            elif char == newLineChar:
              rows[currentRow].append(currentCell)
              currentCell = ""
              currentRow += 1
              if nextChar:
                rows[currentRow] = []
              if isNextCharAQuote:
                inQuote = True
                currentPosition += 1 # Jump 2
            elif isLastChar:
                rows[currentRow].append(currentCell + char)
            else:
                currentCell += char
          currentPosition += 1
        return rows

class pytree(ImmutablePytree):
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
    
    tree = pytree("seed 2")
    assert "seed" in tree
    
    # tree[0:2]
    # assert len(tree) == 10
