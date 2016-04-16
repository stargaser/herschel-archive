
# coding: utf-8

# ## Four corners of Herschel images

# This function from http://stackoverflow.com/questions/13542855/python-help-to-implement-an-algorithm-to-find-the-minimum-area-rectangle-for-gi
#
# and working code (error in the original) at http://gis.stackexchange.com/questions/22895/how-to-find-the-minimum-area-rectangle-for-given-points/169633#169633
#

# In[1]:

import numpy as np
from scipy.spatial import ConvexHull


def minimum_bounding_rectangle(points):
    """
    Find the smallest bounding rectangle for a set of points.
    Returns a set of points representing the corners of the bounding box.

    :param points: an nx2 matrix of coordinates
    :rval: an 4x2 matrix of coordinates
    """
    from scipy.ndimage.interpolation import rotate
    pi2 = np.pi/2.

    # get the convex hull for the points
    hull_points = points[ConvexHull(points).vertices]

    # calculate edge angles
    edges = np.zeros((len(hull_points)-1, 2))
    edges = hull_points[1:] - hull_points[:-1]

    angles = np.zeros((len(edges)))
    angles = np.arctan2(edges[:, 1], edges[:, 0])

    angles = np.abs(np.mod(angles, pi2))
    #angles = np.unique(angles)

    # find rotation matrices
    # XXX both work
    rotations = np.vstack([
        np.cos(angles),
        np.cos(angles-pi2),
        np.cos(angles+pi2),
        np.cos(angles)]).T
#     rotations = np.vstack([
#         np.cos(angles),
#         -np.sin(angles),
#         np.sin(angles),
#         np.cos(angles)]).T
    rotations = rotations.reshape((-1, 2, 2))

    # apply rotations to the hull
    rot_points = np.dot(rotations, hull_points.T)

    # find the bounding points
    min_x = np.nanmin(rot_points[:, 0], axis=1)
    max_x = np.nanmax(rot_points[:, 0], axis=1)
    min_y = np.nanmin(rot_points[:, 1], axis=1)
    max_y = np.nanmax(rot_points[:, 1], axis=1)

    # find the box with the best area
    areas = (max_x - min_x) * (max_y - min_y)
    best_idx = np.argmin(areas)

    # return the best box
    x1 = max_x[best_idx]
    x2 = min_x[best_idx]
    y1 = max_y[best_idx]
    y2 = min_y[best_idx]
    r = rotations[best_idx]

    rval = np.zeros((4, 2))
    rval[0] = np.dot([x1, y2], r)
    rval[1] = np.dot([x2, y2], r)
    rval[2] = np.dot([x2, y1], r)
    rval[3] = np.dot([x1, y1], r)

    return rval


# In[2]:

from scipy.optimize import OptimizeResult, minimize
from shapely.geometry import Polygon, MultiPoint


# In[3]:

def fun(x, hull):
    coords = x.reshape(4,2)
    p = Polygon(coords)
    area = p.difference(hull).area + hull.difference(p).area
    return(area)


# ## How to find the minimum quadrilateral?

# Online research shows that there isn't such a convenient formula for finding the minimum quadrilateral. We have found the minimum bounding rectangle.
#
# We can try an iterative approach.

# In[20]:

def fourCorners(fname, ext=1):
    """
    Compute the four corners in celestial coordinates

    Parameters:
    -----------
    fname (string): path to FITS image
    ext (int): extension with WCS keywords and image (default 1)

    Returns:
    --------
    corners: 4x2 numpy array of the four corners in (ra, dec) pairs
    """
    import astropy.io.fits as fits
    from astropy.wcs import WCS
    import numpy as np
    hdu = fits.open(fname)
    w = WCS(hdu[ext].header)
    imdata = hdu[1].data
    grid = np.indices(imdata.shape)
    coords = np.vstack([grid[1][np.isfinite(imdata)],grid[0][np.isfinite(imdata)]]).T
    rect = minimum_bounding_rectangle(coords)
    #
    # Use the Scipy hull vertices because shapely's MultiPoint and convex_hull are so slow
    hull_points = coords[ConvexHull(coords).vertices]
    points = MultiPoint(hull_points)
    hull = points.convex_hull
    # From trial-and-error, the L-BFGS-B method works the best by far
    res = minimize(lambda x: fun(x, hull), rect.flat, method='L-BFGS-B',
               options={'ftol': 1e-4, 'disp': True, 'eps': 0.1})
    corners = w.all_pix2world(res.x.reshape(4,2),0)
    return(corners)


# ## Test on a SPIRE image, pixel coordinates only

# In[13]:

import astropy.io.fits as fits
from astropy.wcs import WCS


# In[39]:

#fname = '/Users/shupe/data/spsc/level2/20151007/fits/fits/1342186233PLW_pmd.fits.zip'
#fname = '/Users/shupe/data/spsc/level2/20151007/fits/fits/1342206677PLW_pmd.fits.zip'
fname = '/Users/shupe/data/spsc/level2/20151007/fits/fits/1342206694PSW_pmd.fits.zip'
#fname = '/Users/shupe/data/spsc/level2/20151007/fits/fits/1342207030PSW_pmd.fits.zip'


# In[40]:

hdu = fits.open(fname)


# In[41]:

get_ipython().magic('time mycorners = fourCorners(fname)')


# In[42]:

mycorners


# ## Plot image and box in world coordinates

# In[43]:

import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')


# In[44]:

import aplpy


# In[45]:

gc = aplpy.FITSFigure(hdu[1])
gc.show_grayscale()
gc.show_polygons([mycorners], edgecolor='b')


# In[ ]:




# In[ ]:



