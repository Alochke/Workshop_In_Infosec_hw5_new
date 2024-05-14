#!/usr/bin/env python3

"""
Create a graph from a Guesslang test report.

"""

import argparse
import json
import logging
from pathlib import Path
import shutil
import tempfile
import webbrowser

from guesslang.config import config_logging


LOGGER = logging.getLogger(__name__)

RESOURCES_DIR = Path(__file__).parent.joinpath('resources')
REPORT_DIR_PREFIX = 'guesslang-report-'


def main():
    """Report graph creator command line"""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'reportfile', type=argparse.FileType('r'),
        help="test report file generated by `guesslang --test TESTDIR`")
    parser.add_argument(
        '-d', '--debug', default=False, action='store_true',
        help="show debug messages")

    args = parser.parse_args()
    config_logging(args.debug)

    report = json.load(args.reportfile)
    graph_data = _build_graph(report)
    index_path = _prepare_resources(graph_data)
    webbrowser.open(str(index_path))


def _build_graph(report):
    languages = sorted(report['per-language'])
    groups = _build_groups(report['per-language'])

    return {
        'nodes':  [
            {'name': lang, 'group': groups[lang]} for lang in languages
        ],
        'links': [
            {
                'source': languages.index(lang),
                'target': languages.index(predicted_lang),
                'value': (
                    predicted_files / details['nb-files']
                    if details['nb-files'] else 0),
            }
            for lang, details in report['per-language'].items()
            for predicted_lang, predicted_files in details['predicted'].items()
        ]
    }


def _build_groups(per_language):
    top = {}
    links = {}
    # For each language find the language with which it is the most confused
    for lang, details in per_language.items():
        top[lang] = 1
        links[lang] = None
        for predicted_lang, predicted_files in details['predicted'].items():
            if lang == predicted_lang:
                continue

            if predicted_files > top[lang]:
                top[lang] = predicted_files
                links[lang] = predicted_lang

    # Group the language pairs. For example:
    # - the 3 pairs: (C -> C++), (C++ -> Java), (HTML -> CSS)
    # - are merged into 2 groups: (C, C++, Java), (HTML, CSS)
    bag = [set([lang]) for lang in links]
    for langs in links.items():
        new_bag = []
        lang_group = set()
        for group in bag.copy():
            if any(lang in group for lang in langs):
                lang_group.update(group)
            else:
                new_bag.append(group)
        new_bag.append(lang_group)
        bag = new_bag

    LOGGER.debug("%d languages groups created", len(bag))

    # Assign an ID to each group
    groups = {}
    for pos, group in enumerate(reversed(bag)):
        for lang in group:
            groups[lang] = pos

    return groups


def _prepare_resources(graph_data):
    dirname = tempfile.mkdtemp(prefix=REPORT_DIR_PREFIX)
    for path in RESOURCES_DIR.glob('**/*'):
        shutil.copy(str(path), dirname)

    data_path = Path(dirname).joinpath('data.json')
    try:
        with data_path.open('w') as data_file:
            json.dump(graph_data, data_file, indent=2, sort_keys=True)
    except OSError as error:
        LOGGER.error("Cannot save report graph data: %s", error)
        raise RuntimeError('Failed to save the report graph data')

    index_file = data_path.parent.joinpath('index.html').absolute()
    LOGGER.debug("Report graph available at %s", index_file)
    return index_file


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        LOGGER.critical("Cancelled!")
    except RuntimeError as error:
        LOGGER.critical("Aborted: %s", error)
