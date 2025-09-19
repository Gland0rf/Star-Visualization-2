import math

def _unit(v):
        L = math.hypot(v[0], v[1])
        return (v[0]/L, v[1]/L)
    
def _perp(u):
    return (-u[1], u[0])

def _colinear_root(mu, a, b, iters=100, tol=1e-12):
    def f(x):
        return (x
                - (1.0 - mu)*(x + mu)/abs(x + mu)**3
                - mu*(x - 1.0 + mu)/abs(x - 1.0 + mu)**3)
    fa, fb = f(a), f(b)
    if fa*fb > 0:
        for k in range(1, 6):
            aa, bb = a - k, b + k
            fa, fb = f(aa), f(bb)
            if fa*fb <= 0:
                a, b = aa, bb
                break
        else:
            return (a+b)/2
    for _ in range(iters):
        m = 0.5*(a+b)
        fm = f(m)
        if fa*fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
        if abs(b - a) < tol:
            break
    return 0.5*(a+b)

def _compute_lagrange_points_phys(star, current_planet):
    planet_pos = current_planet.location
    star_pos = star.location
    m_planet = current_planet.mass
    m_star = star.mass

    r_vec = (planet_pos[0] - star_pos[0], planet_pos[1] - star_pos[1])
    r = math.hypot(r_vec[0], r_vec[1])
    r_hat = _unit(r_vec)
    p_hat = _perp(r_hat)

    mtot = m_star + m_planet
    bary = ((m_star*star_pos[0] + m_planet*planet_pos[0]) / mtot,
            (m_star*star_pos[1] + m_planet*planet_pos[1]) / mtot)
    
    mu = m_planet / mtot

    eps = 1e-6
    x1 = _colinear_root(mu, -mu + eps, 1.0 - mu - eps)
    x2 = _colinear_root(mu, 1.0 - mu + eps, 5.0)
    x3 = _colinear_root(mu, -5.0, -mu - eps)

    def to_phys(x, y=0.0):
        return (star_pos[0] + r*((x + mu)*r_hat[0] + y*p_hat[0]),
                star_pos[1] + r*((x + mu)*r_hat[1] + y*p_hat[1]))
    
    l1 = to_phys(x1, 0.0)
    l2 = to_phys(x2, 0.0)
    l3 = to_phys(x3, 0.0)

    s3o2 = math.sqrt(3.0)/2.0
    l4 = to_phys(0.5 - mu, s3o2)
    l5 = to_phys(0.5 - mu, -s3o2)

    return l1, l2, l3, l4, l5