# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# MDAnalysis --- http://mdanalysis.googlecode.com
# Copyright (c) 2006-2011 Naveen Michaud-Agrawal,
#               Elizabeth J. Denning, Oliver Beckstein,
#               and contributors (see website for details)
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
#     N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and
#     O. Beckstein. MDAnalysis: A Toolkit for the Analysis of
#     Molecular Dynamics Simulations. J. Comput. Chem. 32 (2011), 2319--2327,
#     doi:10.1002/jcc.21787
#

"""
:mod:`MDAnalysis` --- analysis of molecular simulations in python
=================================================================

MDAnalysis is a python toolkit to analyze molecular dynamics
trajectories generated by CHARMM, NAMD, Amber, Gromacs, or LAMMPS.

It allows one to read molecular dynamics trajectories and access the
atomic coordinates through numpy arrays. This provides a flexible and
relatively fast framework for complex analysis tasks. In addition,
CHARMM-style atom selection commands are implemented. Trajectories can
also be manipulated (for instance, fit to a reference structure) and
written out. Time-critical code is written in C for speed.

Code and documentation are hosted at http://code.google.com/p/mdanalysis/

Help is also available through the mailinglist at
http://groups.google.com/group/mdnalysis-discussion

Please report bugs and feature requests through the issue tracker at
http://code.google.com/p/mdanalysis/issues/

Citation
--------

When using MDAnalysis in published work, please cite

    N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and
    O. Beckstein. MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics
    Simulations. J. Comput. Chem. 32 (2011), 2319--2327, doi:`10.1002/jcc.21787`_
    http://mdanalysis.googlecode.com


.. rubric:: Included algorithms

If you use the RMSD alignment code (:mod:`MDAnalysis.analysis.align`) that
uses the :mod:`~MDAnalysis.core.qcprot` module please also cite

    Douglas L. Theobald. Rapid calculation of RMSD using a
    quaternion-based characteristic polynomial. Acta Crystallographica
    A 61 (2005), 478-480.

    Pu Liu, Dmitris K. Agrafiotis, and Douglas L. Theobald. Fast
    determination of the optimal rotational matrix for macromolecular
    superpositions. J. Comput. Chem. 31 (2010), 1561-1563.

If you use the helix analysis algorithm HELANAL_ in
:mod:`MDAnalysis.analysis.helanal` please cite

    Bansal M, Kumar S, Velavan R. 2000. HELANAL - A program to characterise
    helix geometry in proteins. J. Biomol. Struct. Dyn. 17, 811-819

Thanks!

.. _`10.1002/jcc.21787`: http://dx.doi.org/10.1002/jcc.21787
.. _HELANAL: http://www.ccrnp.ncifcrf.gov/users/kumarsan/HELANAL/helanal.html

Getting started
---------------

Import the package::

  >>> import MDAnalysis

(note that not everything in MDAnalysis is imported right away; for
additional functionality you might have to import sub-modules
separately, e.g. for RMS fitting ``import MDAnalysis.analysis.align``.)

Build a "universe" from a topology (PSF, PDB) and a trajectory (DCD, XTC/TRR);
here we are assuming that PSF, DCD, etc contain file names. If you don't have
trajectories at hand you can play with the ones that come with MDAnalysis for
testing (see below under `Examples`_)::

  >>> u = MDAnalysis.Universe(PSF, DCD)

Select the C-alpha atoms and store them as a group of atoms::

  >>> ca = u.selectAtoms('name CA')
  >>> len(ca)
  214

Calculate the centre of mass of the CA and of all atoms::

  >>> ca.centerOfMass()
  array([ 0.06873595, -0.04605918, -0.24643682])
  >>> u.atoms.centerOfMass()
  array([-0.01094035,  0.05727601, -0.12885778])

Calculate the CA end-to-end distance (in angstroem)::
  >>> from numpy import sqrt, dot
  >>> coord = ca.coordinates()
  >>> v = coord[-1] - coord[0]   # last Ca minus first one
  >>> sqrt(dot(v, v,))
  10.938133

Define a function eedist():
  >>> def eedist(atoms):
  ...     coord = atoms.coordinates()
  ...     v = coord[-1] - coord[0]
  ...     return sqrt(dot(v, v,))
  ...
  >>> eedist(ca)
  10.938133

and analyze all timesteps *ts* of the trajectory::
  >>> for ts in u.trajectory:
  ...      print eedist(ca)
  10.9381
  10.8459
  10.4141
   9.72062
  ....

.. SeeAlso:: :class:`MDAnalysis.core.AtomGroup.Universe` for details


Examples
--------

MDAnalysis comes with a number of real trajectories for testing. You
can also use them to explore the functionality and ensure that
everything is working properly::

  from MDAnalysis import *
  from MDAnalysis.tests.datafiles import PSF,DCD, PDB,XTC
  u_dims_adk = Universe(PSF,DCD)
  u_eq_adk = Universe(PDB, XTC)

The PSF and DCD file are a closed-form-to-open-form transition of
Adenylate Kinase (from [Beckstein2009]_) and the PDB+XTC file are ten
frames from a Gromacs simulation of AdK solvated in TIP4P water with
the OPLS/AA force field.

[Beckstein2009] O. Beckstein, E.J. Denning, J.R. Perilla and
                T.B. Woolf, Zipping and Unzipping of Adenylate Kinase: Atomistic
                Insights into the Ensemble of Open <--> Closed Transitions. J Mol Biol
                394 (2009), 160--176, doi:10.1016/j.jmb.2009.09.009
"""

__version__ = "0.8.0rc4"  # NOTE: keep in sync with RELEASE in setup.py

__all__ = ['Timeseries', 'Universe', 'asUniverse', 'Writer', 'collection']

import logging
# see the advice on logging and libraries in
# http://docs.python.org/library/logging.html?#configuring-logging-for-a-library
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
h = NullHandler()
logging.getLogger("MDAnalysis").addHandler(h)
del h

def start_logging(logfile="MDAnalysis.log"):
    """Start logging of messages to file and console.

    The default logfile is named `MDAnalysis.log` and messages are
    logged with the tag *MDAnalysis*.
    """
    import core.log
    core.log.create("MDAnalysis", logfile=logfile)
    logging.getLogger("MDAnalysis").info("MDAnalysis %s STARTED logging to %r", __version__, logfile)

def stop_logging():
    """Stop logging to logfile and console."""
    import core.log
    logger = logging.getLogger("MDAnalysis")
    logger.info("MDAnalysis STOPPED logging")
    core.log.clear_handlers(logger)  # this _should_ do the job...

# custom exceptions and warnings
class SelectionError(Exception):
    """Raised when a atom selection failed."""

class NoDataError(ValueError):
    """Raised when empty input is not allowed or required data are missing."""

class FormatError(EnvironmentError):
    """Raised when there appears to be a problem with format of input files."""

class ApplicationError(OSError):
    """Raised when an external application failed.

    The error code is specific for the application.

    .. versionadded:: 0.7.7
    """

class SelectionWarning(Warning):
    """Warning indicating a possible problem with a selection."""

class MissingDataWarning(Warning):
    """Warning indicating is that required data are missing."""

class ConversionWarning(Warning):
    """Warning indicating a problem with converting between units."""

class FileFormatWarning(Warning):
    """Warning indicating possible problems with a file format."""

# Bring some often used objects into the current namespace
from core import Timeseries
from core.AtomGroup import Universe, asUniverse, Merge
from coordinates.core import writer as Writer

collection = Timeseries.TimeseriesCollection()

