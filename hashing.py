import numpy as np
import numba as nb
import matplotlib.pyplot as plt

norm = np.linalg.norm
                    
def _sort_stars(star_pos):
    """
    sort  such that A and B are most distant start

    Parameters
    ----------
    star_pos : (4,2) np.ndarray with star coordinates
    
    Returns
    -------
    A : (2,) star coordinate with most distant star
    B : (2,) star coordinate with most distant star
    C : (2,) star coordinate inside circle created by A,B
    D : (2,) star coordinate inside circle created by A,B

    """
    dist_mat = np.array([[0, norm(star_pos[0]-star_pos[1]), norm(star_pos[0]-star_pos[2]), norm(star_pos[0]-star_pos[3])],
                         [0,                             0, norm(star_pos[1]-star_pos[2]), norm(star_pos[1]-star_pos[3])],
                         [0,                             0,                             0, norm(star_pos[2]-star_pos[3])]]) 
    
    idx_max = np.array(np.unravel_index(dist_mat.argmax(), dist_mat.shape))
    
    A, B = star_pos[idx_max]
    C, D = star_pos[~np.isin(np.array([0,1,2,3]), idx_max)]
    
    return A,B,C,D


def _rectify_code(code):
    """code is symmetric, make code is invariant to order of stars in hashing"""
    if (code[0]+code[2] > 1):
        code = 1-code
    if (code[0] > code[2]): 
        code = code[[2, 3, 0, 1]]
    return code


def generate_quad_code(star_pos):
    """
    generate geometric hash code given coordinates for four stars as described
    in reference.
    
    The hash code are the normalized coordinates of stars C and D in a
    coordinate system span by A and B. A and B must be the most distant stars.
    Hash coordinates are not neccessarily in [0,1]!

    Parameters
    ----------
    star_pos : (4,2) np.ndarray with star coordinates

    Returns
    -------
    code : (4,) np.ndarray with hash code
        
    Reference
    -------
    Lang, D., Hogg, D. W., Mierle, K., Blanton, M., & Roweis, S. (2010). 
    Astrometry. net: Blind astrometric calibration of arbitrary astronomical 
    images. The astronomical journal, 139(5), 1782.
        
    Derivation
    --------
    Transformation of shited B into the local coordinate system:
    1) Rotate B by alpha with alpha beeing the angle between B and the x-axis. 
    2) Rotate B by -45° to have equal coordinates (Bx'=By'). 
    3) Scale by sqrt(2)/hyp with hyp=sqrt(Bx**2 + By**2)
    
    B' = rot(-45°)*rot(alpha)*B*scale
       = ( 1  1) (cos(alpha)  -sin(alpha)) B sqrt(2)/hyp
         (-1  1) (sin(alpha)   cos(alpha))
        
    cos(alpha) = cos(acos(By/hyp)) => cos(alpha) =  By
    sin(alpha) = sin(asin(Bx/hyp)) => sin(alpha) =  Bx
    
    B' = ( 1  1) ( By -Bx) B hyp**2
         (-1  1) ( Bx  By) 

    """
    A, B, C, D = _sort_stars(star_pos)
    
    # shift
    B_shift = B-A
    C_shift = C-A
    D_shift = D-A
    
    # rotate
    M = np.array([[+B_shift[1], -B_shift[0]],
                  [+B_shift[0], +B_shift[1]]])
    E = np.array([[ 1,  1],
                  [-1,  1]])
    B_rot = E@M@B_shift
    C_rot = E@M@C_shift
    D_rot = E@M@D_shift
    
    # scaling
    scale = 1.0/(B_shift[0]**2 + B_shift[1]**2)
    B_norm = B_rot*scale
    C_norm = C_rot*scale
    D_norm = D_rot*scale
    
    #assert np.all(B_norm==np.array([1.0, 1.0])), B_norm
    
    raw_code = np.concatenate((C_norm, D_norm))
    
    if not (
            ((norm(raw_code[[0,1]]) <= np.sqrt(2)) & (norm(raw_code[[0,1]]-np.array([1,1])) <= np.sqrt(2)))
          | ((norm(raw_code[[2,3]]) <= np.sqrt(2)) & (norm(raw_code[[2,3]]-np.array([1,1])) <= np.sqrt(2)))
          ):
        print(raw_code, star_pos, A, B, C, D, B_norm)
        print(norm(raw_code[[0,1]]), norm(raw_code[[0,1]]-np.array([1,1])),
              norm(raw_code[[2,3]]), norm(raw_code[[2,3]]-np.array([1,1])))
        plt.scatter(A[0], A[1], c="r")
        plt.scatter(B[0], B[1], c="g")
        plt.scatter(C[0], C[1], c="b")
        plt.scatter(D[0], D[1], c="k")
        plt.gca().add_patch(plt.Circle((A+B)/2, norm(A-B)/2, fill=False))
        plt.gca().set_aspect("equal")
        plt.show()
        #----
        plt.scatter(0, 0, c="r")
        plt.scatter(B_shift[0], B_shift[1], c="g")
        plt.scatter(C_shift[0], C_shift[1], c="b")
        plt.scatter(D_shift[0], D_shift[1], c="k")
        plt.gca().add_patch(plt.Circle((B_shift)/2, norm(B_shift)/2, fill=False))
        plt.gca().set_aspect("equal")
        plt.show()
        #----
        plt.scatter(0, 0, c="r")
        plt.scatter(B_rot[0], B_rot[1], c="g")
        plt.scatter(C_rot[0], C_rot[1], c="b")
        plt.scatter(D_rot[0], D_rot[1], c="k")
        plt.gca().add_patch(plt.Circle((B_rot)/2, norm(B_rot)/2, fill=False))
        plt.gca().set_aspect("equal")
        plt.show()
        #----
        plt.scatter(1,1, c="r")
        plt.scatter(B_norm[0], B_norm[1], c="g")
        plt.scatter(C_norm[0], C_norm[1], c="b")
        plt.scatter(D_norm[0], D_norm[1], c="k")
        plt.gca().add_patch(plt.Circle((B_norm)/2, norm(B_norm)/2, fill=False))
        plt.gca().set_aspect("equal")
        plt.show()
        raise ValueError
        
    
    code = _rectify_code(raw_code)
    
    return code
    


def generate_hash_codes(star_pos, star_brightness):
    """generate codes for given brightest stars (for tests)"""
    # sort by brightness (use more sophisticated loop in future)
    _star_pos = star_pos[np.argsort(star_brightness)]
    
    n_stars = star_pos.shape[0]
    #codes = np.zeros((,4))
    # iterate by brightness
    for i_a in range(3, n_stars):
        for i_b in range(2, i_a):
            for i_c in range(1, i_b):
                for i_d in range(0, i_c):
                    code = generate_quad_code(_star_pos[[i_a, i_b, i_c, i_d]])  
    return code

