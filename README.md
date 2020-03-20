# vim-jumpsuite

Jump to the errors from your test suite.

This script parses python tracebacks in a JUnit-style XML unittest reports and
prints out a quickfix list compatible output that allows you to use the
quickfix list to jump to up to 3 "most interesting location" points for each
failing test.


# Installation

## As vim plugin

Install this repository with your favorite plugin manager.

You have available a command:

    :JumpSuite path/to/junit-xml-report.xml

If XML filename is not provided, it'll use `g:jumpsuite_filename`.

You can map that command to your preferred key mapping.

This plugin will also set makeprg, so if you have vim-dispatch, you can just
run `m<Enter>`.


## Manual integration

Set `'makeprg'` so you can run with `:make`/`:lmake`, or if you have
vim-dispatch, with `m<Enter>`

    set makeprg=python\ /path/to/jumpsuite.py\ /path/to/test-report.xml

Or configure a mapping like so: 

    nnoremap <Leader>js :cexpr system('python jumpsuite.py')\|copen<Enter>

You can also use locationlist:

    nnoremap <Leader>js :lexpr system('python jumpsuite.py')\|copen<Enter>


# Configuring your project


## unittest

Install dependency:

    pip install unittest-xml-runner

Run xmlrunner, for example, from CLI:

    python -m xmlrunner discover --output-file test-report.xml
    
For more configuration options, see unittest-xml-reporting.


## pytest

pytest has native support for XML report, no need to install additional dependency.
Currently, we don't support parsing pytest-style traceback, you have to use
native-style traceback by passing `--tb=native`.

Run pytest with flags:

    pytest --junitxml=test-report.xml --tb=native

Or make it permanent by adding in your pytest.ini

    [pytest]
    addopts=--junitxml=test-report.xml --tb=native


## Django 

Install dependency:

     pip install unittest-xml-runner

Add to your settings.py:

    TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
    TEST_OUTPUT_DIR = os.path.join(BASE_DIR, 'test-reports')
    TEST_OUTPUT_FILE_NAME = 'test-report.xml'


# Troubleshooting

 1. I use pytest, why is traceback is not parsed correctly?

    Make sure you use --tb=native traceback format, this script does not support
    parsing pytest default traceback format.

 2. Why is the quickfix list not jumpable?

    Check your 'errorformat', reset them to default or add the pattern we depend
    on: 

        set errorformat+=%f:%l:%m


# TODO

1. makeprg does not honor 'g:jumpsuite_filename'
2. More languages?
3. More tests. There is some tests, but it's a shame that a plugin to make
   unittest easier doesn't have extensive test coverage.
4. Write vim docs
5. Add ways to disable setting global settings like makeprg.
