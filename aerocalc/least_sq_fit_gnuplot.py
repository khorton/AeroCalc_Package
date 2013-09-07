#!/usr/bin/env python
"""
Least squares fit functions for use in plotting in Gnuplot.

Typical use, with numpy arrays of x and y values (X_vals_array, Y_vals_array):

    import Gnuplot, Gnuplot.funcutils
    func_text = lst_sq_fitN(X_vals_array, Y_vals_array) # where N is an integer between 1 and 9, indicating the maximum power in the polynomial.  I.e. N = 1 produces a linear fit.  N = 2 is a parabolic fit, etc.
    g = Gnuplot.Gnuplot(debug=1)
    data=Gnuplot.Data(X_vals_array, Y_vals_array, title='Data', with ='p -1 4')
    g.plot(data, Gnuplot.Func(func_text, title='Curve Fit to Data', with ='lines lt -1'))
"""
from __future__ import division
from scipy.optimize import leastsq

def residuals1(p, y, x):
    a, b = p
    err = y - (a + b * x)
    return err

def lst_sq_fit1(X, Y, params=False):
    p0=[1., 1.]
    plsq = leastsq(residuals1, p0, args=(Y, X))
    [a, b] = plsq[0]
    func_text = '%.16f + %.16f * x' % (a, b)
    # return func_text, [a, b]
    if params:
        return func_text, plsq[0]
    else:
        return func_text

def residuals2(p, y, x):
    a, b, c = p
    err = y - (a + b * x + c * x**2)
    return err

def lst_sq_fit2(X, Y, params=False):
    p0=[1., 1., 1.]
    plsq = leastsq(residuals2, p0, args=(Y, X))
    [a, b, c] = plsq[0]
    func_text = '%.16f + %.16f * x + %.16f * x**2' % (a, b, c)
    # return func_text, [a, b, c]
    if params:
        return func_text, plsq[0]
    else:
        return func_text

def residuals3(p, y, x):
    a, b, c, d = p
    err = y - (a + b * x + c * x**2 + d * x**3)
    return err

def lst_sq_fit3(X, Y, params=False):
    p0=[1., 1., 1., 1.]
    plsq = leastsq(residuals3, p0, args=(Y, X))
    [a, b, c, d] = plsq[0]
    func_text = '%.16f + %.16f * x + %.16f * x**2 + %.16f * x**3' % (a, b, c, d)
    # return func_text, [a, b, c, d]
    if params:
        return func_text, plsq[0]
    else:
        return func_text

def residuals4(p, y, x):
    a, b, c, d, e = p
    err = y - (a + b * x + c * x**2 + d * x**3 + e * x**4)
    return err

def lst_sq_fit4(X, Y, params=False):
    p0=[1., 1., 1., 1., 1.]
    plsq = leastsq(residuals4, p0, args=(Y, X))
    [a, b, c, d, e] = plsq[0]
    func_text = '%.16f + %.16f * x + %.16f * x**2 + %.16f * x**3 + %.16f * x**4' % (a, b, c, d, e)
    if params:
        return func_text, plsq[0]
    else:
        return func_text

def residuals5(p, y, x):
    a, b, c, d, e, f = p
    err = y - (a + b * x + c * x**2 + d * x**3 + e * x**4 + f * x**5)
    return err

def lst_sq_fit5(X, Y, params=False):
    p0=[1., 1., 1., 1., 1., 1.]
    plsq = leastsq(residuals5, p0, args=(Y, X))
    [a, b, c, d, e, f] = plsq[0]
    func_text = '%.16f + %.16f * x + %.16f * x**2 + %.16f * x**3 + %.16f * x**4 + %.16f * x**5' % (a, b, c, d, e, f)
    if params:
        return func_text, plsq[0]
    else:
        return func_text

def residuals6(p, y, x):
    a, b, c, d, e, f, g = p
    err = y - (a + b * x + c * x**2 + d * x**3 + e * x**4 + f * x**5 + g * x**6)
    return err

def lst_sq_fit6(X, Y, params=False):
    p0=[1., 1., 1., 1., 1., 1., 1.]
    plsq = leastsq(residuals6, p0, args=(Y, X))
    [a, b, c, d, e, f, g] = plsq[0]
    func_text = '%.16f + %.16f * x + %.16f * x**2 + %.16f * x**3 + %.16f * x**4 + %.16f * x**5 + %.16f * x**6' % (a, b, c, d, e, f, g)
    if params:
        return func_text, plsq[0]
    else:
        return func_text

def residuals7(p, y, x):
    a, b, c, d, e, f, g, h = p
    err = y - (a + b * x + c * x**2 + d * x**3 + e * x**4 + f * x**5 + g * x**6 + h * x**7)
    return err

def lst_sq_fit7(X, Y, params=False):
    p0=[1., 1., 1., 1., 1., 1., 1., 1.]
    plsq = leastsq(residuals7, p0, args=(Y, X))
    [a, b, c, d, e, f, g, h] = plsq[0]
    func_text = '%.16f + %.16f * x + %.16f * x**2 + %.16f * x**3 + %.16f * x**4 + %.16f * x**5 + %.16f * x**6 + %.16f * x**7' % (a, b, c, d, e, f, g, h)
    if params:
        return func_text, plsq[0]
    else:
        return func_text

def residuals8(p, y, x):
    a, b, c, d, e, f, g, h, i = p
    err = y - (a + b * x + c * x**2 + d * x**3 + e * x**4 + f * x**5 + g * x**6 + h * x**7 + i * x**8)
    return err

def lst_sq_fit8(X, Y, params=False):
    p0=[1., 1., 1., 1., 1., 1., 1., 1., 1.]
    plsq = leastsq(residuals8, p0, args=(Y, X))
    [a, b, c, d, e, f, g, h, i] = plsq[0]
    func_text = '%.16f + %.16f * x + %.16f * x**2 + %.16f * x**3 + %.16f * x**4 + %.16f * x**5 + %.16f * x**6 + %.16f * x**7 + %.16f * x**8' % (a, b, c, d, e, f, g, h, i)
    if params:
        return func_text, plsq[0]
    else:
        return func_text

def residuals9(p, y, x):
    a, b, c, d, e, f, g, h, i, j = p
    err = y - (a + b * x + c * x**2 + d * x**3 + e * x**4 + f * x**5 + g * x**6 + h * x**7 + i * x**8 + j * x**9)
    return err

def lst_sq_fit9(X, Y, params=False):
    p0=[1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]
    plsq = leastsq(residuals9, p0, args=(Y, X))
    [a, b, c, d, e, f, g, h, i, j] = plsq[0]
    func_text = '%.16f + %.16f * x + %.16f * x**2 + %.16f * x**3 + %.16f * x**4 + %.16f * x**5 + %.16f * x**6 + %.16f * x**7 + %.16f * x**8 + %.16f * x**9' % (a, b, c, d, e, f, g, h, i, j)
    if params:
        return func_text, plsq[0]
    else:
        return func_text

