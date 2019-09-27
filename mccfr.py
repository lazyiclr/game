import numpy as np
from LeducHoldem import Game
import copy
import queue
import utils
from utils import RegretSolver, exploitability, generateOutcome, RegretSolverPlus
import time



class MCCFR:
	def __init__(self, game, Type="regretmatching"):
		self.game = game

		self.Type = Type
		Solver = None
		if Type == "regretmatching":
			Solver = RegretSolver
		else:
			Solver = RegretSolverPlus

		self.solvers = []
		self.solvers.append(list(map(lambda x:  Solver(game.nactsOnIset[0][x]), range(game.numIsets[0]))))
		self.solvers.append(list(map(lambda x:  Solver(game.nactsOnIset[1][x]), range(game.numIsets[1]))))
		self.sumstgy = [[], []]
		for i, iset in enumerate(range(game.numIsets[0])):
			nact = game.nactsOnIset[0][iset]
			if game.playerOfIset[0][iset] == 0:
				self.sumstgy[0].append(np.ones(nact) / nact)
			else:
				self.sumstgy[0].append(np.ones(0))

		for i, iset in enumerate(range(game.numIsets[1])):
			nact = game.nactsOnIset[1][iset]
			if game.playerOfIset[1][iset] == 1:
				self.sumstgy[1].append(np.ones(nact) / nact)
			else:
				self.sumstgy[1].append(np.ones(0))

		self.outcome,self.reward = generateOutcome(game, self.sumstgy)
		
		self.nodestouched = 0

		self.round = -1
	def updateAll(self):
		game = self.game
		self.round += 1
		self.update(0, 0)
		self.update(1, 0)

		def updateSumStgy(owner, iset):
			player = game.playerOfIset[owner][iset]
			if player == owner:
				stgy = self.solvers[owner][iset].curstgy
				if self.Type == "regretmatching":
					self.sumstgy[owner][iset] += stgy
				else:
					self.sumstgy[owner][iset] += stgy * (self.round + 1)

				nisetid = np.random.choice(stgy.shape[0], 1, p=stgy)[0]
				niset = game.isetSucc[owner][iset][nisetid]
				updateSumStgy(owner, niset)
			else:
				for niset in game.isetSucc[owner][iset]:
					updateSumStgy(owner, niset)
		updateSumStgy(0, 0)
		updateSumStgy(1, 0)
	def update(self, owner, hist):
		
		self.nodestouched += 1
		game = self.game

		if game.isTerminal[hist] == True:
			return game.reward[hist]

		player = game.playerOfHist[hist]
		stgy = None 

		if player == 2:
			stgy = game.chanceprob[hist]
		else:
			iset = game.Hist2Iset[player][hist]
			stgy = self.solvers[player][iset].curstgy


		if player == owner:
			nacts = game.nactsOnHist[hist]
			outcome = np.zeros(nacts)
			ret = np.zeros(2)
			for a in range(nacts):
				r = self.update(owner, game.histSucc[hist][a])[owner]
				outcome[a] = r
				ret += r * stgy[a]
			iset = game.Hist2Iset[owner][hist]
			self.solvers[owner][iset].receive(outcome)
			return ret
		else:
			nacts = game.nactsOnHist[hist]
			#if player != 2:
			#	self.sumstgy[player][iset] += stgy

			nhistid = np.random.choice(nacts, 1, p=stgy)[0]
			nhist = game.histSucc[hist][nhistid]
			return self.update(owner, nhist)




	def getExploitability(self):
		stgy_prof = []
		def avg(_x):
			s = np.sum(_x)
			l = _x.shape[0]
			if s < 1e-5:
				return np.ones(l) / l
			return _x / s
		stgy_prof.append(list(map( lambda _x: avg(_x), self.sumstgy[0] )))
		stgy_prof.append(list(map( lambda _x: avg(_x), self.sumstgy[1] )))

		return exploitability(self.game, stgy_prof)

