""" Configured site factory implementation.

$Id$
"""

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.Portal import CMFSite

from registry import _profile_registry as profile_registry
from tool import SetupTool
from utils import _wwwdir

def addConfiguredSiteForm( dispatcher ):

    """ Wrap the PTF in 'dispatcher', including 'profile_registry' in options.
    """
    wrapped = PageTemplateFile( 'siteAddForm', _wwwdir ).__of__( dispatcher )

    return wrapped( profiles=profile_registry.listProfileInfo() )

def addConfiguredSite( dispatcher, site_id, profile_id, RESPONSE=None ):

    """ Add a CMFSite to 'dispatcher', configured according to 'profile_id'.
    """
    site = CMFSite( site_id )
    dispatcher._setObject( site_id, site )
    site = dispatcher._getOb( site_id )

    setup_tool = SetupTool()
    site._setObject( 'portal_setup', setup_tool )
    setup_tool = getToolByName( site, 'portal_setup' )

    profile_info = profile_registry.getProfileInfo( profile_id )
    setup_tool.setProfileDirectory( profile_info[ 'path' ]
                                  , profile_info.get( 'product' )
                                  )

    setup_tool.runAllImportSteps()
    setup_tool.createSnapshot( 'initial_configuration' )

    if RESPONSE is not None:
        RESPONSE.redirect( '%s/manage_main?update_menu=1'
                         % dispatcher.absolute_url() )
