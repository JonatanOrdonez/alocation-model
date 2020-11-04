import numpy as np
import constants as ct
import exceptions
from reader import readCSV
from utils import gompertzNewCases
import lpmodel


class PatientsAllocationModel:
    def __init__(self):
        self.sigmas = readCSV(ct.sigmasPath)[0]
        self.thetas = readCSV(ct.thetasPath)[0]
        self.gompertzParams = readCSV(ct.gompertzPath)
        self.costs = readCSV(ct.costsPath)
        self.elapsedDays = ct.getElapsedDays()
        self.bethas = np.zeros((ct.citiesLength, ct.days))
        self.alphas = np.zeros((ct.citiesLength, ct.days))

    def readSigmas(self, sigmasArray):
        sigmasArray = np.array(sigmasArray).astype(np.float)
        if sigmasArray.shape != (ct.citiesLength,):
            raise exceptions.InvalidArrayShape
        self.sigmas = sigmasArray

    def readThetas(self, thetasArray):
        thetasArray = np.array(thetasArray).astype(np.float)
        if thetasArray.shape != (ct.citiesLength,):
            raise exceptions.InvalidArrayShape
        self.thetas = thetasArray

    def readGompertzParams(self, gompertzArray):
        gompertzArray = np.array(gompertzArray).astype(np.float)
        if gompertzArray.shape != (ct.gompertzParamsLength, ct.citiesLength):
            raise exceptions.InvalidArrayShape

        self.gompertzParams = gompertzArray

    def execute(self):
        self.__getPatientsForecasts()
        self.__getForecastsForFreeICU()
        self.lpModel = lpmodel.Lpmodel(
            self.costs, self.sigmas, self.thetas, self.alphas, self.bethas)
        return self.lpModel.execute()

    def __getPatientsForecasts(self):
        for i in ct.citiesIndex:
            for t in ct.daysIndex:
                a = self.gompertzParams[i][0]
                b = self.gompertzParams[i][1]
                r = self.gompertzParams[i][2]
                probHospital = self.gompertzParams[i][3]
                probICU = self.gompertzParams[i][5]
                day = self.elapsedDays + t

                newDiagnostics = gompertzNewCases(a, b, r, day)
                self.bethas[i][t] = int(
                    newDiagnostics * probHospital * probICU)

    def __getForecastsForFreeICU(self):
        for i in ct.citiesIndex:
            for t in ct.daysIndex:
                if t < ct.epsilon:
                    a = self.gompertzParams[i][0]
                    b = self.gompertzParams[i][1]
                    r = self.gompertzParams[i][2]
                    probHospital = self.gompertzParams[i][3]
                    probICU = self.gompertzParams[i][5]
                    day = self.elapsedDays + t

                    previousDiagnostics = gompertzNewCases(a, b, r, day)
                    self.alphas[i][t] = int(previousDiagnostics *
                                            probHospital * probICU)
                else:
                    self.alphas[i][t] = 0


model = PatientsAllocationModel()
finalMatrix = model.execute()
print(finalMatrix)
