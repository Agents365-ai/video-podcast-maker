"""Tests for scripts/cli.py — dispatcher table and schema introspection."""
import argparse
import os

import pytest

# scripts/ is on sys.path via tests/conftest.py
import cli as dispatcher  # noqa: E402


# --- ACTIONS table sanity ---------------------------------------------

def test_every_action_has_required_fields():
    for method, info in dispatcher.ACTIONS.items():
        for key in ('script', 'prepend', 'parser_attr', 'description'):
            assert key in info, f"{method} missing '{key}'"


def test_every_action_script_exists_on_disk():
    scripts_dir = dispatcher.SCRIPTS_DIR
    for method, info in dispatcher.ACTIONS.items():
        path = os.path.join(scripts_dir, info['script'])
        assert os.path.isfile(path), f"{method} → {path} not found"


def test_action_methods_use_dot_separator_or_no_separator():
    for method in dispatcher.ACTIONS:
        # Either a single token (leaf: 'verify', 'prereqs') or 'resource.action'
        assert method.count('.') <= 1, f"{method} has too many dots"


def test_prepend_args_are_lists():
    for method, info in dispatcher.ACTIONS.items():
        assert isinstance(info['prepend'], list), f"{method}.prepend not a list"


# --- parser introspection ---------------------------------------------

def test_introspect_returns_parser_for_generate_tts():
    info = dispatcher.ACTIONS['tts.run']
    parser = dispatcher._try_introspect_parser(info)
    assert isinstance(parser, argparse.ArgumentParser)


def test_introspect_returns_parser_for_learn_design():
    info = dispatcher.ACTIONS['design.list']
    parser = dispatcher._try_introspect_parser(info)
    assert isinstance(parser, argparse.ArgumentParser)


def test_introspect_returns_none_when_parser_attr_is_none():
    # resolve_backend.py is intentionally a one-liner with no argparse —
    # no parser to introspect, so parser_attr stays None
    info = dispatcher.ACTIONS['prefs.backend']
    parser = dispatcher._try_introspect_parser(info)
    assert parser is None


@pytest.mark.parametrize('method', [
    'tts.run', 'tts.validate',
    'verify',
    'align',
    'audit.beats',
    'shorts.gen',
    'design.list', 'design.show', 'design.delete', 'design.add',
    'prereqs',
    'prefs.get',
    'prefs.migrate',
])
def test_introspect_succeeds_for_methods_with_build_parser(method):
    """Every method whose underlying script exposes build_parser/_build_parser
    should yield a parser. This guards against future drift where someone
    flips parser_attr to 'build_parser' but the script never exports it."""
    info = dispatcher.ACTIONS[method]
    parser = dispatcher._try_introspect_parser(info)
    assert isinstance(parser, argparse.ArgumentParser), \
        f"{method} ({info['script']}): parser_attr={info['parser_attr']} but introspection returned None"


# --- params extraction --------------------------------------------------

def test_params_from_generate_tts_parser_includes_input_and_format():
    info = dispatcher.ACTIONS['tts.run']
    parser = dispatcher._try_introspect_parser(info)
    params = dispatcher._params_from_parser(parser)
    assert 'input' in params
    assert 'format' in params  # added by cli_envelope.add_format_arg
    assert params['format']['choices'] == ['auto', 'json', 'prose']
    assert params['input']['default'] == 'podcast.txt'


def test_params_excludes_help_and_internal():
    info = dispatcher.ACTIONS['tts.run']
    parser = dispatcher._try_introspect_parser(info)
    params = dispatcher._params_from_parser(parser)
    assert 'help' not in params
    assert 'forwarded_args' not in params


def test_param_records_have_expected_shape():
    info = dispatcher.ACTIONS['tts.run']
    parser = dispatcher._try_introspect_parser(info)
    params = dispatcher._params_from_parser(parser)
    for name, rec in params.items():
        assert set(rec.keys()) == {'type', 'required', 'default', 'choices',
                                    'help', 'flag', 'positional'}


# --- type mapping -----------------------------------------------------

@pytest.mark.parametrize('py_type, expected_name', [
    (int, 'integer'),
    (float, 'number'),
    (bool, 'boolean'),
    (str, 'string'),
    (None, 'string'),
])
def test_type_name_mapping(py_type, expected_name):
    assert dispatcher._type_name(py_type) == expected_name


# --- top-level parser -------------------------------------------------

def test_top_level_parser_lists_all_resources():
    parser = dispatcher.build_parser()
    # Find the resource subparser
    resource_action = next(a for a in parser._actions
                            if isinstance(a, argparse._SubParsersAction))
    expected = {'tts', 'audit', 'shorts', 'design', 'assets', 'prefs', 'verify', 'align', 'prereqs', 'capabilities', 'schema'}
    assert expected == set(resource_action.choices.keys())


def test_resource_subparsers_have_expected_actions():
    parser = dispatcher.build_parser()
    resource_action = next(a for a in parser._actions
                            if isinstance(a, argparse._SubParsersAction))
    tts_parser = resource_action.choices['tts']
    tts_sub = next(a for a in tts_parser._actions
                    if isinstance(a, argparse._SubParsersAction))
    assert {'run', 'validate'} == set(tts_sub.choices.keys())

    design_parser = resource_action.choices['design']
    design_sub = next(a for a in design_parser._actions
                       if isinstance(a, argparse._SubParsersAction))
    assert {'list', 'show', 'delete', 'add'} == set(design_sub.choices.keys())
