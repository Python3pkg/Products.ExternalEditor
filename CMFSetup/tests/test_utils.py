""" CMFSetup.utils unit tests

$Id$
"""

import unittest

def _testFunc( *args, **kw ):

    """ This is a test.

    This is only a test.
    """

_TEST_FUNC_NAME = 'Products.CMFSetup.tests.test_utils._testFunc'

class Whatever:
    pass

_WHATEVER_NAME = 'Products.CMFSetup.tests.test_utils.Whatever'

whatever_inst = Whatever()
whatever_inst.__name__ = 'whatever_inst'

_WHATEVER_INST_NAME = 'Products.CMFSetup.tests.test_utils.whatever_inst'

class UtilsTests( unittest.TestCase ):

    def test__getDottedName_simple( self ):

        from Products.CMFSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( _testFunc ), _TEST_FUNC_NAME )

    def test__getDottedName_string( self ):

        from Products.CMFSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( _TEST_FUNC_NAME ), _TEST_FUNC_NAME )

    def test__getDottedName_unicode( self ):

        from Products.CMFSetup.utils import _getDottedName

        dotted = u'%s' % _TEST_FUNC_NAME
        self.assertEqual( _getDottedName( dotted ), _TEST_FUNC_NAME )
        self.assertEqual( type( _getDottedName( dotted ) ), str )

    def test__getDottedName_class( self ):

        from Products.CMFSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( Whatever ), _WHATEVER_NAME )

    def test__getDottedName_inst( self ):

        from Products.CMFSetup.utils import _getDottedName

        self.assertEqual( _getDottedName( whatever_inst )
                        , _WHATEVER_INST_NAME )

    def test__getDottedName_noname( self ):

        from Products.CMFSetup.utils import _getDottedName

        class Doh:
            pass

        doh = Doh()
        self.assertRaises( ValueError, _getDottedName, doh )

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( UtilsTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
