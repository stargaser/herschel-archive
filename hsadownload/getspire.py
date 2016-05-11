
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from hsadownload.access import getHsaFits, getObsUrn, parseContextHdu, fixHerschelHeader
import os
import astropy.io.fits as fits


def downloadSpireMap(ldict, obsid, lev, bandKey, direc='./SpirePhoto/', \
    spgVersion='SPG v13.0.0', overWrite=False):
    normVersion = ''.join(spgVersion.split())
    if bandKey in ldict:
        filename = os.path.join(direc,"%s_SPIRE_%s_%s_%s.fits.gz"%(obsid,lev,bandKey,normVersion))
        hdu = getHsaFits(ldict[bandKey], fname=filename, save=True)
        hdu.close()
        print('downloaded ' + filename)
    else:
        print('did not find %s in %s for %s' %(bandKey, lev, obsid))

def storeSpirePhoto(obsid, spgVersion='SPG v13.0.0', direc='./SpirePhotoScan/'):
    instrument = 'SPIRE'
    normVersion = ''.join(spgVersion.split())
    urn = getObsUrn(obsid,instrument,spgVersion=spgVersion)
    hdulist = getHsaFits(urn)
    cdict = parseContextHdu(hdulist)
    if 'level2_5' in cdict:
        lev = 'L25'
        lhdulist = getHsaFits(cdict['level2_5'])
        ldict = parseContextHdu(lhdulist)
        for bandKey in ['psrcPLW','psrcPMW', 'psrcPSW']:
            if (bandKey in ldict):
                if (obsid == lhdulist[0].header['obsid001']):
                    downloadSpireMap(ldict, obsid, lev, bandKey, direc,
                             spgVersion=spgVersion)
                else:
                    print('skipping %s for %s since obsid001 is %s' % (bandKey, obsid, lhdulist[0].header['obsid001']))
    elif 'level2' in cdict:
        lev = 'L2'
        lhdulist = getHsaFits(cdict['level2'])
        ldict = parseContextHdu(lhdulist)
        for bandKey in ['psrcPLW','psrcPMW', 'psrcPSW']:
            downloadSpireMap(ldict, obsid, lev, bandKey, direc,
                             spgVersion=spgVersion)
    else:
        return(0)
    return(1)

