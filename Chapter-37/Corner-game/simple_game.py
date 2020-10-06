#This version requires python 2.7

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from sklearn.model_selection import train_test_split
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt
from operator import add, neg

def solve(payoff_matrix, iterations=100):
    'Return the oddments (mixed strategy ratios) for a given payoff matrix'
    transpose = zip(*payoff_matrix)
    numrows = len(payoff_matrix)
    numcols = len(transpose)
    row_cum_payoff = [0] * numrows
    col_cum_payoff = [0] * numcols
    colpos = xrange(numcols)
    rowpos = map(neg, range(numrows))
    colcnt = [0] * numcols
    rowcnt = [0] * numrows
    active = 0
    for i in xrange(iterations):
        rowcnt[active] += 1        
        col_cum_payoff = map(add, payoff_matrix[active], col_cum_payoff)
        active = min((zip(col_cum_payoff, colpos)))[1]
        colcnt[active] += 1       
        row_cum_payoff = map(add, transpose[active], row_cum_payoff)
        active = -max(zip(row_cum_payoff, rowpos))[1]
    value_of_game = (max(row_cum_payoff) + min(col_cum_payoff)) / 2.0 / iterations
    return rowcnt, colcnt, value_of_game



d = range(1,22)

aset = [1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2]

for a in aset:

	dataset = pd.read_csv("matrix.csv")

	for i in range(len(dataset)):
		dataset.Drive[i] = 1.22 * (1-(1.0/(a**((22-i)))))

	print(dataset)

	niter = 200

	X = -np.array(dataset)

	sol = solve(X,iterations = niter)
	nash_defense = np.array(sol[0])/float(niter)
	nash_offense = np.array(sol[1])/float(niter)
	expected_pts = sol[2]
	print "a = ", a 
        print "Defense Nash equilibrium: ", nash_defense #sum(nash_defense*[21, 20, 19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1]),nash_offense, sol[2]
        print "Offense Nash equilibrium: ", nash_offense
        print "Value of the game (xPts): ", sol[2]
