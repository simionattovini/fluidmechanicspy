import numpy as np

__REL_ROUGH_STD_VALS = np.array([0, 1e-5, 5e-5,
                                 1e-4, 2e-4, 4e-4, 6e-4, 8e-4,
                                 1e-3, 2e-3, 4e-3, 6e-3, 8e-3,
                                 0.01, 0.015, 0.02, 0.03, 0.04, 0.05])


def f_colebrook(relrough: float, reynolds: float, tol: float=1e-6, max_it: int = 10000) -> float:
    """
    f_colebrook calculates the friction factor f according to the Colebrook formula.

    :param relrough: Relative roughness of the piping
    :param reynolds: Reynolds Number
    :param tol: Tolerance between iteration steps
    :param max_it: Maximum number of iterations
    :return: The friction factor f
    """

    if relrough < 0:
        raise ValueError('Relative Roughness must be a non-negative value')
    if reynolds < 2300:
        raise ValueError('Reynolds number must be >= 2300')
    if tol <= 0:
        raise ValueError('Tolerance must be a positive value')
    if max_it <= 0:
        raise ValueError('The maximum number of iterations must be positive')

    val: float = 1
    val = -2 * np.log10(relrough / 3.7 + (2.51 / reynolds) * val)
    dif: float = np.abs(val - 1)
    it = 0
    while dif > tol and it < max_it:
        dif = val
        val = -2 * np.log10(relrough / 3.7 + (2.51 / reynolds) * val)
        dif = np.abs(dif - val)
        it += 1

    if it >= max_it - 1:
        print(f'Maximum number of iterations ({str(it)}) reached before convergence. ' +
              f'Result might be innacurate')

    return (1/val)**2

def f_haaland(relrough: float, reynolds: float) -> float:
    """
    f_haaland calculates the friction factor f according to the Haaland formula.

    :param relrough: Relative roughness of the piping
    :param reynolds: Reynolds Number
    :return: The friction factor f
    """

    if relrough < 0:
        raise ValueError('Relative Roughness must be a non-negative value')
    if reynolds < 2300:
        raise ValueError('Reynolds number must be >= 2300')

    if reynolds < 3000:
        print('Warning: Haaland formula for friction factor is not valid for Re<3000')

    return (-1.8*np.log10((relrough/3.7)**1.11+6.9/reynolds))**-2

def f_laminar(reynolds: float, suppress_warnings: bool = False) -> float:
    """
    f_laminar calculates the friction factor for laminar flow, given by f = 64/Re
    :param reynolds: Reynolds number
    :return: The friction factor for a laminar flow with given reynolds number
    """

    if not suppress_warnings:
        if reynolds > 2300:
            print('Warning: flow is usually not laminar for Re>2300')

    if reynolds<=0:
        raise ValueError('Reynolds number must be positive')

    return 64/reynolds

def f2rr_colebrook(f: float) -> float:
    """
    Converts friction factor to relative roughness for Re->inf
    :param f: friction factor
    :return: relative roughness
    """
    return 3.7 * (10 ** ((-1/2)*np.sqrt(1/f)))

def rr2f_colebrook(rr: float) -> float:
    """
    Converts relative roughness to friction factor for Re->inf
    :param rr: relative roughness
    :return: friciton factor
    """
    np.seterr(divide='ignore')
    return (-2*np.log10(rr/3.7))**(-2)

def f_regardless(reynolds: float, relrough: float, lt_lim: float =2300) -> float:
    """
    f_regardless calculates the value for the friction factor whether the flow is laminar or tubulent
    :param reynolds: Reynolds number
    :param relrough: Relative roughness
    :param lt_lim: Laminar-Turbulent limit
    :return: friction factor
    """
    if reynolds >= lt_lim:
        f = f_colebrook(relrough, reynolds)
    else:
        f = f_laminar(reynolds)
    return f