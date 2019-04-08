#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#    Copyright (C) 2009-2019 Ovidio Peña Rodríguez <ovidio@bytesfall.com>
#    Copyright (C) 2013-2019 Konstantin Ladutenko <kostyfisik@gmail.com>
#
#    This file is part of scattnlay
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    The only additional remark is that we expect that all publications
#    describing work using this software, or all commercial products
#    using it, cite at least one of the following references:
#    [1] O. Peña and U. Pal, "Scattering of electromagnetic radiation by
#        a multilayered sphere," Computer Physics Communications,
#        vol. 180, Nov. 2009, pp. 2348-2354.
#    [2] K. Ladutenko, U. Pal, A. Rivera, and O. Peña-Rodríguez, "Mie
#        calculation of electromagnetic near-field for a multilayered
#        sphere," Computer Physics Communications, vol. 214, May 2017,
#        pp. 225-230.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from scattnlay_ import scattcoeffs_, scattnlay_,  fieldnlay_
import numpy as np
import sys


def switch_to_double_precision():
    from scattnlay_ import scattcoeffs_, scattnlay_,  fieldnlay_
    sys.modules['scattnlay.main'].scattnlay_ = scattnlay_
    sys.modules['scattnlay.main'].scattcoeffs_ = scattcoeffs_
    sys.modules['scattnlay.main'].fieldnlay_ = fieldnlay_


def switch_to_multiple_precision():
    from scattnlay_mp_ import scattcoeffs_, scattnlay_,  fieldnlay_
    sys.modules['scattnlay.main'].scattnlay_ = scattnlay_
    sys.modules['scattnlay.main'].scattcoeffs_ = scattcoeffs_
    sys.modules['scattnlay.main'].fieldnlay_ = fieldnlay_


def scattcoeffs(x, m, nmax=-1, pl=-1):
    """
    scattcoeffs(x, m[, nmax, pl])

    Calculate the scattering coefficients required to calculate both the
    near- and far-field parameters.

        x: Size parameters (1D or 2D ndarray)
        m: Relative refractive indices (1D or 2D ndarray)
        nmax: Maximum number of multipolar expansion terms to be used for the
              calculations. Only use it if you know what you are doing, otherwise
              set this parameter to -1 and the function will calculate it.
        pl: Index of PEC layer. If there is none just send -1

    Returns: (terms, an, bn)
    with
        terms: Number of multipolar expansion terms used for the calculations
        an, bn: Complex scattering coefficients
    """
    if len(m.shape) != 1 and len(m.shape) != 2:
        raise ValueError('The relative refractive index (m) should be a 1-D or 2-D NumPy array.')
    if len(x.shape) == 1:
        if len(m.shape) == 1:
            return scattcoeffs_(x, m, nmax=nmax, pl=pl)
        else:
            raise ValueError('The number of of dimensions for the relative refractive index (m) and for the size parameter (x) must be equal.')
    elif len(x.shape) != 2:
        raise ValueError('The size parameter (x) should be a 1-D or 2-D NumPy array.')

    if nmax == -1:
        nstore = 0
    else:
        nstore = nmax

    terms = np.zeros((x.shape[0]), dtype=int)
    an = np.zeros((0, nstore), dtype=complex)
    bn = np.zeros((0, nstore), dtype=complex)

    for i, xi in enumerate(x):
        if len(m.shape) == 1:
            mi = m
        else:
            mi = m[i]

        terms[i], a, b = scattcoeffs_(xi, mi, nmax=nmax, pl=pl)

        if terms[i] > nstore:
            nstore = terms[i]
            an.resize((an.shape[0], nstore))
            bn.resize((bn.shape[0], nstore))

        an = np.vstack((an, a))
        bn = np.vstack((bn, b))

    return terms, an, bn
#scattcoeffs()


