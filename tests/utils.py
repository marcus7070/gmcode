from typing import List, TextIO, Optional
from pygcode import Line, Word


class GcodeFile:
    """
    Lazily reads a gcode file, with some convienience functions for parsing it.
    """

    def __init__(self, filename: str):
        self.filename = filename
        self._lines: Optional[List[Line]] = None

    @property
    def lines(self) -> List[Line]:
        """
        Lazy function for getting Line objects.
        """
        if self._lines is None:
            with open(self.filename) as f0:
                self._lines = [Line(s) for s in f0.readlines()]

        return self._lines

    def __len__(self) -> int:
        return len(self.lines)

    def __getitem__(self, position: int) -> Line:
        return self.lines[position]

    def normalise(self, gcode: str) -> str:
        return str(Line(gcode).gcodes[0].word)

    def contains_gcode(self, gcode: str) -> bool:
        """
        Normalises gcode argument and returns True if it appears anywhere in
        the file.
        """
        return self.normalise(gcode) in self.gcodes()

    def line_contains_gcode(self, idx: int, gcode: str) -> bool:
        """
        Normalises gcode argument and returns True if it appears on line number
        idx.
        """
        return self.normalise(gcode) in [str(g0.word) for g0 in self.lines[idx].gcodes]

    def line_contains_word(self, idx: int, word: str) -> bool:
        """
        Normalises word argument and returns True if it appears on line number
        idx.
        """
        return Word(word) in self.lines[idx].block.words

    def count_gcode(self, gcode: str) -> int:
        """
        Normalises gcode argument and returns the number of times it appears in
        the file.
        """
        n0 = self.normalise(gcode)
        return sum([n0 == g0 for g0 in self.gcodes()])

    def gcodes(self) -> List[str]:
        """
        Returns the normalised gcodes in the file.
        """
        out = []
        for l0 in self.lines:
            for g0 in l0.gcodes:
                out.append(str(g0.word))
        return out
