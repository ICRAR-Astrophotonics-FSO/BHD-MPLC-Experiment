from moku.instruments import Datalogger

class Moku:
    def __init__(self, ip_address, aom_frequencies):
        """Initialize the Moku device with given IP address and AOM frequencies. the AOM frequencies is a list of frequencies for different channels."""
        self.ip_address = ip_address
        self.aom_frequencies = aom_frequencies
        self.logger = Datalogger(self.ip_address, force_connect=True)
        self.logger.set_output_termination(channel=1, termination='HiZ')
        self.logger.set_output_termination(channel=2, termination='HiZ')
        #set input terminations and input attenuation
        self.logger.set_acquisition_mode('Precision')

    def dBm_to_Vpp(self, dBm):
        P_watts = 10**(dBm/10)/1000
        Vrms = (50*P_watts)**0.5
        Vpp = 2*(2)**(1/2)*Vrms
        return Vpp

    def generate_sinewave(self,channel, power):
        amplitude = self.dBm_to_Vpp(power)
        self.logger.generate_waveform(channel=channel, type='Sine', frequency=self.aom_frequencies[channel-1], amplitude=amplitude)

    def stop(self):
        self.logger.generate_waveform(channel=1, type='Sine', frequency=0, amplitude=0)
        self.logger.generate_waveform(channel=2, type='Sine', frequency=0, amplitude=0)

    def log_data(self, duration, sample_rate, notes, title_prefix):
        """todo figure out how to label the files sensibly"""
        self.logger.enable_input(channel=1)
        self.logger.enable_input(channel=2)
        self.logger.set_samplerate(sample_rate=sample_rate)
        self.logger.start_logging(duration=duration, comments=notes, file_name_prefix=title_prefix)

    def configure_source(self, power_chA_w, power_chB_w, cal_power_a_dBm, cal_power_b_dBm):
        """calibartion power is the output optical power when we drive at 0 dBm"""
        import numpy as np
        self.generate_sinewave(channel=1, power=10 * np.log10(power_chA_w * 1000) - cal_power_a_dBm)
        self.generate_sinewave(channel=2, power=10 * np.log10(power_chB_w * 1000) - cal_power_b_dBm)