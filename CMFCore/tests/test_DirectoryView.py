import Zope
from unittest import TestCase, TestSuite, makeSuite, main

from Products.CMFCore.tests.base.dummy import DummyFolder

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.DirectoryView import DirectoryViewSurrogate
from Products.CMFCore.DirectoryView import _dirreg
from Products.CMFCore.DirectoryView import DirectoryInformation

from Globals import package_home, DevelopmentMode

from os import remove, mkdir, rmdir, curdir, stat
from os.path import join, abspath, dirname
from shutil import copy2
from time import sleep

try:
    __file__
except NameError:
    # Test was called directly, so no __file__ global exists.
    _prefix = abspath(curdir)
else:
    # Test was called by another test.
    _prefix = abspath(dirname(__file__))

# the path of our fake skin
skin_path_name = join(_prefix, 'fake_skins', 'fake_skin')

def _registerDirectory(self=None):
    registerDirectory('fake_skins', _prefix)
    if self is not None:
        ob = self.ob = DummyFolder()
        addDirectoryViews(ob, 'fake_skins', _prefix)
    
def _writeFile(filename, stuff):
    # write some stuff to a file on disk
    # make sure the file's modification time has changed
    thePath = join(skin_path_name,filename)
    try:
        mtime1 = stat(thePath)[8]
    except:
        mtime1 = 0
    mtime2 = mtime1
    while mtime2==mtime1:
        f = open(thePath,'w')
        f.write(stuff)
        f.close()
        mtime2 = stat(thePath)[8]

def _deleteFile(filename):
    # nuke it
    remove(join(skin_path_name,filename))

class DirectoryViewTests1( TestCase ):

    def setUp(self):
        _registerDirectory()
        self.ob = DummyFolder()
        
    def test_registerDirectory( self ):
        """ Test registerDirectory  """
        pass
    
    def test_getDirectoryInfo1( self ):
        """ windows INSTANCE_HOME  """
        addDirectoryViews(self.ob, 'fake_skins', _prefix)
        self.ob.fake_skin.manage_properties(r'Products\CMFCore\tests\fake_skins\fake_skin')        
        self.failUnless(hasattr(self.ob.fake_skin,'test1'))

    def test_getDirectoryInfo2( self ):
        """ windows SOFTWARE_HOME  """
        addDirectoryViews(self.ob, 'fake_skins', _prefix)
        self.ob.fake_skin.manage_properties(r'C:\Zope\2.5.1\Products\CMFCore\tests\fake_skins\fake_skin')        
        self.failUnless(hasattr(self.ob.fake_skin,'test1'))

    def test_getDirectoryInfo3( self ):
        """ *nix INSTANCE_HOME  """
        addDirectoryViews(self.ob, 'fake_skins', _prefix)
        self.ob.fake_skin.manage_properties('Products/CMFCore/tests/fake_skins/fake_skin')        
        self.failUnless(hasattr(self.ob.fake_skin,'test1'))

    def test_getDirectoryInfo4( self ):
        """ *nix SOFTWARE_HOME  """
        addDirectoryViews(self.ob, 'fake_skins', _prefix)
        self.ob.fake_skin.manage_properties('/usr/local/zope/2.5.1/Products/CMFCore/tests/fake_skins/fake_skin')        
        self.failUnless(hasattr(self.ob.fake_skin,'test1'))

class DirectoryViewTests2( TestCase ):

    def setUp( self ):
        _registerDirectory(self)        

    def test_addDirectoryViews( self ):
        """ Test addDirectoryViews  """
        pass

    def test_DirectoryViewExists( self ):
        """
        Check DirectoryView added by addDirectoryViews
        appears as a DirectoryViewSurrogate due
        to Acquisition hackery.
        """
        self.failUnless(isinstance(self.ob.fake_skin,DirectoryViewSurrogate))

    def test_DirectoryViewMethod( self ):
        """ Check if DirectoryView method works """
        self.assertEqual(self.ob.fake_skin.test1(),'test1')

    def test_properties(self):
        """Make sure the directory view is reading properties"""
        self.assertEqual(self.ob.fake_skin.testPT.title, 'Zope Pope')

test1path = join(skin_path_name,'test1.py')
test2path = join(skin_path_name,'test2.py')
test3path = join(skin_path_name,'test3')

if DevelopmentMode:

  class DebugModeTests( TestCase ):

    def setUp( self ):
        
        # initialise skins
        _registerDirectory(self)

        # add a method to the fake skin folder
        _writeFile(test2path, "return 'test2'")

        # edit the test1 method
        copy2(test1path,test1path+'.bak')
        _writeFile(test1path, "return 'new test1'")

        # add a new folder
        mkdir(test3path)
        
    def tearDown( self ):
        
        # undo FS changes
        remove(test1path)
        copy2(test1path+'.bak',test1path)
        remove(test1path+'.bak')
        try:        
            remove(test2path)
        except (IOError,OSError):
            # it might be gone already
            pass
        try:
            rmdir(test3path)
        except (IOError,OSError):
            # it might be gone already
            pass

    def test_AddNewMethod( self ):
        """
        See if a method added to the skin folder can be found
        """
        self.assertEqual(self.ob.fake_skin.test2(),'test2')

    def test_EditMethod( self ):
        """
        See if an edited method exhibits its new behaviour
        """
        self.assertEqual(self.ob.fake_skin.test1(),'new test1')

    def test_NewFolder( self ):
        """
        See if a new folder shows up
        """
        self.failUnless(isinstance(self.ob.fake_skin.test3,DirectoryViewSurrogate))
        self.ob.fake_skin.test3.objectIds()

    def test_DeleteMethod( self ):
        """
        Make sure a deleted method goes away
        """
        remove(test2path)
        try:
            self.ob.fake_skin.test2
        except AttributeError:
            pass
        else:
            self.fail('test2 still exists')

    def test_DeleteAddEditMethod( self ):
        """
        Check that if we delete a method, then add it back,
        then edit it, the DirectoryView notices.

        This excecises yet another Win32 mtime weirdity.
        """
        remove(test2path)
        try:
            self.ob.fake_skin.test2
        except AttributeError:
            pass
        else:
            self.fail('test2 still exists')
            
        # add method back to the fake skin folder
        _writeFile(test2path, "return 'test2.2'")
        
        # we need to wait a second here or the mtime will actually
        # have the same value, no human makes two edits in less
        # than a second ;-)
        sleep(1)
        
        # check
        self.assertEqual(self.ob.fake_skin.test2(),'test2.2')

        # edit method
        _writeFile(test2path, "return 'test2.3'")

        # check
        self.assertEqual(self.ob.fake_skin.test2(),'test2.3')
        
    def test_DeleteFolder( self ):
        """
        Make sure a deleted folder goes away
        """
        rmdir(test3path)
        try:
            self.ob.fake_skin.test3
        except AttributeError:
            pass
        else:
            self.fail('test3 still exists')

else:

    class DebugModeTests( TestCase ):
        pass

def test_suite():
    return TestSuite((
        makeSuite(DirectoryViewTests1),
        makeSuite(DirectoryViewTests2),
        makeSuite(DebugModeTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')




