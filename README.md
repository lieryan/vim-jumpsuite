# vim-jumpsuite

Jump to "interesting" line of code from your test suite.

jumpsuite parses tracebacks from a JUnit-style XML unittest reports generated
by [unittest-xml-reporting](https://pypi.org/project/unittest-xml-reporting/)
or [pytest](https://github.com/xmlrunner/unittest-xml-reporting), and picks a
few of the "most interesting" line for each failing test to populate the
quickfix list with locations that you will most likely need to go to while
fixing the test.


For example, jumpsuite will turn [this long and tedious traceback](jumpsuite/tests/10.xml):
    
    Traceback (most recent call last):
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/backends/utils.py", line 86, in _execute
        return self.cursor.execute(sql, params)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/backends/sqlite3/base.py", line 396, in execute
        return Database.Cursor.execute(self, query, params)
    sqlite3.IntegrityError: CHECK constraint failed: comments_rating
    
    The above exception was the direct cause of the following exception:
    
    Traceback (most recent call last):
      File "/home/user/Projects/myapp/myapp/comments/tests.py", line 8, in test_adding_comment
        resp1 = self.client.post('/comment/', {'text': 'hello world'})
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/test/client.py", line 526, in post
        response = super().post(path, data=data, content_type=content_type, secure=secure, **extra)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/test/client.py", line 356, in post
        secure=secure, **extra)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/test/client.py", line 421, in generic
        return self.request(**r)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/test/client.py", line 496, in request
        raise exc_value
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/core/handlers/exception.py", line 34, in inner
        response = get_response(request)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/core/handlers/base.py", line 115, in _get_response
        response = self.process_exception_by_middleware(e, request)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/core/handlers/base.py", line 113, in _get_response
        response = wrapped_callback(request, *callback_args, **callback_kwargs)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/views/generic/base.py", line 71, in view
        return self.dispatch(request, *args, **kwargs)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/views/generic/base.py", line 97, in dispatch
        return handler(request, *args, **kwargs)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/views/generic/edit.py", line 172, in post
        return super().post(request, *args, **kwargs)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/views/generic/edit.py", line 142, in post
        return self.form_valid(form)
      File "/home/user/Projects/myapp/myapp/comments/views.py", line 14, in form_valid
        obj.save_rating()
      File "/home/user/Projects/myapp/myapp/comments/models.py", line 12, in save_rating
        return Rating.objects.calculate_rating(self)
      File "/home/user/Projects/myapp/myapp/comments/models.py", line 17, in calculate_rating
        return Rating.objects.create(value=len(comment.text) - 100)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/models/manager.py", line 82, in manager_method
        return getattr(self.get_queryset(), name)(*args, **kwargs)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/models/query.py", line 433, in create
        obj.save(force_insert=True, using=self.db)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/models/base.py", line 746, in save
        force_update=force_update, update_fields=update_fields)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/models/base.py", line 784, in save_base
        force_update, using, update_fields,
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/models/base.py", line 887, in _save_table
        results = self._do_insert(cls._base_manager, using, fields, returning_fields, raw)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/models/base.py", line 926, in _do_insert
        using=using, raw=raw,
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/models/manager.py", line 82, in manager_method
        return getattr(self.get_queryset(), name)(*args, **kwargs)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/models/query.py", line 1204, in _insert
        return query.get_compiler(using=using).execute_sql(returning_fields)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/models/sql/compiler.py", line 1391, in execute_sql
        cursor.execute(sql, params)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/backends/utils.py", line 68, in execute
        return self._execute_with_wrappers(sql, params, many=False, executor=self._execute)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/backends/utils.py", line 77, in _execute_with_wrappers
        return executor(sql, params, many, context)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/backends/utils.py", line 86, in _execute
        return self.cursor.execute(sql, params)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/utils.py", line 90, in __exit__
        raise dj_exc_value.with_traceback(traceback) from exc_value
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/backends/utils.py", line 86, in _execute
        return self.cursor.execute(sql, params)
      File "/home/user/.virtualenvs/myenv/lib/python3.7/site-packages/django/db/backends/sqlite3/base.py", line 396, in execute
        return Database.Cursor.execute(self, query, params)
    django.db.utils.IntegrityError: CHECK constraint failed: comments_rating


into this quickfix jumplist:

    FAILED. Ran 1 tests in 0.028s (errors=1, failures=0, skipped=0)
    /home/user/Projects/myapp/myapp/comments/tests.py:8: test_adding_comment : django.db.utils.IntegrityError: CHECK constraint failed: comments_rating : resp1 = self.client.post('/comment/', {'text': 'hello world'})
    /home/user/Projects/myapp/myapp/comments/views.py:14:`-  form_valid :  : obj.save_rating()
    /home/user/Projects/myapp/myapp/comments/models.py:17:`-  calculate_rating :  : return Rating.objects.create(value=len(comment.text) - 100)


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

    nnoremap <Leader>js :lexpr system('python jumpsuite.py')\|lopen<Enter>


# Configuring your project


## unittest

Install dependency:

    pip install unittest-xml-reporting

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

     pip install unittest-xml-reporting

Add to your settings.py:

    TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
    TEST_OUTPUT_DIR = os.path.join(BASE_DIR, 'test-reports')
    TEST_OUTPUT_FILE_NAME = 'test-report.xml'


# Configuring what jumpsuite filters out

There is a config file to fine tune the traceback lines that vim-jumpsuite 
filters out from the summarized quickfix list. You can use shell/glob pattern
to specify a pattern of file names or function names that jumpsuite should
skip when finding files to jump to. The config file is in:

    ~/.config/jumpsuite/exclude

Example exclude file:

    dont_care_about_this_file.py
    or_this_file.py

    lib/functions.py
       validate
       prevent

    myapp/*.py
        # some comment
        some_function_to_ignore
        another_function

    *
        validate_*

By default, jumpsuite already ignores a number of files that you are unlikely
to be interested to jump to such as third party libraries installed in
site-package.

# Troubleshooting

 1. I use pytest, why is traceback is not parsed correctly?

    Make sure you use --tb=native traceback format, this script does not support
    parsing pytest default traceback format.

 2. Why is the quickfix list not jumpable?

    Check your 'errorformat', reset them to default or add the pattern we depend
    on: 

        set errorformat+=%f:%l:%m
        set errorformat+=%f:%l:%c:%m


# TODO and BUGS

1. 'g:jumpsuite_filename' cannot be changed interactively, currently it must be
   set from .vimrc before the plugin is loaded
2. More languages?
3. More tests. There is some tests, but it's a shame that a plugin to make
   unittest easier doesn't have extensive test coverage.
4. Write vim docs
5. Add ways to disable setting global settings like makeprg.
6. We should have an option to auto-open jumpsuite when vim-test finished
