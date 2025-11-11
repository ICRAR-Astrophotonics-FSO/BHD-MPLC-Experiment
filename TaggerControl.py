class TaggerControl:
    def __init__(self, trigger_levels_V=[0.06, 0.06, 0.06, 0.06]):
            import TimeTagger
            self.tagger = TimeTagger.createTimeTagger()        
            self.tagger.reset()
            for channel in range(1,5):
                    self.tagger.setTriggerLevel(channel=channel, voltage=trigger_levels_V[channel-1])
            self.cr = TimeTagger.Countrate(self.tagger, channels=[1, 2, 3, 4])


    def get_counts(self, integration_time_ps = 0.25e12, samples = 10):
        """returns a list of length samples, each entry is a list of counts with one entry for each channel"""
        data = []
        for i in range(samples):
            self.cr.clear()
            self.cr.startFor(integration_time_ps)
            self.cr.waitUntilFinished()
            data.append(self.cr.getData())
            print(data[-1]) 
        return data

    def Cleanup(self):
        """Frees the time tagger object, only call this when you are completely done with the tagger and will not use this object again"""
        import TimeTagger
        TimeTagger.freeTimeTagger(self.tagger)