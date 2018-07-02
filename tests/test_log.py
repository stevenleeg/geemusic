import sys
import unittest
import json
import uuid
import logging
import warnings

from testfixtures import log_capture
from os import getenv
from geemusic.utils.music import GMusicWrapper

def surpress_warnings():
    PY3 = sys.version_info[0] == 3
    if PY3:
        warnings.filterwarnings(action="ignore",
                                message="unclosed",
                                category=ResourceWarning)
        warnings.filterwarnings(action="ignore",
                                message="deprecated",
                                category=DeprecationWarning)

class GMusicWrapperNoLogUnitTests(unittest.TestCase):
    """ Unit tests of the GMusicWrapper log functionality """

    def setUp(self):
        surpress_warnings()
        self.api = GMusicWrapper(getenv("GOOGLE_EMAIL"), getenv("GOOGLE_PASSWORD"))
    
    def tearDown(self):
        pass

    @log_capture()
    def test_graceful_degradation_of_log(self, capture):
        """ Makes sure logging degrades gracefully """
        
        self.api.log("test")
        capture.check()

class GMusicWrapperLogUnitTests(unittest.TestCase):
    """ Unit tests of the GMusicWrapper log functionality """

    def setUp(self):
        surpress_warnings()
        logger = logging.getLogger()
        self.api = GMusicWrapper(getenv("GOOGLE_EMAIL"), getenv("GOOGLE_PASSWORD"), logger)
    
    def tearDown(self):
        pass

    @log_capture()
    def test_graceful_degradation_of_log(self, capture):
        """ Makes sure logging degrades gracefully """
        self.api.log("test")
        capture.check(('root', 'DEBUG', 'test'),)


if __name__ == '__main__':
    unittest.main()
