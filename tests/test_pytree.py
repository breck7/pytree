"""Tests for `pytree` package."""

from click.testing import CliRunner

from pytree import cli
from pytree.pytree import Pytree


def test_basic():
    tree = Pytree("hello world this is a test\nit worked\nnest\n it")
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
    tree = Pytree(sample)
    assert sample == str(tree)

    di = {"seed": 428, "name": "joe"}
    tree = Pytree(di)
    print(str(tree))
    assert len(tree) == 2

    tree = Pytree.iris()
    assert len(tree) == 10

    # Dicts can't have dupe keys
    di = {"seed": 428, "sib": {"frank": 2}, "name": "joe", "seed": 12}  # NOQA
    tree = Pytree(di)
    assert len(tree) == 3

    tree = Pytree.iris()
    i = 0
    for item in tree:
        i += 1

    assert i == 10

    tree = Pytree("seed 2")
    assert "seed" in tree

    tree = Pytree.iris()
    assert len(tree.clone()[0:2]) == 2

    tree = Pytree(sample)
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
