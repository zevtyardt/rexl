from lib.decorators import with_argparser
from array import *
import random
import re
import argparse
import copy
import sys
from typing import List, Optional
import logging
from argparse import Namespace
import tabulate
import itertools

logging.basicConfig(format="%(message)s", level=logging.INFO)


class CrosswordGenerator:
    def __init__(self, words: List[str], *, maxloop: Optional[int] = 1, empty_cell: str = " "):
        self.direct = Namespace(up="UP", down="DOWN",
                                left="LEFT", right="RIGHT")

        assert len(words) > 0, "input 'kata' tidak boleh kosong"
        self.words = set(word.upper() for word in words if word and re.match(
            r"^[a-zA-Z]{2,}$", word))

        self.maxloop = maxloop
        self.registered = Namespace(horizontal=[], vertical=[])
        self.empty_cell = empty_cell
        self.nonetype = type(None)
        self.array = self.build_first_array()

    def longest_word(self, *,  delitem: bool = False) -> str:
        longest_word_ = ""
        for word in self.words:
            if len(word) >= len(longest_word_):
                longest_word_ = word
        if delitem and longest_word_:
            self.words.remove(longest_word_)
        return longest_word_

    def build_first_array(self) -> List:
        [
            [' ', ' ', ' ', ' ', 'L', ' '],
            [' ', 'D', 'O', 'L', 'O', 'R'],
            [' ', ' ', ' ', ' ', 'R', ' '],
            [' ', ' ', ' ', ' ', 'E', ' '],
            ['I', 'P', 'S', 'U', 'M', ' '],
        ]
        longest_word = self.longest_word(delitem=True)
        logging.info(f"kata dasar: {longest_word}")
        if random.choice([self.direct.down, self.direct.right]) == self.direct.down:
            self.registered.vertical.append((longest_word, (0, 0)))
            return [[char] for char in longest_word]
        else:
            self.registered.horizontal.append((longest_word, (0, 0)))
            return [[char for char in longest_word]]

    def next_word(self, **kwargs) -> str:
        return self.longest_word(**kwargs)

    def split_text(self, word: str, delimeter: str) -> List[list]:
        def x(y): return delimeter.join(y)

        splited = word.split(delimeter)
        if len(splited) == 2:
            return [splited]
        else:
            n = []
            for i in range(1, len(splited)):
                n.append([x(splited[:i]), x(splited[i:])])
            return n

    def find_position(self, word: str) -> dict:
        dict = {}
        for char in word:
            for col, arr in enumerate(self.array):
                for row, ar in enumerate(arr):
                    if char == ar and (col, row) not in dict.get(char, []):
                        dict.setdefault(char, [])
                        dict[char].append((col, row))
        return dict

    # FIXME
    def check_same_position(self) -> None:
        def parse_pos(x): return (pos for word, pos in x)

        logging.info("\ncek 'vertical'")
        for word, pos in self.registered.vertical:
            logging.info(
                f" {word = }, {pos = }, {pos in parse_pos(self.registered.horizontal) = }")
        logging.info(f"{self.registered.horizontal = }")

    def update_registered_position(self, direction: str, newA: int) -> None:
        for index, (vertical, horizontal) in enumerate(itertools.zip_longest(self.registered.vertical, self.registered.horizontal)):
            if vertical:
                word, (row, col) = vertical
                if direction == "vertical":
                    row += newA
                elif direction == "horizontal":
                    col += newA
                self.registered.vertical[index] = (word, (row, col))
            if horizontal:
                word, (row, col) = horizontal
                if direction == "vertical":
                    row += newA
                elif direction == "horizontal":
                    col += newA
                self.registered.horizontal[index] = (word, (row, col))

    def add_word(self, data: Namespace) -> None:
        row, col = data.location
        word = data.sideA + data.char + data.sideB

        template = Namespace(word=data.sideA + data.char +
                             data.sideB, row=row, col=col, cross=False)
        if data.direction == "vertical":
            self.registered.vertical.append((word, (row - data.newA, col)))
            row += data.newA
            if data.sideA:
                for _ in range(data.newA):
                    self.array.insert(0, [self.empty_cell]
                                      * len(self.array[0]))
                for num in range(1, len(data.sideA) + 1):
                    charA = data.sideA[-num]
                    self.array[row - num][col] = charA
            if data.sideB:
                for _ in range(data.newB):
                    self.array.append([self.empty_cell] * len(self.array[0]))
                for num, charA in enumerate(data.sideB, start=1):
                    self.array[row + num][col] = charA

        elif data.direction == "horizontal":
            self.registered.horizontal.append((word, (row, col - data.newA)))
            col += data.newA
            for n in range(len(self.array)):
                for _ in range(data.newA):
                    self.array[n].insert(0, self.empty_cell)
                for _ in range(data.newB):
                    self.array[n].append(self.empty_cell)
            if data.sideA:
                for num in range(1, len(data.sideA) + 1):
                    charB = data.sideA[-num]
                    self.array[row][col - num] = charB
            if data.sideB:
                for num, charB in enumerate(data.sideB, start=1):
                    self.array[row][col + num] = charB
        self.update_registered_position(data.direction, data.newA)

    def check_lines(self, l: List[int]) -> Optional[bool]:
        return all(l)

    def possible_direction(self, word: str, char: str, location: tuple) -> Optional[str]:
        splited_text = self.split_text(word, char)
        row, col = location

        results = []

        # 1 artinya sel sudah ditempati
        # 0 berarti sebaliknya
        lines = Namespace(
            up=Namespace(left=[], right=[]),
            down=Namespace(left=[], right=[]),
            left=Namespace(up=[], down=[]),
            right=Namespace(up=[], down=[]),
        )

        # mulai mengecek satu persatu
        for sideA, sideB in splited_text:
            local_direct = Namespace(
                up=False, down=False, left=False, right=False)

            # step 1: cek line dan sisi kiri/kanan jika
            logging.debug(f"\n{sideA  = }")
            for num in range(1, len(sideA) + 1):
                if not isinstance(local_direct.up, self.nonetype):
                    if row - num < 0:
                        if not isinstance(local_direct.up, int):
                            local_direct.up = 0
                        local_direct.up += 1
                    else:
                        previous_char = self.array[row - num][col]
                        if previous_char not in (self.empty_cell, sideA[-num]):
                            local_direct.up = None

                if not isinstance(local_direct.left, self.nonetype):
                    if col - num < 0:
                        if not isinstance(local_direct.left, int):
                            local_direct.left = 0
                        local_direct.left += 1
                    else:
                        previous_char = self.array[row][col - num]
                        if previous_char not in (self.empty_cell, sideA[-num]):
                            local_direct.left = None

                if row - num >= 0:
                    lines.up.left.append(
                        (1 if self.array[row - num][col - 1] == self.empty_cell else 0) if col - 1 >= 0 else 1)
                    lines.up.right.append(
                        (1 if self.array[row - num][col + 1] == self.empty_cell else 0) if col + 1 < len(self.array[row]) else 1)
                if col - num >= 0:
                    lines.left.up.append(
                        (1 if self.array[row - 1][col - num] == self.empty_cell else 0) if row - 1 >= 0 else 1)
                    lines.left.down.append(
                        (1 if self.array[row + 1][col - num] == self.empty_cell else 0) if row + 1 < len(self.array) else 1)

            logging.debug(f"{location} = {char}")
            logging.debug(f"{sideB  = }")

            for num, charB in enumerate(sideB, start=1):
                if not isinstance(local_direct.down, self.nonetype):
                    if row + num >= len(self.array):
                        if not isinstance(local_direct.down, int):
                            local_direct.down = 0
                        local_direct.down += 1
                    else:
                        next_char = self.array[row + num][col]
                        if next_char not in (self.empty_cell, charB):
                            local_direct.down = None

                if not isinstance(local_direct.right, self.nonetype):
                    if col + num >= len(self.array[row]):
                        if not isinstance(local_direct.right, int):
                            local_direct.right = 0
                        local_direct.right += 1
                    else:
                        next_char = self.array[row][col + num]
                        if next_char not in (self.empty_cell, charB):
                            local_direct.right = None

                if row + num < len(self.array):
                    lines.down.left.append(
                        (1 if self.array[row + num][col - 1] == self.empty_cell else 0) if col - 1 >= 0 else 1)
                    lines.down.right.append(
                        (1 if self.array[row + num][col + 1] == self.empty_cell else 0) if col + 1 < len(self.array[row]) else 1)
                if col + num < len(self.array[row]):
                    lines.right.up.append(
                        (1 if self.array[row - 1][col + num] == self.empty_cell else 0) if row - 1 >= 0 else 1)
                    lines.right.down.append(
                        (1 if self.array[row + 1][col + num] == self.empty_cell else 0) if row + 1 < len(self.array) else 1)

            logging.debug(f"{lines.up = }")
            logging.debug(f"{lines.left = }")
            logging.debug(f"{lines.down = }")
            logging.debug(f"{lines.right = }")

            # step 2: ubah value
            if local_direct.left is False and col - len(sideA) >= 0:
                local_direct.left = 0
            if local_direct.up is False and row - len(sideA) >= 0:
                local_direct.up = 0
            if local_direct.right is False and col + len(sideB) < len(self.array[row]):
                local_direct.right = 0
            if local_direct.down is False and row + len(sideB) < len(self.array):
                local_direct.down = 0

            # step 3: cek self.array[row][col] sebelum/sesudah harus kosong
            if local_direct.up is not False and row + 1 < len(self.array) and self.array[row + 1][col] != self.empty_cell:
                local_direct.down = None
            if local_direct.down is not False and row > 0 and self.array[row - 1][col] != self.empty_cell:
                local_direct.up = None
            if local_direct.right is not False and col > 0 and self.array[row][col - 1] != self.empty_cell:
                local_direct.left = None
            if local_direct.left is not False and col + 1 < len(self.array[row]) and self.array[row][col + 1] != self.empty_cell:
                local_direct.right = None

            # step 4: cek sel setelah ujung kata harus kosong
            if sideA:
                if isinstance(local_direct.up, int) and row - len(sideA) > 0 and self.array[row - len(sideA) - 1][col] != self.empty_cell:
                    local_direct.up = None
                if isinstance(local_direct.left, int) and col - len(sideA) > 0 and self.array[row][col - len(sideA) - 1] != self.empty_cell:
                    local_direct.left = None
            if sideB:
                if isinstance(local_direct.down, int) and row + len(sideB) + 1 < len(self.array) and self.array[row + len(sideB) + 1][col] != self.empty_cell:
                    local_direct.down = None
                if isinstance(local_direct.right, int) and col + len(sideB) + 1 < len(self.array[row]) and self.array[row][col + len(sideB) + 1] != self.empty_cell:
                    local_direct.right = None

            # XXX: step 5: cek sekitar line
            in_lines = Namespace(
                up=(self.check_lines(lines.up.left) and self.check_lines(lines.up.right)
                    and bool(sideA)) or not bool(sideA),
                down=(self.check_lines(lines.down.left) and self.check_lines(lines.down.right) and bool(
                    sideB)) or not bool(sideB),
                left=(self.check_lines(lines.left.up) and self.check_lines(lines.left.down) and bool(
                    sideA)) or not bool(sideA),
                right=(self.check_lines(lines.right.up) and self.check_lines(lines.right.down) and bool(
                    sideB)) or not bool(sideB)
            )

            logging.debug(f"{in_lines = }")
            logging.debug(f"{local_direct = }")

            # OK: final result
            if (local_direct.left is not False and local_direct.right is not False) and \
               (local_direct.left is not None and local_direct.right is not None) and \
               (local_direct.left or not (local_direct.left and sideA)) and \
               (in_lines.left and in_lines.right) and \
               (local_direct.right or not (local_direct.right and sideB)):
                results.append(Namespace(direction="horizontal", location=location, char=char, sideA=sideA, sideB=sideB,
                                         newA=local_direct.left or 0, newB=local_direct.right or 0))

            if (local_direct.up is not False and local_direct.down is not False) and \
               (local_direct.up is not None and local_direct.down is not None) and \
               (local_direct.up or not (local_direct.up and sideA)) and \
               (in_lines.up and in_lines.down) and \
               (local_direct.down or not (local_direct.down and sideB)):
                results.append(Namespace(direction="vertical", location=location, char=char, sideA=sideA, sideB=sideB,
                                         newA=local_direct.up or 0, newB=local_direct.down or 0))
        if results:
            logging.debug(f"{results = }")
        return results

    def parse_pos(self, word: str, locations: List[tuple]) -> dict:
        logging.debug(f"parsing kata: {word}")
        results = []
        for char, pos in locations.items():
            for po in pos:
                if (data_results := self.possible_direction(word, char, po)):
                    results.extend(data_results)
                    logging.debug(
                        f"\nterdapat {len(data_results)} kemungkinan untuk lokasi {po}\ntotal kemungkinan untuk kata {word!r}: {len(results)}\n")
        return random.choice(results or [None])

    def compute(self, loop=0, added=0) -> None:
        temp = []
        while self.words:
            if logging.getLogger().level == logging.DEBUG:
                self.print_array()

            next_word = self.next_word(delitem=True)
            pos = self.find_position(next_word)
            if (data := self.parse_pos(next_word, pos)):
                added += 1
                row, col = data.location
                if data.direction == "vertical":
                    row += data.newA
                else:
                    col += data.newA
                logging.info(
                    f"menambahkan kata: {next_word!r} arah {data.direction!r} lokasi ({row}, {col}) {len(self.words)} kata tersisa")
                self.add_word(data)
            else:
                logging.info(f"lewati kata: {next_word}")
                temp.append(next_word)
        if temp:
            if loop >= self.maxloop:
                logging.info(
                    f"\n{added} kata berhasil ditambahkan\n{len(temp)} kata tidak dapat ditambahkan {temp}")
                return
            self.words = set(temp)
            self.compute(loop + 1, added)
        else:
            logging.info(f"\n{added} kata berhasil ditambahkan")

    def print_array(self, array: Optional[list] = None) -> None:
        array = array or copy.deepcopy(self.array)
        def green(x): return f"\x1b[92m{x}\x1b[0m"
        headers = list(map(str, range(len(array[0]))))

        f = "{:<%s} " % (len(str(len(array))) + 9)
        f += " ".join("{{:>{}}}".format(len(i)) for i in headers)

        array.insert(0, headers)
        print("\nhasil generate:")
        for num, i in enumerate(array, start=-1):
            if num < 0:
                esc = "\x1b[0m\x1b[92m"
                print("\x1b[92m" + f.format(esc, *i) + "\x1b[0m")
            else:
                print(f.format(f"\x1b[92m{num}\x1b[0m", *i))

        print("\n" +
              tabulate.tabulate(itertools.zip_longest(
                  map(lambda item: f"{item[0]} {item[1]}",
                      self.registered.horizontal),
                  map(lambda item: f"{item[0]} {item[1]}",
                      self.registered.vertical)
              ), headers=[green("MENDATAR"), green("MENURUN")], showindex=list(map(green, range(1, max(len(self.registered.horizontal), len(self.registered.vertical)) + 1))),
                  tablefmt="plain") + "\n"
              )


class Crossword(object):
    parser = argparse.ArgumentParser()
    parser.add_argument("words", metavar="word", nargs="+", help="wordlist")

    @with_argparser(parser)
    def do_crossword__Generator(self, params):
        """CLI crossword generator"""
        c = CrosswordGenerator(params.words)
        try:
            c.compute()
        except KeyboardInterrupt:
            pass
        c.print_array()
