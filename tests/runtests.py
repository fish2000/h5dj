#!/usr/bin/env python
# encoding: utf-8
"""
Run this file to test `signalqueue` -- 
You'll want to have `nose` and `django-nose` installed.

"""
def main():
    import test_settings
    
    logging_format = '--logging-format="%(asctime)s %(levelname)-8s %(name)s:%(lineno)03d:%(funcName)s %(message)s"'
    test_settings.__dict__.update({
        "NOSE_ARGS": [
            '--rednose', '--nocapture', '--nologcapture', '-v',
            logging_format] })
    
    from django.conf import settings
    settings.configure(**test_settings.__dict__)
    import logging.config
    logging.config.dictConfig(settings.LOGGING)
    
    from django.core.management import call_command
    call_command('test', 'tests.h5dj_tests.tests',
        interactive=False, traceback=True, verbosity=2)
    
    import shutil
    tempdata = settings.tempdata
    print "Deleting test data: %s" % tempdata
    shutil.rmtree(tempdata)
    
    import sys
    sys.exit(0)

if __name__ == '__main__':
    main()