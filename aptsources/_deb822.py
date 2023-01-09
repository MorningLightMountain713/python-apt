#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) Canonical Ltd
#
# SPDX-License-Identifier: GPL-2.0+

"""deb822 parser with support for comment headers and footers."""

import io
import collections
import typing

import apt_pkg

T = typing.TypeVar("T")


class Section:
    """A single deb822 section, possibly with comments.

    This represents a single deb822 section.
    """

    def __init__(self, section: str):
        self.header, self.footer = comments = ["", ""]
        in_section = False
        trimmed_section = ""

        for line in section.split("\n"):
            if line.startswith("#"):
                comments[in_section] += line + "\n"
                continue

            in_section = True
            trimmed_section += line + "\n"

        self.tags = collections.OrderedDict(apt_pkg.TagSection(trimmed_section))

    def __getitem__(self, key: str) -> str:
        """Get the value of a field."""
        return self.tags[key]

    def __setitem__(self, key: str, val: str) -> None:
        """Set the value of a field."""
        self.tags[key] = val

    def __bool__(self):
        return bool(self.tags)

    def get(
        self, key: str, default: typing.Optional[T] = None
    ) -> typing.Union[typing.Optional[T], str]:
        try:
            return self.tags[key]
        except KeyError:
            return default

    def __str__(self) -> str:
        """Canonical string rendering of this section."""
        return (
            self.header
            + "".join(f"{k}: {v}\n" for k, v in self.tags.items())
            + self.footer
        )


class File:
    """
    Parse a given file object into a list of Section objects.
    """

    def __init__(self, fobj: io.TextIOBase):
        sections = fobj.read().split("\n\n")
        self.sections = [Section(s) for s in sections]

    def __iter__(self) -> typing.Iterator[Section]:
        return iter(self.sections)

    def __str__(self) -> str:
        return "\n\n".join(str(s) for s in self.sections)


if __name__ == "__main__":

    st = """# Header
# More header
K1: V1
# Inline
K2: V2
 # not a comment
# Footer
# More footer
"""

    s = Section(st)

    print(s)
