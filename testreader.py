#!/usr/bin/env python

from __future__ import print_function

import os
import re
import sys
from collections import namedtuple, OrderedDict
from itertools import dropwhile
from tempfile import mkdtemp
from xml.etree import ElementTree as ET


SUBTEST_PAT = re.compile(r'^(.*) \[(.*)\]$')
FILE_LINE_PATH = re.compile(r'File "(.*)", line (\d+), in (.+)')

TBLine = namedtuple('TBLine', ['fname', 'lineno', 'name', 'file_line', 'code_line'])


def summarize_testsuites(suites):
    summary = {'errors': int, 'failures': int, 'skipped': int, 'skips': int, 'tests': int, 'time': float}
    attribs = [s.attrib for s in suites]
    for key in summary:
        summary[key] = sum(summary[key](a[key]) for a in attribs if key in a)
    assert not (summary['skipped'] and summary['skips'])
    if summary['skips']:
        summary['skipped'] = summary['skips']
    return summary


def format_summary(summary):
    template = "Ran {tests} tests in {time:.3f}s (errors={errors}, failures={failures}, skipped={skipped})"
    msg = template.format(**summary)
    if summary['errors'] > 0 or summary['failures'] > 0:
        msg = 'FAILED. ' + msg
    return msg


def parse_case(case):
    if case.find('error') is not None:
        detail = case.find('error')
    else:
        detail = case.find('failure')

    if case.attrib['classname']:
        modulename, classname = case.attrib['classname'].rsplit('.', 1)
        abbrev_modulename = '.'.join([p[0] for p in modulename.split('.')])
        abbrev_classname = abbrev_modulename + '.' + classname
        shortname = abbrev_classname + '.' + case.attrib['name']
        fullname = modulename + '.' + classname + '.' + case.attrib['name']
    else:
        shortname = case.attrib['name']
        fullname = case.attrib['name']

    if 'type' in detail:
        template = "{detail[type]}: {detail[message]}"
    else:
        template = "{detail[message]}"
    error = template.format(case=case.attrib, detail=detail.attrib)

    return shortname, fullname, error, detail.text


def get_test_name(case):
    test_name = case.attrib['name']
    subtest_match = SUBTEST_PAT.match(test_name)
    if subtest_match:
        return subtest_match.group(1)
    return test_name


TB_MARKER = "Traceback (most recent call last):"
def main(report_file):
    def format_case(case):
        shortname, fullname, error, detail = parse_case(case)

        interesting_tblines = OrderedDict()
        try:
            lines, error_line, parsed_tb = find_last_traceback(detail, case)
        except StopIteration: # FIXME: use proper exception
            lines = [line[4:] for line in detail.splitlines() if line.startswith('E ')]
            if lines:
                print('\n'.join(lines))
        else:
            test_tbline = extract_test_tbline(error_line, parsed_tb)
            if test_tbline:
                # reserve the spot for test_tbline
                interesting_tblines[test_tbline[0]] = test_tbline

            closest_tbline = extract_closest_tbline(lines)
            if closest_tbline:
                interesting_tblines[closest_tbline[0]] = closest_tbline

            _, parsed_tb, error_line, trailer = parse_traceback(detail.splitlines())
            deepest_tbline = extract_closest_tbline(parsed_tb)
            if deepest_tbline:
                interesting_tblines[deepest_tbline[0]] = deepest_tbline

            if test_tbline:
                # test_tbline takes priority
                interesting_tblines[test_tbline[0]] = test_tbline

        for tbline in interesting_tblines.values():
            print(format_tbline(*tbline))

    def find_last_traceback(detail, case):
        lines = []
        trailer = detail.splitlines()
        while not lines and trailer:
            try:
                _, parsed_tb, error_line, trailer = parse_traceback(trailer)
            except StopIteration:
                if not lines and parsed_tb:
                    lines = list(parsed_tb)
                    break
                raise

            test_name = get_test_name(case)

            lines = list(dropwhile(
                lambda line: test_name != line.name,
                parsed_tb,
            ))
        return lines, error_line, parsed_tb

        #for line in trailer:
        #    if line.strip():
        #        print(line)

        # TODO: set errorformat=%f:%l:%m,%C\ %.%#,%A\ \ File\ \"%f\"\\,\ line\ %l%.%#,%Z%[%^\ ]%\\@=%m

    def format_casestd(case_id, case):
        stderrfile = extract_std('err', case, case_id)
        if stderrfile:
            print("{stderrfile}:0:stderr".format(stderrfile=stderrfile))

        stdoutfile = extract_std('out', case, case_id)
        if stdoutfile:
            print("{stdoutfile}:0:stdout".format(stdoutfile=stdoutfile))

    def extract_std(kind, case, case_id):
        node = case.find('system-{kind}'.format(kind=kind))
        if node is not None:
            filename = os.path.join(stddir, str(case_id) + '.{kind}'.format(kind=kind))
            with open(filename, 'w') as f:
                f.write(node.text)
            return filename

    stddir = mkdtemp(prefix='testreader')

    with open(report_file) as report:
        try:
            report = ET.parse(report)
        except ET.ParseError:
            print('Cannot parse file {}'.format(report_file), file=sys.stderr)
            return -1
        root = report.getroot()
        if root.tag == 'testsuite':
            suites = [root]
        else:
            suites = root.findall('testsuite')
        summary = summarize_testsuites(suites)
        summary_msg = format_summary(summary)
        print(summary_msg)

        for suite in suites:
            for case_id, case in enumerate(suite.findall('testcase')):
                if case.find('error') is not None or case.find('failure') is not None:
                    format_case(case)

                    format_casestd(case_id, case)

        if 'FAILED' in summary_msg:
            return -1


