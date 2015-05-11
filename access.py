""" Functions for accessing the Herschel Science Archive """

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import astropy.io.fits as fits
from astropy.io.votable import parse
import urllib, urllib2, shutil, os

def getHsaFits(urn, fname=None, save=False):
    """ Retrieve a product from the Herschel Science Archive 
    
        Parameters:
        -----------
        urn (string) : Uniform Resource Name in the Herschel Science Archive
        fname (string): filename or filepath; if None, a temporary file is used
        save (boolean): if True, don't delete the FITS file that is written to disk
        
        Returns:
        --------
        hdu : an astropy.io.fits HDU object with the product contents
    """
    url = 'http://archives.esac.esa.int/hsa/aio/jsp/product.jsp'
    values = {'URN' : urn }
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    if fname:
        fp = open(fname, 'wb')
    else:
        fp = tempfile.NamedTemporaryFile(prefix="hsa", mode='wb', delete=False)
        fname = fp.name
    shutil.copyfileobj(response, fp)
    fp.close()
    hdu = fits.open(fname)
    if not save:
        os.path.exists(fname) and os.remove(fname)
    return(hdu)
    
def parseContextHdu(hdu):
    """ Parse all the pointers from an HDU for a Herschel Context product
    
    Parameters:
    -----------
    hdu (astropy.io.fits.HDUList) : Header Data Unit List object for the Context product
    
    Returns:
    --------
    cdict (dict) : dictionary of names and URN strings for MapContext, otherwise
        dictionary of numbers and URN strings for ListContext
    """
    cdict = {}
    nfields = hdu['bridges'].header['TFIELDS']
    if (nfields == 2):
        isMap = True
    elif (nfields == 1):
        isMap = False
    else:
        raise ValueError, "Unknown context table number of fields %d" % nfields
    bTable = hdu['bridges'].data
    if isMap:
        for i in range(len(bTable['name'])):
            cdict[bTable['name'][i]] = bTable['urn'][i].replace('urn::','urn:hsa:')
    else:
        for i in range(len(bTable['urn'])):
            cdict[i] = bTable['urn'][i].replace('urn::','urn:hsa:')
    return(cdict)


def getObsUrn(obsid, instrument='PACS', spgVersion='SPG v12.1.0'):
    """ Retrieve the URN string for an observation id from the Herschel Science Archive,
     for a specified spgVersion and instrument.
    
    Parameters:
    -----------
    obsid (long) : integer Observation ID, like 1342186233
    instrument (string) : 'PACS', 'SPIRE' or 'HIFI' (defaults to 'PACS')
    spgVersion (string) : SPG version (defaults to 'SPG v12.1.0')
    
    Returns:
    --------
    urn (string) : Univeral Resource Name in the archive for this product
    """
    url = 'http://archives.esac.esa.int/hsa/aio/jsp/metadata.jsp'
    values = {'RESOURCE_CLASS' : 'PRODUCT', \
              'QUERY' : "(( obsid==%d) and instrument=='%s' and ( creator=='%s'))"%(obsid, instrument, spgVersion), \
              'HCSS_CLASS_TYPE' : 'herschel.ia.obs.ObservationContext', \
              'LIMIT' : 5000, \
              'RETURN_TYPE' : 'VOTABLE' }
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    votable = parse(response, pedantic=False)
    table = votable.get_first_table().to_table()
    table = table[np.where(table['HCSSTrackVersion'] == np.max(table['HCSSTrackVersion']))]
    urn = table['URN'].data[0]
    return(urn)

def fixHerschelHeader(header):
    """ 
    Fix nonstandard use of HIERARCH in a Herschel header.
    
    Parameters:
    -----------
    header: astropy.io.fits.header Header object
    
    Returns:
    --------
    hdr: modified copy of the input header
    """
    hdr = header.copy()
    for keywd, value in hdr.items():
        if (keywd[:4] == 'key.'):
            inkey = keywd[4:]
            if (inkey.upper() != value.upper()):
                try:
                    hdr.rename_keyword(inkey, value)
                except ValueError:
                    pass
    return(hdr)