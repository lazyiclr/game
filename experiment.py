import numpy as np
from LeducHoldem import Game
import copy
import queue
import utils
from utils import RegretSolver, exploitability, generateOutcome, RegretSolverPlus
import time

import mccfr
import Lazycfr
import cfr
import cfrnoprune
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--betm", type=int)
parser.add_argument("--Type", type=str)
parser.add_argument("--algo", type=str)
parser.add_argument("--thres", type=float)

parser.add_argument("--noprune", type=int)
args = parser.parse_args()



betm=10
if args.betm:
	betm = args.betm
savepath = "leduc_3_"+str(betm)

algo="cfr"
if args.algo:
	algo = args.algo#"cfr"
Type = "regretmatchingplus"
if args.Type:
	Type=args.Type


print(algo, Type, savepath)
if betm>7:
	game = Game(path=savepath+".npz")
else:
	game = Game( bidmaximum =betm)#path=savepath+".npz")#bidmaximum=betmpath=

print("initializing game")
print("game info:", game.numHists, game.numIsets, algo, Type)

reporttimes=[10, 10, 10, 10, 10, 20, 60, 100, 200, 300, 600, 500]
printround=[10000, 8000, 6000, 4000, 2000, 100, 50, 200, 100, 50, 1, 1]
def run(game, path="result", Type="regretmatching", solvername = "cfr"):
	thres = 1.0
	def solve(gamesolver, reporttime=60, timelim = 30000, minimum=0):
		curexpl = 100
		cumutime = 0
		timestamp = time.time()
		result = []
		expls = []
		times = []
		nodes = []
		rounds = 0
		while cumutime + time.time() - timestamp < timelim or gamesolver.nodestouched < minimum:
			rounds += 1
			if rounds % printround[betm]== 0:
				print("round ", rounds, "time", time.time() - timestamp, cumutime,  betm, solvername, Type, "betm", betm , "thres", thres, "expl", curexpl)
			gamesolver.updateAll()
			if time.time() - timestamp > reporttimes[betm]:
				cumutime += time.time() - timestamp
				expl = gamesolver.getExploitability()
				curexpl = expl
				tmpresult = (expl, cumutime, gamesolver.nodestouched)
				print("solvername", solvername, Type, "game", savepath, "expl", expl, "time", cumutime, "nodestouched", gamesolver.nodestouched, "thres", thres, "rounds", rounds)
				result.append(tmpresult)
				expls.append(expl)
				times.append(cumutime)
				nodes.append(gamesolver.nodestouched)
				timestamp = time.time()
				res_path = savepath+"_"+solvername+"_"+Type
				if solvername == "lazycfr":
					res_path+="_"+str(thres)
				if solvername == "cfr":
					res_path+="_"+str(args.noprune)
				np.savez(res_path, expl = expls, times = times, nodes = nodes)
		print("shape", len(expls), len(times), len(nodes))
		return (expls, times, nodes)
	print("initializing solver")
	solver = None
	if solvername == "cfr":
		if args.noprune:
			solver = cfrnoprune.CFR(game, Type=Type)
		else:
			solver = cfr.CFR(game, Type=Type)
	if solvername == "mccfr":
		solver = mccfr.MCCFR(game, Type=Type)
	if solvername == "lazycfr":
		if args.thres:
			thres = args.thres
		solver = Lazycfr.LazyCFR(game, Type=Type, thres =thres)


	res = solve(solver)
	return res


res = run(game, Type=Type, solvername=algo)