def pair(traceback):
    for line in traceback:
        yield line, next(traceback)


def takeuntil(condition, iterator, immediate_tail=False):
    buff = []
    iterator = iter(iterator)
    def _takeuntil():
        for item in iterator:
            if condition(item):
                yield item
            else:
                buff.append(item)
                break
    def _tail():
        if not buff and not immediate_tail:
            for _ in taker:
                pass
        #yield from buff
        for l in buff: yield l
        #yield from iterator
        for l in iterator: yield l

    taker = _takeuntil()
    return taker, _tail()


def parse_traceback(lines):
    lines = dropwhile(lambda line: TB_MARKER not in line, lines)

    header_line = next(lines)

    traceback, lines = takeuntil(lambda line: line.startswith("  "), lines)
    parsed_tb = []

    def parse_file_line(file_line):
        return FILE_LINE_PATH.search(file_line).groups()

    for file_line, code_line in pair(traceback):
        fname, lineno, name = parse_file_line(file_line)
        parsed_tb.append(TBLine(fname, lineno, name, file_line, code_line.strip()))

    error_line = next(lines).strip()

    # multiple tracebacks?
    trailer = list(lines)

    return header_line, parsed_tb, error_line, trailer


def is_framework_code(tbline):
    framework_paths = ['unittest/case.py', 'django/test/testcases.py', '.virtualenvs', '.pyenv', 'site-packages']
    return any(path in tbline.fname for path in framework_paths) or (tbline.name in ['prevent', 'validate'] and tbline.fname.endswith('lib/functions.py'))

def is_framework_setup(tbline):
    return is_framework_code(tbline)


def extract_test_tbline(error_line, parsed_tb):
    #import pprint, difflib
    #assert lines == parsed_tb, '\n'.join(difflib.unified_diff(pprint.pformat(lines).split('\n'), pprint.pformat(parsed_tb).split('\n')))
    lines = list(dropwhile(is_framework_setup, parsed_tb))
    if lines:
        test_tbline = (lines[0], error_line)
    else:
        test_tbline = (parsed_tb[-1], error_line)
    return test_tbline


def extract_closest_tbline(lines):
    if lines:
        for line in reversed(lines):
            if not is_framework_code(line):
                return (line, "", 1)


def format_tbline(tbline, error_line, level=0):
    indent = {0: '', 1: '`- '}[level]
    template = "{0.fname}:{0.lineno}:{indent} {0.name} : {error_line} : {0.code_line}"
    error_line = re.sub('(\d+)(?=:)', r'\1\\', error_line)
    return template.format(tbline, indent=indent, error_line=error_line)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        filename = "test-reports/test-report.xml"
    status = main(filename)
    if status != 0:
        exit(status)
