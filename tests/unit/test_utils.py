# -*- coding: utf-8 -*-
# coding: utf-8
# -----------------------------------------------------------------------------
# Copyright 2012-2017 Andreas Maier. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

"""
All tests for ownmoviedb/utils.py module.
"""

from __future__ import absolute_import, print_function

import pytest

from ownmoviedb.utils import ParseComplexTitle


@pytest.mark.parametrize(
    "complex_title, exp_rv", [
        ("A",
         {"title": "A",
          "year": None,
          "series_title": None,
          "episode_id": None,
          "episode_title": None}),
        ("A (1999)",
         {"title": "A",
          "year": "1999",
          "series_title": None,
          "episode_id": None,
          "episode_title": None}),
        ("A (1999) (2000)",
         {"title": "A (1999)",
          "year": "2000",
          "series_title": None,
          "episode_id": None,
          "episode_title": None}),
        ("A (1999) B",
         {"title": "A B",
          "year": "1999",
          "series_title": None,
          "episode_id": None,
          "episode_title": None}),
        ("A (1999) 2000",
         {"title": "A 2000",
          "year": "1999",
          "series_title": None,
          "episode_id": None,
          "episode_title": None}),
        ("A (199)",
         {"title": "A (199)",
          "year": None,
          "series_title": None,
          "episode_id": None,
          "episode_title": None}),
        ("A (199x)",
         {"title": "A (199x)",
          "year": None,
          "series_title": None,
          "episode_id": None,
          "episode_title": None}),
        ("A (19990)",
         {"title": "A (19990)",
          "year": None,
          "series_title": None,
          "episode_id": None,
          "episode_title": None}),
        ("A - 1 - B",
         {"title": "A - 1 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "1",
          "episode_title": "B"}),
        ("A - 01 - B",
         {"title": "A - 01 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "01",
          "episode_title": "B"}),
        ("A - 001 - B",
         {"title": "A - 001 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "001",
          "episode_title": "B"}),
        ("A - 123 - B",
         {"title": "A - 123 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "123",
          "episode_title": "B"}),
        ("A - 123a - B",
         {"title": "A - 123a - B",
          "year": None,
          "series_title": "A",
          "episode_id": "123a",
          "episode_title": "B"}),
        ("A - 12.13 - B",
         {"title": "A - 12.13 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "12.13",
          "episode_title": "B"}),
        ("A, Folge 12 - B",
         {"title": "A, Folge 12 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "Folge 12",
          "episode_title": "B"}),
        ("12, Folge 13 - 14",
         {"title": "12, Folge 13 - 14",
          "year": None,
          "series_title": "12",
          "episode_id": "Folge 13",
          "episode_title": "14"}),
        ("A, Doppelfolge 12 - B",
         {"title": "A, Doppelfolge 12 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "Doppelfolge 12",
          "episode_title": "B"}),
        ("A, Teil 12 - B",
         {"title": "A, Teil 12 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "Teil 12",
          "episode_title": "B"}),
        ("A, Part 12 - B",
         {"title": "A, Part 12 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "Part 12",
          "episode_title": "B"}),
        ("A, part 12 - B",
         {"title": "A, part 12 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "part 12",
          "episode_title": "B"}),
        ("A, Buch 12 - B",
         {"title": "A, Buch 12 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "Buch 12",
          "episode_title": "B"}),
        ("A, Book 12 - B",
         {"title": "A, Book 12 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "Book 12",
          "episode_title": "B"}),
        ("A, book 12 - B",
         {"title": "A, book 12 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "book 12",
          "episode_title": "B"}),
        ("A, Episode 12 - B",
         {"title": "A, Episode 12 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "Episode 12",
          "episode_title": "B"}),
        ("A, Film 12 - B",
         {"title": "A, Film 12 - B",
          "year": None,
          "series_title": "A",
          "episode_id": "Film 12",
          "episode_title": "B"}),
    ]
)
def test_one_ParseComplexTitle(complex_title, exp_rv):
    """
    Test the ParseComplexTitle() function.
    """

    act_rv = ParseComplexTitle(complex_title)

    assert act_rv["title"] == exp_rv["title"]
    assert act_rv["year"] == exp_rv["year"]
    assert act_rv["series_title"] == exp_rv["series_title"]
    assert act_rv["episode_id"] == exp_rv["episode_id"]
    assert act_rv["episode_title"] == exp_rv["episode_title"]


# TODO: Add testcases for the other functions
