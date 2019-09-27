import matplotlib as mpl 
mpl.use('Agg')
import pylab
import scipy.io as sio
import numpy as np
plt = mpl.pyplot

#lt.grid(True)
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--betm", type=int)
args = parser.parse_args()

cards = 3
bidmaximum	= 6
if args.betm:
	bidmaximum = args.betm	

name = "leduc_"+str(cards)+"_"+str(bidmaximum)#3_5
print("name")
path = name+".npz"
#file = np.load(path)


lower = 2
plt.title("Leduc-"+str(bidmaximum), fontsize=30)
plt.xlabel('Nodes touched', fontsize=20)
plt.ylabel('Exploitability (log 10)', fontsize=20)

mcname = name + "_mccfr_regretmatching.npz"
file = np.load(mcname)
mc_rm_expl = file['expl']
mc_rm_time = file['times']
mc_rm_nodes = file['nodes']
print("mc_rm_expl", np.log10(mc_rm_expl))



lazyname = name + "_lazycfr_regretmatching_0.1.npz"
file = np.load(lazyname)
lazy_rm_expl01 = file['expl']
lazy_rm_time01 = file['times']
lazy_rm_nodes01 = file['nodes']
#print("lazy_rm_expl", np.log10(lazy_rm_expl))


lazyname = name + "_lazycfr_regretmatching_0.01.npz"#_0.05
file = np.load(lazyname)
lazy_rm_expl001 = file['expl']
lazy_rm_time001 = file['times']
lazy_rm_nodes001 = file['nodes']


cfrname = name + "_cfr_regretmatching_1.npz"
file = np.load(cfrname)
noprune_rm_expl = file['expl']
noprune_rm_time = file['times']
noprune_rm_nodes = file['nodes']


cfrname = name + "_cfr_regretmatching_0.npz"
file = np.load(cfrname)
vanilla_rm_expl = file['expl']
vanilla_rm_time = file['times']
vanilla_rm_nodes = file['nodes']



mcname = name + "_mccfr_regretmatchingplus.npz"
file = np.load(mcname)
mc_rmplus_expl = file['expl']
mc_rmplus_time = file['times']
mc_rmplus_nodes = file['nodes']


lazyname = name + "_lazycfr_regretmatchingplus_0.1.npz"#
file = np.load(lazyname)
lazy_rmplus_expl01 = file['expl']
lazy_rmplus_time01 = file['times']
lazy_rmplus_nodes01 = file['nodes']

lazyname = name + "_lazycfr_regretmatchingplus_0.01.npz"#
file = np.load(lazyname)
lazy_rmplus_expl001 = file['expl']
lazy_rmplus_time001 = file['times']
lazy_rmplus_nodes001 = file['nodes']
#print("lazy_rmplus_nodes", np.log10(lazy_rmplus_expl))


cfrname = name + "_cfr_regretmatchingplus_0.npz"
file = np.load(cfrname)
vanilla_rmplus_expl = file['expl']
vanilla_rmplus_time = file['times']
vanilla_rmplus_nodes = file['nodes']



cfrname = name + "_cfr_regretmatchingplus_1.npz"
file = np.load(cfrname)
noprune_rmplus_expl = file['expl']
noprune_rmplus_time = file['times']
noprune_rmplus_nodes = file['nodes']

def shrink(x, y, gap=0.1):
	retx, rety = [], []

	now = 0
	for i, v in enumerate(x):
		if v - now > gap:
			rety.append(y[i])
			retx.append(v)
			now = v

	return np.array(retx), np.array(rety)

print("vanilla_rmplus_expl",  np.log10(vanilla_rmplus_expl))

nodeslim = np.inf

timelim = np.inf
upp = 0
for i, v in enumerate(mc_rm_time):
	upp = i
	if v > timelim:
		break
line_mc, = plt.plot(np.log10(mc_rm_time[lower:upp] + 1) , np.log10(mc_rm_expl[lower:upp]), color = "red")

upp = 0
for i, v in enumerate(lazy_rm_nodes01):
	upp = i
	if v > nodeslim:
		break
_x, _y = shrink(np.log10(lazy_rm_nodes01[lower:upp] + 1), np.log10(lazy_rm_expl01[lower:upp]))
line_lazy01, = plt.plot(_x, _y, color = "blue", marker="x")

upp = 0
for i, v in enumerate(lazy_rm_nodes001):
	upp = i
	if v > nodeslim:
		break

_x, _y = shrink(np.log10(lazy_rm_nodes001[lower:upp] + 1), np.log10(lazy_rm_expl001[lower:upp]))
line_lazy001, = plt.plot(_x, _y, color = "blue", marker="*")



upp = 0
for i, v in enumerate(vanilla_rm_nodes):
	upp = i
	if v > nodeslim:
		break
line_vanilla, = plt.plot(np.log10(vanilla_rm_nodes[lower:upp] + 1), np.log10(vanilla_rm_expl[lower:upp]), color = "cyan")

upp = 0
for i, v in enumerate(mc_rmplus_nodes):
	upp = i
	if v > nodeslim:
		break
line_mcplus, = plt.plot(np.log10(mc_rmplus_nodes[lower:upp] + 1), np.log10(mc_rmplus_expl[lower:upp]), color = "green")

upp = 0
for i, v in enumerate(lazy_rmplus_nodes01):
	upp = i
	if v > nodeslim:
		break