def scattnlay(x, m, theta=np.zeros(0, dtype=float), nmax=-1, pl=-1):
    """
    scattnlay(x, m[, theta, nmax, pl])

    Calculate the actual scattering parameters and amplitudes.

        x: Size parameters (1D or 2D ndarray)
        m: Relative refractive indices (1D or 2D ndarray)
        theta: Scattering angles where the scattering amplitudes will be
               calculated (optional, 1D ndarray)
        nmax: Maximum number of multipolar expansion terms to be used for the
              calculations. Only use it if you know what you are doing.
        pl: Index of PEC layer.

    Returns: (terms, Qext, Qsca, Qabs, Qbk, Qpr, g, Albedo, S1, S2)
    with
        terms: Number of multipolar expansion terms used for the calculations
        Qext: Efficiency factor for extinction
        Qsca: Efficiency factor for scattering
        Qabs: Efficiency factor for absorption (Qabs = Qext - Qsca)
        Qbk: Efficiency factor for backscattering
        Qpr: Efficiency factor for the radiation pressure
        g: Asymmetry factor (g = (Qext-Qpr)/Qsca)
        Albedo: Single scattering albedo (Albedo = Qsca/Qext)
        S1, S2: Complex scattering amplitudes
    """
    if len(m.shape) != 1 and len(m.shape) != 2:
        raise ValueError('The relative refractive index (m) should be a 1-D or 2-D NumPy array.')
    if len(x.shape) == 1:
        if len(m.shape) == 1:
            return scattnlay_(x, m, theta, nmax=nmax, pl=pl)
        else:
            raise ValueError('The number of of dimensions for the relative refractive index (m) and for the size parameter (x) must be equal.')
    elif len(x.shape) != 2:
        raise ValueError('The size parameter (x) should be a 1-D or 2-D NumPy array.')
    if len(theta.shape) != 1:
        raise ValueError('The scattering angles (theta) should be a 1-D NumPy array.')

    terms = np.zeros((x.shape[0]), dtype=int)
    Qext = np.zeros((x.shape[0]), dtype=float)
    Qsca = np.zeros((x.shape[0]), dtype=float)
    Qabs = np.zeros((x.shape[0]), dtype=float)
    Qbk = np.zeros((x.shape[0]), dtype=float)
    Qpr = np.zeros((x.shape[0]), dtype=float)
    g = np.zeros((x.shape[0]), dtype=float)
    Albedo = np.zeros((x.shape[0]), dtype=float)
    S1 = np.zeros((x.shape[0], theta.shape[0]), dtype=complex)
    S2 = np.zeros((x.shape[0], theta.shape[0]), dtype=complex)

    for i, xi in enumerate(x):
        if len(m.shape) == 1:
            mi = m
        else:
            mi = m[i]

        terms[i], Qext[i], Qsca[i], Qabs[i], Qbk[i], Qpr[i], g[i], Albedo[i], S1[i], S2[i] = scattnlay_(xi, mi, theta, nmax=nmax, pl=pl)

    return terms, Qext, Qsca, Qabs, Qbk, Qpr, g, Albedo, S1, S2
#scattnlay()


def fieldnlay(x, m, xp, yp, zp, nmax=-1, pl=-1):
    """
    fieldnlay(x, m, xp, yp, zp[, theta, nmax, pl])

    Calculate the actual scattering parameters and amplitudes.

        x: Size parameters (1D or 2D ndarray)
        m: Relative refractive indices (1D or 2D ndarray)
        xp: Array containing all X coordinates to calculate the complex
            electric and magnetic fields (1D ndarray)
        nmax: Maximum number of multipolar expansion terms to be used for the
              calculations. Only use it if you know what you are doing.
        pl: Index of PEC layer.

    Returns: (terms, E, H)
    with
        terms: Number of multipolar expansion terms used for the calculations
        E, H: Complex electric and magnetic field at the provided coordinates
    """
    if len(m.shape) != 1 and len(m.shape) != 2:
        raise ValueError('The relative refractive index (m) should be a 1-D or 2-D NumPy array.')
    if len(x.shape) == 1:
        if len(m.shape) == 1:
            return fieldnlay_(x, m, xp, yp, zp, nmax=nmax, pl=pl)
        else:
            raise ValueError('The number of of dimensions for the relative refractive index (m) and for the size parameter (x) must be equal.')
    elif len(x.shape) != 2:
        raise ValueError('The size parameter (x) should be a 1-D or 2-D NumPy array.')

    terms = np.zeros((x.shape[0]), dtype=int)
    E = np.zeros((x.shape[0], xp.shape[0], 3), dtype=complex)
    H = np.zeros((x.shape[0], xp.shape[0], 3), dtype=complex)

    for i, xi in enumerate(x):
        if len(m.shape) == 1:
            mi = m
        else:
            mi = m[i]

        terms[i], E[i], H[i] = fieldnlay_(xi, mi, xp, yp, zp, nmax=nmax, pl=pl)

    return terms, E, H
#fieldnlay()

