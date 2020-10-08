import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# simulation parameters 
ft = 0.77
pofr = 0.23
pcg2 = 0.52
pcg3 = 0.36
pot = 0.5

nsim = 10000
niter = 1000
sim = []

for _ in range(nsim):
    win = []
    for _ in range(niter):
            diff = 3
            # trailing team with the two fts
            if random.random()<ft:
                diff -= 1
            if random.random()<ft:
                diff -= 1
                if random.random()<ft:
                    diff +=1 
                    if diff >= 4:
                        win.append(0)
                        continue
                if random.random() < ft:
                    diff += 1
                    if diff >= 4:
                        win.append(0)
                        continue
                else:
                    if random.random() > pofr:
                        if diff == 1:
                            if random.random() < pcg2:
                                diff -=2
                        if diff > 1:
                            if random.random() < pcg3:
                                diff -=3
            else: 
                if random.random()<pofr:
                    if random.random()<pcg3:
                        diff-=3
                else:
                    if random.random()<ft:
                        diff +=1 
                        if diff >=4:
                            win.append(0)
                            continue
                    if random.random() < ft:
                        diff+=1
                        if diff >=4:
                            win.append(0)
                            continue
                    else:
                        if random.random() > pofr:
                            if diff == 1:
                                if random.random() < pcg2:
                                    diff -=2
                            if diff > 1:
                                if random.random() < pcg2:
                                    diff -=3
            if diff == 0:
                if random.random()<pot:
                    win.append(1)
            else:
                if diff > 0:
                    win.append(0)
                else:
                    win.append(1)
    sim.append(sum(win)/niter)
    
plt.xlabel("Win Probability")
plt.ylabel("Density")

sns.distplot(sim, hist=False, norm_hist=True)
plt.show()
