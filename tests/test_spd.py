# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import numpy as np
from plum import Dispatcher
from lab import B

from stheno.spd import SPD, Diagonal, UniformDiagonal, LowRank
# noinspection PyUnresolvedReferences
from . import eq, neq, lt, le, ge, gt, raises, call, ok, eprint

dispatch = Dispatcher()


def test_spd():
    a = np.random.randn(3, 3)
    dummy = SPD(a.dot(a.T))

    def compare(ref, spd, invertible=True):
        a = np.random.randn(3, 10)
        b = np.random.randn(3, 10)
        A = np.random.randn(3, 3)

        # Compare implementations.
        yield ok, np.allclose(ref.mat, spd.mat), 'matrices'
        yield ok, np.allclose(ref.diag, spd.diag), 'diagonals'
        yield ok, ref.shape == spd.shape, 'shapes'
        yield ok, np.allclose(ref.cholesky(),
                              spd.cholesky()), 'cholesky'
        yield ok, np.allclose(ref.root(), spd.root()), 'roots'
        yield ok, np.allclose(ref.cholesky_mul(A),
                              spd.cholesky_mul(A)), 'chol mul'
        yield ok, np.allclose(ref.ratio(dummy), spd.ratio(dummy)), 'ratio'

        if invertible:
            yield ok, np.allclose(ref.mah_dist2(a), spd.mah_dist2(a)), 'mah'
            yield ok, np.allclose(ref.mah_dist2(a, b),
                                  spd.mah_dist2(a, b)), 'mah 2'
            yield ok, np.allclose(ref.quadratic_form(a),
                                  spd.quadratic_form(a)), 'qf'
            yield ok, np.allclose(ref.quadratic_form(a, b),
                                  spd.quadratic_form(a, b)), 'qf 2'
            yield ok, np.allclose(ref.quadratic_form_diag(a),
                                  spd.quadratic_form_diag(a)), 'qf diag'
            yield ok, np.allclose(ref.quadratic_form_diag(a, b),
                                  spd.quadratic_form_diag(a, b)), 'qf diag 2'
            yield ok, np.allclose(ref.ratio(ref), spd.ratio(ref)), 'ratio 2'
            yield ok, np.allclose(ref.ratio(ref), spd.ratio(spd)), 'ratio 3'
            yield ok, np.allclose(ref.ratio(spd), spd.ratio(ref)), 'ratio 4'
            yield ok, np.allclose(ref.ratio(spd), spd.ratio(spd)), 'ratio 5'
            yield ok, np.allclose(ref.inv_prod(A), spd.inv_prod(A)), 'inv prod'
            yield ok, np.allclose(ref.logdet(), spd.logdet()), 'logdets'
        else:
            yield raises, RuntimeError, lambda: spd.mah_dist2(a)
            yield raises, RuntimeError, lambda: spd.mah_dist2(a, a)
            yield raises, RuntimeError, lambda: spd.quadratic_form(a)
            yield raises, RuntimeError, lambda: spd.quadratic_form(a, a)
            yield raises, RuntimeError, lambda: spd.quadratic_form_diag(a)
            yield raises, RuntimeError, lambda: spd.quadratic_form_diag(a, a)
            yield raises, RuntimeError, lambda: spd.inv_prod(A)
            yield raises, RuntimeError, lambda: spd.logdet()

    # Compare Dense and diagonal implementation.
    a = np.diag(np.random.randn(3) ** 2)
    spd = SPD(a)
    spd_diag = Diagonal(np.diag(a))
    for x in compare(spd, spd_diag):
        yield x

    # Compare Dense and uniform diagonal implementation.
    a = np.random.randn() ** 2
    spd = SPD(np.eye(3) * a)
    spd_diag_uniform = UniformDiagonal(a, 3)
    for x in compare(spd, spd_diag_uniform):
        yield x

    # Compare Dense and low-rank implementation.
    a = np.random.randn(3, 2)
    spd = SPD(a.dot(a.T))
    spd_low_rank = LowRank(a)
    for x in compare(spd, spd_low_rank, invertible=False):
        yield x


def test_spd_arithmetic():
    dense = SPD(np.eye(3))
    diag = Diagonal(np.ones(3))

    yield eq, type(dense + dense), SPD
    yield eq, type(dense + diag), SPD
    yield eq, type(diag + dense), SPD
    yield eq, type(diag + diag), Diagonal

    yield ok, np.allclose(dense.mat + diag.mat, (dense + diag).mat)

    yield eq, type(dense * dense), SPD
    yield eq, type(dense * diag), SPD
    yield eq, type(diag * dense), SPD
    yield eq, type(diag * diag), Diagonal

    yield ok, np.allclose(dense.mat * diag.mat, (dense * diag).mat)

    yield eq, type(5 * dense), SPD
    yield eq, type(5 * diag), Diagonal

    yield ok, np.allclose(5 * dense.mat, (5 * dense).mat)
    yield ok, np.allclose(5 * diag.mat, (5 * diag).mat)

    yield eq, type(5 + dense), SPD
    yield eq, type(5 + diag), SPD

    yield ok, np.allclose(5 + dense.mat, (5 + dense).mat)
    yield ok, np.allclose(5 + diag.mat, (5 + diag).mat)


def test_lab_interaction():
    diag = Diagonal(np.ones(3))

    yield eq, type(B.add(diag, diag)), Diagonal
    yield eq, type(B.add(5, diag)), SPD
    yield eq, type(B.add(diag, 5)), SPD

    yield eq, type(B.multiply(diag, diag)), Diagonal
    yield eq, type(B.multiply(5, diag)), Diagonal
    yield eq, type(B.multiply(diag, 5)), Diagonal
