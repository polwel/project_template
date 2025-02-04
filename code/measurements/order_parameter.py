from subprocess import check_call
import numpy as np
from matplotlib import pyplot as plt
import matplotlib

from paths import SETTINGS_PATH, OUTPUT_PATH, SIM_PATH, SIM_WD
from common import parse_output

SETTINGS_TEMPLATE = """
N_CARS    = 50
ROAD_LENGTH = 1000
VMAX      = 15
MIN_DIST  = 2
TIME_HEAD = 1.5
AMAX      = 0.6
DMAX      = 2
CAR_SIZE  = 5
DT        = 0.250
END_TIME  = 30000


# Output format
POSITIONS = 1
VELOCITIES = 1
OUT_FREQ = 80
THROUGHPUT = 1
"""


def compute_variances(N, save=True, settings = SETTINGS_TEMPLATE, gammas = None):
    if gammas == None:    
        gammas = np.linspace(1.5, 3.5, N)
    N = len(gammas)
    variances = 0*gammas
    
    for i, gamma in enumerate(gammas):
        print "\n\nRunning sim for gamma = {0}".format(gamma)
        settings_file = open(SETTINGS_PATH + "/order_parameter.txt", "w")
        settings_file.write(settings)
        settings_file.write("ID = order_parameter{0}\nGAMMA = {0}".format(gamma))
        settings_file.close()
    
        check_call([SIM_PATH, SETTINGS_PATH+"/order_parameter.txt"], cwd = SIM_WD)
        
        # read output
        n, tt, xx, vv, throughput = parse_output(OUTPUT_PATH+"/cars_order_parameter{}.dat".format(gamma))      
        
        variances[i] = np.var(vv[-1])
        
    if save:   
        np.save("variances", variances)
        np.save("gammas", gammas)
    return gammas, variances


def make_plot():
    variances = np.load("variances.npy")
    gammas = np.load("gammas.npy")

    matplotlib.rcParams.update({'font.size': 11})
    plt.figure(figsize=(4,3), dpi = 200)
    plt.plot(gammas, np.sqrt(variances), label="data")
    plt.xlabel(r"interaction exponent $\gamma$")
    plt.ylabel(r"std. dev. of velocities $\sqrt{\langle v^2 \rangle}$ [m/s]")
    plt.ylim((-1, np.sqrt(np.max(variances))+1))
    
    
    idx = np.where(np.logical_and(2.8 <= gammas, gammas <= 2.97) )
    a, b = np.polyfit(gammas[idx], np.sqrt(variances)[idx], 1)
    xx = np.linspace(2.,3.5, 2)
    plt.plot(xx, a*xx+b, "g--", label="linear fit")
    plt.grid(True)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig("order_parameter.png")
    plt.savefig("order_parameter.pdf")
    plt.show()
    
    
if __name__ == "__main__":
    #compute_variances(N=101)
    make_plot()

