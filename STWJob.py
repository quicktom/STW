
class STWJob:

    def __init__(self, deltaEt):
        self.deltaEt = deltaEt
        self.started = False

    def startJob(self, CurrentEt):
        self.startEt = CurrentEt
        self.started = True

    def stopJob(self):
        self.started = False

    def doJob(self, CurrentEt):
        if self.started:
            if CurrentEt >= self.startEt + self.deltaEt:
                self.startEt = CurrentEt
                return True

        return False