_x, _y = shrink(np.log10(lazy_rmplus_nodes01[lower:upp] + 1), np.log10(lazy_rmplus_expl01[lower:upp]))
line_lazyplus01, = plt.plot(_x, _y, color = "magenta", marker="x")


upp = 0
for i, v in enumerate(lazy_rmplus_time001):
	upp = i
	if v > timelim:
		break


_x, _y = shrink(np.log10(lazy_rmplus_time001[lower:upp] + 1), np.log10(lazy_rmplus_expl001[lower:upp]))
line_lazyplus001, = plt.plot(_x, _y, color = "magenta", marker="*")

upp = 0
for i, v in enumerate(vanilla_rmplus_time):
	if v > timelim:
		break
	upp = i
line_vanillaplus, = plt.plot(np.log10(vanilla_rmplus_time[lower:upp] + 1), np.log10(vanilla_rmplus_expl[lower:upp]), color = "black")

plt.legend((line_lazy01, line_lazy001, line_mc, line_vanilla, line_lazyplus01, line_lazyplus001, line_vanillaplus, line_mcplus), ("Lazy-CFR-0.1", "Lazy-CFR-0.01", "MC-CFR", "CFR-prune", "Lazy-CFR+-0.1", "Lazy-CFR+-0.01", "CFR+-prune", "MC-CFR+"), prop={'size':10}, loc="lower left")
print("nodes-leduc-"+str(bidmaximum)+".png")
plt.savefig("nodes-leduc-"+str(bidmaximum)+".png")
plt.close('all')
plt.title("Leduc-"+str(bidmaximum), fontsize=30)
plt.xlabel('seconds (log 10)', fontsize=20)
plt.ylabel('Exploitability (log 10)', fontsize=20)


timelim = np.inf
upp = 0
for i, v in enumerate(mc_rm_time):
	upp = i
	if v > timelim:
		break
line_mc, = plt.plot(np.log10(mc_rm_time[lower:upp] + 1) , np.log10(mc_rm_expl[lower:upp]), color = "red")

upp = 0
for i, v in enumerate(lazy_rm_time01):
	upp = i
	if v > timelim:
		break
_x, _y = shrink(np.log10(lazy_rm_time01[lower:upp] + 1), np.log10(lazy_rm_expl01[lower:upp]))
line_lazy01, = plt.plot(_x, _y, color = "blue", marker="x")

upp = 0
for i, v in enumerate(lazy_rm_time001):
	upp = i
	if v > timelim:
		break

_x, _y = shrink(np.log10(lazy_rm_time001[lower:upp] + 1), np.log10(lazy_rm_expl001[lower:upp]))
line_lazy001, = plt.plot(_x, _y, color = "blue", marker="*")



upp = 0
for i, v in enumerate(vanilla_rm_time):
	upp = i
	if v > timelim:
		break
line_vanilla, = plt.plot(np.log10(vanilla_rm_time[lower:upp] + 1), np.log10(vanilla_rm_expl[lower:upp]), color = "cyan")


upp = 0
for i, v in enumerate(noprune_rm_time):
	upp = i
	if v > timelim:
		break

_x, _y = shrink(np.log10(noprune_rm_time[lower:upp] + 1), np.log10(noprune_rm_expl[lower:upp]))
line_noprune, = plt.plot(_x,_y, color = "cyan", marker="*")


upp = 0
for i, v in enumerate(mc_rmplus_time):
	upp = i
	if v > timelim:
		break
line_mcplus, = plt.plot(np.log10(mc_rmplus_time[lower:upp] + 1), np.log10(mc_rmplus_expl[lower:upp]), color = "green")

upp = 0
for i, v in enumerate(lazy_rmplus_time01):
	upp = i
	if v > timelim:
		break

_x, _y = shrink(np.log10(lazy_rmplus_time01[lower:upp] + 1), np.log10(lazy_rmplus_expl01[lower:upp]))
line_lazyplus01, = plt.plot(_x, _y, color = "magenta", marker="x")


upp = 0
for i, v in enumerate(lazy_rmplus_time001):
	upp = i
	if v > timelim:
		break


_x, _y = shrink(np.log10(lazy_rmplus_time001[lower:upp] + 1), np.log10(lazy_rmplus_expl001[lower:upp]))
line_lazyplus001, = plt.plot(_x, _y, color = "magenta", marker="*")

upp = 0
for i, v in enumerate(vanilla_rmplus_time):
	if v > timelim:
		break
	upp = i
line_vanillaplus, = plt.plot(np.log10(vanilla_rmplus_time[lower:upp] + 1), np.log10(vanilla_rmplus_expl[lower:upp]), color = "black")


upp = 0
for i, v in enumerate(noprune_rmplus_time):
	if v > timelim:
		break
	upp = i

_x, _y = shrink(np.log10(noprune_rmplus_time[lower:upp] + 1), np.log10(noprune_rmplus_expl[lower:upp]))
line_nopruneplus, = plt.plot(_x, _y, color = "black", marker="*")

plt.legend((line_lazy01, line_lazy001, line_lazyplus01, line_lazyplus001, line_mc, line_mcplus,  line_noprune, line_vanilla,  line_nopruneplus, line_vanillaplus),\
	 ("Lazy-CFR-0.1", "Lazy-CFR-0.01", "Lazy-CFR+-0.1", "Lazy-CFR+-0.01","MC-CFR", "MC-CFR+", "CFR", "CFR-prune",  "CFR+", "CFR+-prune"), prop={'size':10}, loc="lower left")
plt.savefig("time-leduc-"+str(bidmaximum)+".png")
plt.close('all')



