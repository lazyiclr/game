import copy
import numpy as np
import time

"""
		self.numHists = 0
		self.numIsets = [0, 0]
		self.isTerminal = []
		self.reward = []
		self.histSucc = []
		self.histPar = []
		self.playerOfHist = []
		self.nactsOnHist = []
		self.Iset2Hists = [[], []]
		self.Hist2Iset = [[], []]
		self.nactsOnIset = [[], []]
		self.playerOfIset = [[], []]
		self.isetPar = [[],[]]
		self.isetSucc = [[], []]
		self.chanceprob	 = []
"""


class Game:
	def __init__(self, path=-1, cards = 3, bidmaximum=6, tosave=False):
		self.bidmaximum = bidmaximum
		self.cards = cards
		self.numHists = 0
		self.numIsets = [0, 0]
		self.isTerminal = []
		self.reward = []
		self.histSucc = []
		self.histPar = []
		self.playerOfHist = []
		self.nactsOnHist = []
		self.Iset2Hists = [[], []]#
		self.Hist2Iset = [[], []]#
		self.nactsOnIset = [[], []]
		self.playerOfIset = [[], []]
		self.isetPar = [[],[]]
		self.isetSucc = [[], []]
		self.chanceprob	 = []
		if path == -1:
			self.genGame(np.array([[-1]]), np.array([[-1]]), [np.array([-1]), np.array([-1])], [np.array([-1]), np.array([-1])], 0, np.array([[[-1]], [[-1]]]), -1, np.array([-1, -1]), np.array([0, 0]))

			for p in range(2):
				for iset in range(self.numIsets[p]):
					self.Iset2Hists[p][iset] = self.Iset2Hists[p][iset].astype(int)
		else:
			file = np.load(path)

			self.numHists = file['numHists']
			self.numIsets = file['numIsets']
			self.isTerminal = file['isTerminal']
			self.reward = file['reward']
			self.histSucc = file['histSucc']
			self.histPar = file['histPar']
			self.playerOfHist = file['playerOfHist']
			self.nactsOnHist = file['nactsOnHist']
			self.Iset2Hists = [file['Iset2Hists0'], file['Iset2Hists1']]

			self.Hist2Iset = file['Hist2Iset']
			self.nactsOnIset = file['nactsOnIset']
			self.playerOfIset = file['playerOfIset']
			self.isetPar = file['isetPar']
			self.isetSucc = file['isetSucc']
			self.chanceprob = file['chanceprob']
			for h in range(self.numHists):
				self.Hist2Iset[0][h] = int(self.Hist2Iset[0][h])
				self.Hist2Iset[1][h] = int(self.Hist2Iset[1][h])
			for p in range(2):
				for iset in range(self.numIsets[p]):
					self.Iset2Hists[p][iset] = self.Iset2Hists[p][iset].astype(int)
		if tosave:
			np.savez("leduc_"+str(cards)+"_"+str(bidmaximum),  numHists= self.numHists, isTerminal= self.isTerminal, reward= self.reward, 
			histSucc= self.histSucc, histPar= self.histPar, playerOfHist= self.playerOfHist, nactsOnHist= self.nactsOnHist, Iset2Hists0= self.Iset2Hists[0], Iset2Hists1= self.Iset2Hists[1], 
			Hist2Iset= self.Hist2Iset, nactsOnIset= self.nactsOnIset, playerOfIset= self.playerOfIset, isetPar= self.isetPar, isetSucc= self.isetSucc, numIsets= self.numIsets, 
			chanceprob= self.chanceprob)


	def printGame(self):
		print("numHists", self.numHists, "numIsets", self.numIsets)
		print("histPar", list(enumerate(self.histPar)))
		print("histSucc", list(enumerate(self.histSucc)))
		print("isetPar 0", list(enumerate(self.isetPar[0])))
		print("isetSucc 0", list(enumerate(self.isetSucc[0])))
		print("isTerminal", self.isTerminal)
		print("Hist2Iset", self.Hist2Iset)
		print("Iset2Hists", self.Iset2Hists[0])
		print("reward", list(enumerate(self.reward)))
		print("chanceprob", list(enumerate(self.chanceprob)))
		print("playerOfHist", self.playerOfHist)
		print("playerOfIset 0", self.playerOfIset[0])
		print("nactsOnIset 0", self.nactsOnIset[0])
		print("nactsOnIset 1", self.nactsOnIset[1])


	
	def genGame(self, parhists, hacts, parisets, iacts, depth, privatecard, publiccard, bids, quit, isTerminal=False, player=2):
		x, y = parhists.shape

		histids = np.ones((x, y))
		isetids = [np.ones(x), np.ones(y)]




		obs = [True, True]


		if privatecard[0][0][0] == -1:
			obs[1] = False
		elif privatecard[1][0][0] == -1:
			obs[0] = False

		def genNactsOnHist():
			if isTerminal:
				return 0
			if player == 2:
				return int(self.cards)
			if bids[1 - player] == -1:
				return int(self.bidmaximum + 1)
			return 2 + int(self.bidmaximum - bids[1 - player])

		def genNactsOnIset(owner):
			if isTerminal:
				return 0
			if obs[owner] == False:
				return 1
			return genNactsOnHist()



		#print("isTerminal", isTerminal, "privatecard", privatecard, "publiccard", publiccard, "bids", bids, "quit", quit, "obs", obs)

		for i in range(x):
			self.isetSucc[0].append([])
			self.isetPar[0].append(0)
			self.playerOfIset[0].append(0)
			self.nactsOnIset[0].append(0)
			self.Iset2Hists[0].append(0)
			isetids[0][i] = int(self.numIsets[0])
			self.isetPar[0][self.numIsets[0]] = (int(parisets[0][i]), int(iacts[0][i]))
			self.playerOfIset[0][self.numIsets[0]] = player


			self.nactsOnIset[0][self.numIsets[0]] = genNactsOnIset(0)
			if parisets[0][i]>=0:
				self.isetSucc[0][int(parisets[0][i])].append(int(isetids[0][i]))
			self.numIsets[0] += 1

		for i in range(y):
			self.isetSucc[1].append([])
			self.isetPar[1].append(0)
			self.playerOfIset[1].append(0)
			self.nactsOnIset[1].append(0)
			self.Iset2Hists[1].append(0)
			isetids[1][i] = int(self.numIsets[1])
			self.isetPar[1][self.numIsets[1]] = (int(parisets[1][i]), int(iacts[1][i]))
			self.playerOfIset[1][self.numIsets[1]] = player

			self.nactsOnIset[1][self.numIsets[1]] = genNactsOnIset(1)
			if parisets[1][i]>=0:
				self.isetSucc[1][int(parisets[1][i])].append(int(isetids[1][i]))
			self.numIsets[1] += 1


		for i in range(x):
			for j in range(y):
				self.isTerminal.append(False)
				self.reward.append((np.inf, -np.inf))
				self.histSucc.append([])
				self.histPar.append(0)
				self.playerOfHist.append(0)
				self.nactsOnHist.append(0)
				self.Hist2Iset[0].append(0)
				self.Hist2Iset[1].append(0)
				histids[i][j] = int(self.numHists)
				self.histPar[self.numHists] = (int(parhists[i][j]), int(hacts[i][j]))
				self.playerOfHist[self.numHists] = player
				self.isTerminal[self.numHists]  = isTerminal
				self.Hist2Iset[0][self.numHists] = int(isetids[0][i])
				self.Hist2Iset[1][self.numHists] = int(isetids[1][j])

				if player == 2:
					if privatecard[0][i][j] == -1:
						self.chanceprob.append(np.ones(self.cards) / self.cards)
					
					elif privatecard[1][i][j] == -1:
						self.chanceprob.append(np.ones(self.cards))
						for _a in range(self.cards):
							if _a == int(privatecard[0][i][j]):
								self.chanceprob[int(self.numHists)][_a] = 1.0/(2 * self.cards - 1)
							else:
								self.chanceprob[int(self.numHists)][_a] = 2.0/(2 * self.cards - 1)
					else:
						self.chanceprob.append(np.ones(self.cards))
						for _a in range(self.cards):
							_cnt = 2
							if _a == int(privatecard[0][i][j]):
								_cnt -= 1
							if _a == int(privatecard[1][i][j]):
								_cnt -= 1
							self.chanceprob[int(self.numHists)][_a] = _cnt / (2 * self.cards -2)
				else:
					self.chanceprob.append(0)

				"""
				if isTerminal:
					self.nactsOnHist[self.numHists] = 0
				else:
					self.nactsOnHist[self.numHists] = 1 - (self.bidmaximum - bids[1 - player])
				"""
				self.nactsOnHist[self.numHists] = genNactsOnHist()
				if parhists[i][j] >= 0:
					self.histSucc[int(parhists[i][j])].append(int(histids[i][j]))
				self.numHists += 1

		for i in range(x):
			self.Iset2Hists[0][int(isetids[0][i])] = histids[i, :].astype(int)
		for i in range(y):
			self.Iset2Hists[1][int(isetids[1][i])] = histids[:, i].astype(int)


		if isTerminal == True:
			for i in range(x):
				for j in range(y):
					win = 1
					if quit[0]:
						win = -1
					elif quit[1]:
						win = 1
					elif privatecard[0][i][j] == privatecard[1][i][j]:
						win = 0
					elif privatecard[0][i][j] == publiccard:
						win = 1
					elif privatecard[1][i][j] == publiccard:
						win = -1
					elif privatecard[0][i][j] > privatecard[1][i][j]:
						win = 1
					elif privatecard[0][i][j] < privatecard[1][i][j]:
						win = -1
					if win == 0:
						self.reward[int(histids[i][j])] = (0, 0)
					elif win == 1:
						self.reward[int(histids[i][j])] = (bids[1]+0.5, -bids[1]-0.5)
					elif win == -1:
						self.reward[int(histids[i][j])] = (-bids[0]-1, bids[0]+1)
			return #histids, isetids



		if obs[0] == False:
			nxtparhist = np.zeros((x, 0))
			nxthacts = np.zeros((x, 0))
			nxtpariset = [isetids[0].copy(), np.zeros(0)]
			nxtiacts = [np.zeros(x), np.zeros(0)]

			nxtprivatecard = np.zeros((2, x,0))
			nxtpubliccard = -1
			nxtbid = -1 * np.ones(2)
			nxtquit = np.zeros(2)

			for i in range(self.cards):
				nxtparhist = np.concatenate((nxtparhist, histids), axis = 1)
				nxthacts = np.concatenate((nxthacts, i * np.ones((x, y))), axis = 1)
				nxtpariset[1] = np.concatenate((nxtpariset[1], isetids[1]))
				nxtiacts[1] = np.concatenate((nxtiacts[1], i * np.ones(y)))

				tmpprivate0 = privatecard[0, :,:]
				tmpprivate1 = i * np.ones((x, y))
				tmpprivate = np.array((tmpprivate0, tmpprivate1))
				nxtprivatecard = np.concatenate((nxtprivatecard, tmpprivate), axis = 2)


			self.genGame(nxtparhist, nxthacts, nxtpariset, nxtiacts, depth + 1, nxtprivatecard, nxtpubliccard, nxtbid, nxtquit, isTerminal=False, player=0)

		elif obs[1] == False:

			nxtparhist = np.zeros((0, y))
			nxthacts = np.zeros((0, y))
			nxtpariset = [np.zeros(0), isetids[1].copy()]
			nxtiacts = [np.zeros(0), np.zeros(y)]


			nxtprivatecard = np.zeros((2, 0, y))
			nxtpubliccard = -1
			nxtbid = -1 * np.ones(2)
			nxtquit = np.zeros(2)

			for i in range(self.cards):
				nxtparhist = np.concatenate((nxtparhist, histids), axis = 0)
				nxthacts = np.concatenate((nxthacts, i * np.ones((x, y))), axis = 0)
				nxtpariset[0] = np.concatenate((nxtpariset[0], isetids[0]))
				nxtiacts[0] = np.concatenate((nxtiacts[0], i * np.ones(x)))

				tmpprivate1 = privatecard[1, :,:]
				tmpprivate0 = i * np.ones((x, y))
				tmpprivate = np.array((tmpprivate0, tmpprivate1))
				nxtprivatecard = np.concatenate((nxtprivatecard, tmpprivate), axis = 1)
			self.genGame(nxtparhist, nxthacts, nxtpariset, nxtiacts, depth + 1, nxtprivatecard, nxtpubliccard, nxtbid, nxtquit, isTerminal=False, player=2)

		else:
			nacts = genNactsOnHist()


			for i in range(nacts):
				nxtparhist = histids.copy()
				nxthacts = i * np.ones((x, y))
				nxtpariset = [isetids[0].copy(), isetids[1].copy() ]
				nxtiacts = [i * np.ones(x), i * np.ones(y)]


				nxtprivatecard = privatecard.copy()
				nxtpubliccard = -1
				if player == 2:
					nxtpubliccard = i
				else:
					nxtpubliccard = publiccard

				nxtbid = bids.copy()
				if player != 2 and i != nacts - 1:
					if nxtbid[1 - player] == -1:
						nxtbid[player] = i + 1
					else:
						nxtbid[player] = nxtbid[1 - player] + i
				nxtquit = quit.copy()
				if player != 2 and i == nacts - 1:
					nxtquit[player] = 1
					if bids[player] == -1:
						bids[player] = 0

				nxtisTerminal=None 
				nxtplayer = None
				if player == 2:
					nxtisTerminal = False
					nxtplayer = 0
				elif nxtquit[0] or nxtquit[1]:
					nxtisTerminal = True
					nxtplayer = 2
				elif bids[0] == nxtbid[0] and bids[1] == nxtbid[1]:
					nxtplayer = 2
					if publiccard == -1:
						nxtisTerminal = False
					else:
						nxtisTerminal = True
				else:
					nxtisTerminal = False
					nxtplayer = 1 - player

				self.genGame(nxtparhist, nxthacts, nxtpariset, nxtiacts, depth + 1, nxtprivatecard, nxtpubliccard, nxtbid, nxtquit, isTerminal=nxtisTerminal, player=nxtplayer)

#for i in range(5, 11):
#	game = Game(bidmaximum=i)
#	print(i, int(time.time()) % 100000, game.numHists)
#game.printGame()