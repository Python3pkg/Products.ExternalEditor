import Testing
import Zope
from OFS.Folder import Folder
from unittest import TestCase, TestSuite, makeSuite, main
from Products.CMFCore.FSPythonScript import FSPythonScript
from test_DirectoryView import skin_path_name
from os.path import join
import sys, time
from thread import start_new_thread

script_path = join(skin_path_name,'test1.py')

class FSPythonScriptTests( TestCase ):

    def testGetSize(self):
        # Test get_size returns correct value
        script = FSPythonScript('test1', script_path)
        self.assertEqual(len(script.read()),script.get_size())

    def testInitializationRaceCondition(self):
        # Tries to exercise a former race condition where
        # FSObject._updateFromFS() set self._parsed before the
        # object was really parsed.
        for n in range(10):
            f = Folder()
            script = FSPythonScript('test1', script_path).__of__(f)
            res = []

            def call_script(script=script, res=res):
                try:
                    res.append(script())
                except:
                    res.append('%s: %s' % sys.exc_info()[:2])

            start_new_thread(call_script, ())
            call_script()
            while len(res) < 2:
                time.sleep(0.05)
            self.assertEqual(res, ['test1', 'test1'], res)

def test_suite():
    return TestSuite((
        makeSuite(FSPythonScriptTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')

