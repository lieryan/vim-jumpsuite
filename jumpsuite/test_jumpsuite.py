#!/usr/bin/env python3

import pathlib
from subprocess import run, PIPE
from tempfile import mkdtemp
from unittest import TestCase


TESTREADER_PATH = pathlib.Path(__file__).absolute().with_name('jumpsuite.py')
TEST_DATA_PATH = (pathlib.Path(__file__).parent / 'tests').absolute()


class JumpSuiteTest(TestCase):
    maxDiff = None
    def test_compare_output(self):
        files = list(TEST_DATA_PATH.glob('*.xml'))
        self.assertGreater(len(files), 0)

        for input_file in files:
            with self.subTest(input_file):
                EXTENDED_TEMPDIR = mkdtemp()
                out = run(
                    [
                        'python3',
                        str(TESTREADER_PATH),
                        str(input_file),
                        "--tmpdir", EXTENDED_TEMPDIR,
                    ],
                    stdout=PIPE,
                    stderr=PIPE,
                )
                stdout = out.stdout.decode()
                stderr = out.stderr.decode()

                output_file = input_file.with_suffix('.out')
                if output_file.exists():
                    expected_out = output_file.read_bytes().decode()
                    expected_out = expected_out.format(EXTENDED_TEMPDIR=EXTENDED_TEMPDIR)
                    self.assertEqual(expected_out, stdout, msg=stderr)
                else:
                    self.assertTrue(
                        output_file.exists(),
                        "Expected output file {output_file} missing:\n{output}\n\n{error}".format(
                            output_file=output_file,
                            output=stdout,
                            error=stderr,
                        ),
                    )


if __name__ == '__main__':
    import unittest
    try:
        import xmlrunner
        out = open('test-report.xml', 'wb')
        testRunner = xmlrunner.XMLTestRunner(output=out)
    except ImportError:
        testRunner = None

    unittest.main(testRunner=testRunner)
