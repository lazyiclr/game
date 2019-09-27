import numpy as np
from LeducHoldem import Game
import copy
import queue
import utils
from utils import RegretSolver, generateOutcome, exploitability, RegretSolverPlus
import time


class LazyCFR:
	def __init__(self, game, Type="regretmatching", thres = 0.0):
		print("initializing solver")
		self.thres = thres
		self.time = 0

		self.game = game

		self.Type = Type
		Solver = None
		if Type == "regretmatching":
			Solver = RegretSolver
		else:
			solver = RegretSolverPlus


		self.cfvCache = []
		self.cfvCache.append(list(map(lambda x:  np.zeros(game.nactsOnHist[x]), range(game.numHists))))
		self.cfvCache.append(list(map(lambda x:  np.zeros(game.nactsOnHist[x]), range(game.numHists))))


		self.probNotUpdated = [np.zeros((game.numHists, 2)), np.zeros((game.numHists, 2))]
		self.probNotPassed = [np.zeros((game.numHists, 2)), np.zeros((game.numHists, 2))]
		self.histflag = [-1 * np.ones(game.numHists), -1 * np.ones(game.numHists)]
		self.isetflag = [-1 * np.ones(game.numIsets[0]), -1 * np.ones(game.numIsets[1])]


		self.reachp = [np.zeros(game.numIsets[0]), np.zeros(game.numIsets[1])]

		self.solvers = []
		self.solvers.append(list(map(lambda x:  RegretSolver(game.nactsOnIset[0][x]), range(game.numIsets[0]))))
		self.solvers.append(list(map(lambda x:  RegretSolver(game.nactsOnIset[1][x]), range(game.numIsets[1]))))

		"""
		"""
		self.stgy = [[], []]
		for i, iset in enumerate(range(game.numIsets[0])):
			nact = game.nactsOnIset[0][iset]
			if game.playerOfIset[0][iset] == 0:
				self.stgy[0].append(np.ones(nact) / nact)
			else:
				self.stgy[0].append(np.ones(0))

		for i, iset in enumerate(range(game.numIsets[1])):
			nact = game.nactsOnIset[1][iset]
			if game.playerOfIset[1][iset] == 1:
				self.stgy[1].append(np.ones(nact) / nact)
			else:
				self.stgy[1].append(np.ones(0))
		self.round = -1
		self.nodestouched = 0
		self.outcome, self.reward = generateOutcome(game, self.stgy)


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

	def receiveProb(self, owner, histind, prob):
		self.probNotPassed[owner][histind] += prob
		self.probNotUpdated[owner][histind] += prob
		self.nodestouched += 1

	def passProbOnHist(self, owner, histind):
		game = self.game
		if game.isTerminal[histind]:
			return 

		parhind, pactind = game.histPar[histind]
		if parhind != -1 and self.histflag[owner][parhind] < self.round: 
			self.passProbOnHist(owner, parhind)

		player = game.playerOfHist[histind]
		stgy = None
		if player == 2:
			stgy = game.chanceprob[histind]			
		else:
			isetind = game.Hist2Iset[player][histind]
			stgy = self.solvers[player][isetind].curstgy 
		for aind, nxthind in enumerate(game.histSucc[histind]):
			tmp = self.probNotPassed[owner][histind].copy()
			if player == owner:
				tmp[owner] *= stgy[aind]
			else:
				tmp[1 - owner] *= stgy[aind]
			self.cfvCache[owner][nxthind] += np.array(self.outcome[nxthind]) * tmp[1 - owner]
			self.receiveProb(owner, nxthind, tmp)
		self.probNotPassed[owner][histind] = np.zeros(2)
		self.histflag[owner][histind] = self.round


	def updateIset(self, owner, isetind):
		self.isetflag[owner][isetind] = self.round
		game = self.game
		if game.playerOfIset[owner][isetind] == owner:
			sumcfv = np.zeros(game.nactsOnIset[owner][isetind])
			weight = 0
			for innerhind, hind in enumerate(game.Iset2Hists[owner][isetind]):
				sumcfv += self.cfvCache[owner][hind]
				weight = self.probNotUpdated[owner][hind][owner]

				self.cfvCache[owner][hind] *= 0.0
			if owner == 1:
				sumcfv *= -1.0
			self.sumstgy[owner][isetind] += self.reachp[owner][isetind] * self.solvers[owner][isetind].curstgy
			self.solvers[owner][isetind].receive(sumcfv, weight=weight)

		for innerhind, hind in enumerate(game.Iset2Hists[owner][isetind]):
			self.probNotUpdated[owner][hind] = np.zeros(2)
			self.passProbOnHist(0, hind)
			self.passProbOnHist(1, hind)
		nacts = game.nactsOnIset[owner][isetind]
		for innerIind, nxtisetind in enumerate(game.isetSucc[owner][isetind]):
			sumprob = 0.0
			nxthists = game.Iset2Hists[owner][nxtisetind]
			if game.isTerminal[nxthists[0]] == False:
				for nxth in game.Iset2Hists[owner][nxtisetind]:
					sumprob += self.probNotUpdated[owner][nxth][1- owner]
				if game.playerOfIset[owner][isetind] == owner:
					self.reachp[owner][nxtisetind] += self.reachp[owner][isetind] * self.solvers[owner][isetind].curstgy[innerIind]
				else:
					self.reachp[owner][nxtisetind] += self.reachp[owner][isetind]
				if sumprob > self.thres:
					self.updateIset(owner, nxtisetind)
		self.reachp[owner][isetind] = 0


	def updateAll(self):
		t1 = time.time()
		game = self.game
		self.round += 1
		if self.Type == "regretmatching":
			self.reachp[0][0] += 1
			self.reachp[1][0] += 1
		else:
			self.reachp[0][0] += self.round
			self.reachp[1][0] += self.round
		self.receiveProb(0, 0, np.ones(2))
		self.receiveProb(1, 0, np.ones(2))
		self.updateIset(0, 0)
		self.updateIset(1, 0)

		"""
		def updstgy(owner, iset):
			hists = game.Iset2Hists[owner][iset]
			if game.isTerminal[hists[0]]:
				return
			if self.isetflag[owner][iset] < self.round:
				return
			if game.playerOfIset[owner][iset] == owner:
				self.stgy[owner][iset] = self.solvers[owner][iset].curstgy
			nacts = game.nactsOnIset[owner][iset]
			for a in range(nacts):
				updstgy(owner, game.isetSucc[owner][iset][a])
		updstgy(0, 0)
		updstgy(1, 0)
		"""
		


		def updateoutcome(hist):
			if game.isTerminal[hist]:
				return
			if self.histflag[0][hist] < self.round:
				return
			self.reward[hist] = 0.0
			nacts = game.nactsOnHist[hist]
			_stgy = None 
			player = game.playerOfHist[hist]
			if player == 2:
				_stgy = game.chanceprob[hist]
			else:
				piset = game.Hist2Iset[player][hist]
				_stgy = self.solvers[player][piset].curstgy #self.stgy[player][piset]
			for a in range(nacts):
				nh = game.histSucc[hist][a]
				updateoutcome(nh)
				self.outcome[hist][a] = self.reward[nh]
				self.reward[hist] += _stgy[a] * self.reward[nh]
		updateoutcome(0)


		self.time += time.time() - t1

	def getAvgStgy(self, owner, iset):
		game = self.game
		player = game.playerOfIset[owner][iset]
		if player == owner:
			self.sumstgy[owner][iset] += self.reachp[owner][iset] * self.solvers[owner][iset].curstgy
		for _i, niset in enumerate(game.isetSucc[owner][iset]):
			if player == owner:
				self.reachp[owner][niset] += self.reachp[owner][iset] * self.solvers[owner][iset].curstgy[_i]
			else:
				self.reachp[owner][niset] += self.reachp[owner][iset]
			self.getAvgStgy(owner, niset)
		self.reachp[owner][iset] = 0

	def getExploitability(self):
		stgy_prof = []
		def avg(_x):
			s = np.sum(_x)
			l = _x.shape[0]
			if s < 1e-5:
				return np.ones(l) / l
			return _x / s

		self.getAvgStgy(0, 0)
		self.getAvgStgy(1, 0)
		stgy_prof.append(list(map( lambda _x: avg(_x), self.sumstgy[0] )))
		stgy_prof.append(list(map( lambda _x: avg(_x), self.sumstgy[1] )))

		return exploitability(self.game, stgy_prof)


"""
game = Game(bidmaximum=5)#maximumhists=maximumhists)
print(game.numHists, game.numIsets)

lazycfr = LazyCFR(game, Type="regretmatchingplus")

T = 10000
for r in range(T):
	lazycfr.updateAll()

	if r % 300 == 0:
		print("time 0", time.time())
		print("exploitability:", lazycfr.getExploitability(), lazycfr.time)
		print("time 1", time.time())
"""