from SimPEG.Utils import mkvc
from SimPEG import Utils
import numpy as np
import multiprocessing
import scipy.constants as constants

def calcTrow(args):
    """
    Load in the active nodes of a tensor mesh and computes the gravity tensor
    for a given observation location rxLoc[obsx, obsy, obsz]

    INPUT:
    Xn, Yn, Zn: Node location matrix for the lower and upper most corners of
                all cells in the mesh shape[nC,2]
    M
    OUTPUT:
    Tx = [Txx Txy Txz]
    Ty = [Tyx Tyy Tyz]
    Tz = [Tzx Tzy Tzz]

    where each elements have dimension 1-by-nC.
    Only the upper half 5 elements have to be computed since symetric.
    Currently done as for-loops but will eventually be changed to vector
    indexing, once the topography has been figured out.

    """

    rxLoc, Xn, Yn, Zn, component = args

    NewtG = constants.G*1e+8  # Convertion from mGal (1e-5) and g/cc (1e-3)
    eps = 1e-8  # add a small value to the locations to avoid

    nC = Xn.shape[0]

    # Pre-allocate space for 1D array
    t = np.zeros((1, nC))

    dz = rxLoc[2] - Zn

    dy = Yn - rxLoc[1]

    dx = Xn - rxLoc[0]


    # Compute contribution from each corners
    for aa in range(2):
        for bb in range(2):
            for cc in range(2):

                r = (
                        mkvc(dx[:, aa]) ** 2 +
                        mkvc(dy[:, bb]) ** 2 +
                        mkvc(dz[:, cc]) ** 2
                    ) ** (0.50)

                if component == 'x':
                    t = t - NewtG * (-1) ** aa * (-1) ** bb * (-1) ** cc * (
                        dy[:, bb] * np.log(dz[:, cc] + r + eps) +
                        dz[:, cc] * np.log(dy[:, bb] + r + eps) -
                        dx[:, aa] * np.arctan(dy[:, bb] * dz[:, cc] /
                                              (dx[:, aa] * r + eps)))

                elif component == 'y':
                    t = t - NewtG * (-1) ** aa * (-1) ** bb * (-1) ** cc * (
                        dx[:, aa] * np.log(dz[:, cc] + r + eps) +
                        dz[:, cc] * np.log(dx[:, aa] + r + eps) -
                        dy[:, bb] * np.arctan(dx[:, aa] * dz[:, cc] /
                                              (dy[:, bb] * r + eps)))

                else:
                    t = t - NewtG * (-1) ** aa * (-1) ** bb * (-1) ** cc * (
                        dx[:, aa] * np.log(dy[:, bb] + r + eps) +
                        dy[:, bb] * np.log(dx[:, aa] + r + eps) -
                        dz[:, cc] * np.arctan(dx[:, aa] * dy[:, bb] /
                                              (dz[:, cc] * r + eps)))

    # # progress(index)
    # ind = np.asarray(range(10)) * nD / 10
    # if np.any(index == ind):
    #     print("Done " + str(index/nD*100) + " %")

    return t

# def progress(iter, prog, final):
#     """
#     progress(iter,prog,final)

#     Function measuring the progress of a process and print to screen the %.
#     Useful to estimate the remaining runtime of a large problem.

#     Created on Dec, 20th 2015

#     @author: dominiquef
#     """
#     arg = np.floor(float(iter)/float(final)*10.)

#     if arg > prog:

#         print("Done " + str(arg*10) + " %")
#         prog = arg

#     return prog

def getTmat(rxLoc, Xn, Yn, Zn, comp):
    print('Hello World')
    nD = rxLoc.shape[0]
    pool = multiprocessing.Pool(8)
    result = pool.map(calcTrow, [(rxLoc[ii, :], Xn, Yn, Zn, comp) for ii in range(rxLoc.shape[0])])
    pool.close()
    pool.join()

    return result

if __name__ == '__main__':
    print('Hello World')
    rxLoc = np.random.randn(1000, 3)

    nC = 20
    xn = np.asarray(range(nC))#self.mesh.vectorNx
    yn = np.asarray(range(nC))#self.mesh.vectorNy
    zn = np.asarray(range(nC))#self.mesh.vectorNz

    yn2, xn2, zn2 = np.meshgrid(yn[1:], xn[1:], zn[1:])
    yn1, xn1, zn1 = np.meshgrid(yn[0:-1], xn[0:-1], zn[0:-1])

    Yn = np.c_[Utils.mkvc(yn1), Utils.mkvc(yn2)]
    Xn = np.c_[Utils.mkvc(xn1), Utils.mkvc(xn2)]
    Zn = np.c_[Utils.mkvc(zn1), Utils.mkvc(zn2)]
    comp = 'dz'
    result = getTmat(rxLoc, Xn, Yn, Zn, comp)
    # getTmat(args)
#     obj = ClassName()
#     obj.getTmat()