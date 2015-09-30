
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from access import getHsaFits, getObsUrn, parseContextHdu, fixHerschelHeader
import os


def downloadPacsMap(ldict, obsid, lev, bandKey, direc='./PacsPhoto/', \
    spgVersion='SPG v13.0.0', overWrite=False):
    """
    Download PACS map. Not meant to be called directly but to be called by
    storePacsPhoto.
    
    Parameters:
    -----------
    ldict (dict) : dictionary of level labels and urn strings
    obsid (long int) : observation id
    lev (string) : level being downloaded
    bandKey (string) : key for band being downloaded
    direc (string) : directory in which to store file, defaults to './PacsPhoto/'
    spgVersion (string) : pipeline version, to put in output filename
    overwrite (bool) : overwrite file if it already exists? defaults to False
    """
    normVersion = ''.join(spgVersion.split())
    if bandKey in ldict:
        filename = os.path.join(direc,"%s_PACS_%s_%s_%s.fits.gz"%(obsid,lev,
                    bandKey, normVersion))
        if (os.path.exists(filename) and (overWrite == False)):
            print('file ' + filename + ' already downloaded')
        else:
            hdu = getHsaFits(ldict[bandKey], fname=filename, save=True)
            hdu.close()
            print('downloaded ' + filename)
    else:
        print('did not find %s in %s for %s' %(bandKey, lev, obsid))
        
def storePacsPhoto(obsid, spgVersion='SPG v13.0.0', direc='./PacsPhoto/', blueCheck=True):
    """
    Download and store a PACS map
    
    Parameters:
    -----------
    obsid (long int): observation id
    spgVersion (string) : pipeline version, defaults to 'SPG v13.0.0'
    direc (string) : path to directory for storing files, defaults to './PacsPhoto/'
    blueCheck (boolean) : Check whether to download the blue file even if it does
      not match the obsid001 metadata. Defaults to True (check). Set to False to
      force the download of the blue file
      
    Returns:
    --------
    Returns 0 if no no level3, level2_5 or level2 in observation; otherwise 1
    """
    instrument = 'PACS'
    urn = getObsUrn(obsid,instrument)
    hdulist = getHsaFits(urn)
    cdict = parseContextHdu(hdulist)
    if 'level3' in cdict: 
        lev = 'L3'
        bandKey = 'HPPJSMAPR'
        lhdulist = getHsaFits(cdict['level3'])
        ldict = parseContextHdu(lhdulist)
        if (bandKey in ldict):
            if (obsid == lhdulist[0].header['obsid001']):
                downloadPacsMap(ldict, obsid, lev, bandKey, direc)
            else:
                print('skipping %s for %s since obsid001 is %s' % (bandKey, obsid, lhdulist[0].header['obsid001']))
        bandKey = 'HPPJSMAPB'
        if (bandKey in ldict):
            if ((blueCheck == False) or (obsid == lhdulist[0].header['obsid001'])):
                downloadPacsMap(ldict, obsid, lev, bandKey, direc)
        else: # get Level 2.5
            lev = 'L25'
            lhdulist = getHsaFits(cdict['level2_5'])
            ldict = parseContextHdu(lhdulist)
            if ((blueCheck == False) or (obsid == lhdulist[0].header['obsid001'])):
                downloadPacsMap(ldict, obsid, lev, bandKey, direc)
            else:
                print('skipping %s for %s since obsid001 is %s' % (bandKey, obsid, lhdulist[0].header['obsid001']))
                
    elif 'level2_5' in cdict:
        lev = 'L25'
        lhdulist = getHsaFits(cdict['level2_5'])
        ldict = parseContextHdu(lhdulist)
        for bandKey in ['HPPJSMAPR','HPPJSMAPB']:
            if (bandKey in ldict):
                if (((blueCheck == False) and (bandKey[-1] == 'B')) or (obsid == lhdulist[0].header['obsid001'])):
                    downloadPacsMap(ldict, obsid, lev, bandKey, direc)
                else:
                    print('skipping %s for %s since obsid001 is %s' % (bandKey, obsid, lhdulist[0].header['obsid001']))
    elif 'level2' in cdict:
        lev = 'L2'
        lhdulist = getHsaFits(cdict['level2'])
        ldict = parseContextHdu(lhdulist)
        for bandKey in ['HPPPMAPR','HPPPMAPB']:
            downloadPacsMap(ldict, obsid, lev, bandKey, direc)
    else:
        return(0)
    return(1)
    
def imageContents(fname):
    """
    Return a sequence of (obsid, fname, band) tuples contained in a PACS image.
    Intended for use with Spark's flatMap transformatios.
    
    Parameters:
    -----------
    fname: string containing filename for PACS Level 2, Level 2.5 or Level 3 image
    
    Returns:
    --------
    reslist: Python list of (obsid, fname, band) values
    """
    reslist = []
    header = fixHerschelHeader(fits.getheader(fname))
    for key in header.keys():
        if (key[:5].upper() == 'OBSID'):
            obsid = int(header[key])
            if header['WAVELENGTH'] == 160.0:
                reslist.append((obsid, fname,'red'))
            elif header['WAVELENGTH'] == 70.0:
                reslist.append((obsid, fname, 'blue'))
            elif header['WAVELENGTH'] == 100.0:
                reslist.append((obsid, fname, 'green'))
            else:
                pass
    return(reslist)