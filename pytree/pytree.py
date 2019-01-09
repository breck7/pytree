# -*- coding: utf-8 -*-

"""Main module."""

class pytree:

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

    def _clearChildren(self):
        if hasattr(self, "_children"):
            del(self._children)

    def _setLineAndChildren(self, line, children, index = None) :
        if index == None:
            index = len(self)
        parserClass = self.parseNodeType(line)
        parsedNode = parserClass(children, line, self)
        adjustedIndex = len(self) + index if index < 0 else index

        self._getChildrenArray().splice(adjustedIndex, 0, parsedNode)

        # t
        if self._index:
            self._makeIndex(adjustedIndex)
        return parsedNode

    def getKeyword(self) :
        return self.getWords()[0]

    def _makeIndex(self, startAt = 0) :
        if not self._index or not startAt:
            self._index = {}
        nodes = self._getChildren()
        newIndex = self._index
        length = len(nodes)

        for index in range(startAt, length):
          newIndex[nodes[index].getKeyword()] = index

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
          self._setLineAndChildren(content[keyword], children)

        return self

    def getYIRegex(self) :
        # todo: return RegExp(self.getYI(), "g")
        return self.getYI()

    def _getIndentCount(self, str):
        level = 0
        edgeChar = self.getXI()
        while str[level] == edgeChar:
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
 

if __name__ == '__main__':
    # tree = pytree('name John\nage\nfavoriteColors\n blue\n  blue1 1\n  blue2 2\n green\n red 1\n')
    tree = pytree("hello world this is a test\nboom yeah\nnest\n it")

    print(len(tree))
    print(tree.toString())
