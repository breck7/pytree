#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pytree` package."""

import pytest

from click.testing import CliRunner

from pytree import pytree as PyTree
from pytree import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_basic(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    pytree = PyTree.pytree
    tree = pytree("hello world this is a test\nit worked\nnest\n it")
    assert len(tree) == 3
    sample = """name John
age
favoriteColors
 blue
  blue1 1
  blue2 2
 green
 red 1
"""
    tree = pytree(sample)
    assert sample == str(tree)

    di = {"seed": 428, "name" : "joe"}
    tree = pytree(di)
    print(str(tree))
    assert len(tree) == 2

    tree = pytree.iris()
    assert len(tree) == 10


    # Dics can't have dupe keys
    di = {"seed": 428, "sib" : {"frank" : 2}, "name" : "joe", "seed": 12}
    tree = pytree(di)
    assert len(tree) == 3


    tree = pytree.iris()
    i = 0
    for item in tree:
        i += 1
    
    assert i == 10


    tree = pytree("seed 2")
    assert "seed" in tree
    
    tree = pytree.iris()
    assert len(tree.clone()[0:2]) == 2

    tree = pytree(sample)
    assert tree.get("favoriteColors blue blue1") == "1"


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'pytree.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
