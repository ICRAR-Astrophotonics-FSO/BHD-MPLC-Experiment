from moku.instruments import Datalogger
import numpy as np

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




class BHD_Calibrator_MokuPro:

    def dBm_to_Vpp(self, dBm):
        P_watts = 10**(dBm/10)/1000
        Vrms = (50*P_watts)**0.5
        Vpp = 2*(2)**(1/2)*Vrms
        return Vpp
    
    def BenLogV_to_dBm(self, V):
        return 50 * V - 114.5425

    def __init__(self, device_ip, LO_AOM_FREQ, LO_AOM_CHANNEL, LO_BENLOG_CHANNEL,
                 SIG_AOM_FREQ, SIG_AOM_CHANNEL, SIG_BENLOG_CHANNEL, BHD_CHANNEL):
        from moku.instruments import MultiInstrument
        self.LO_AOM_CHANNEL = LO_AOM_CHANNEL
        self.LO_BENLOG_CHANNEL = LO_BENLOG_CHANNEL
        self.SIG_AOM_CHANNEL = SIG_AOM_CHANNEL
        self.SIG_BENLOG_CHANNEL = SIG_BENLOG_CHANNEL
        self.BHD_CHANNEL = BHD_CHANNEL
        self.LO_AOM_FREQ = LO_AOM_FREQ
        self.SIG_AOM_FREQ = SIG_AOM_FREQ

        #now confiugre 3 instruments, a spectrum analyzer to measure the BHD output noise, an oscilloscope to monitor the benlogs and a waveform generator to drive the AOMs
        self.multi = MultiInstrument(device_ip, platform_id=4, force_connect=True)
        #SLOT 1: Spectrum Analyzer
        #SLOT 2: Waveform Generator
        #SLOT 3: OSCILLOSCOPE 
        self.spectrum_analyzer = self.multi.set_instrument(1, 'SpectrumAnalyzer')
        self.waveform_generator = self.multi.set_instrument(2, 'WaveformGenerator')
        self.oscilloscope = self.multi.set_instrument(3, 'Oscilloscope')

        #configure connections

        bhd_connect = dict(source=f"Input{self.BHD_CHANNEL}", destination="Slot1InA")
        lo_benlog_connect = dict(source=f"Input{self.LO_BENLOG_CHANNEL}", destination="Slot3InA")
        sig_benlog_connect = dict(source=f"Input{self.SIG_BENLOG_CHANNEL}", destination="Slot3InB")
        lo_aom_connect = dict(source=f"Slot2OutA", destination=f"Output{self.LO_AOM_CHANNEL}")
        sig_aom_connect = dict(source=f"Slot2OutB", destination=f"Output{self.SIG_AOM_CHANNEL}")

        connections = [bhd_connect, lo_benlog_connect, sig_benlog_connect, lo_aom_connect, sig_aom_connect]
        self.multi.set_connections(connections=connections)

        #set frontends
        self.multi.set_frontend(self.BHD_CHANNEL, "50Ohm", "AC", "0dB")
        self.multi.set_frontend(self.LO_BENLOG_CHANNEL, "1MOhm", "DC", "-10dB")
        self.multi.set_frontend(self.SIG_BENLOG_CHANNEL, "1MOhm", "DC", "-10dB")
        self.multi.set_output(self.LO_AOM_CHANNEL, "14dB")
        self.multi.set_output(self.SIG_AOM_CHANNEL, "14dB")
        self.waveform_generator.disable_modulation(channel=LO_AOM_CHANNEL)
        self.waveform_generator.disable_modulation(channel=SIG_AOM_CHANNEL)
        self.oscilloscope.set_timebase(-1, 1)
        self.oscilloscope.enable_rollmode(roll=True)

        self.spectrum_analyzer.set_span(300e6)

    
    def MeasureResponse(self, LO_drive_power, Sig_drive_power):
        #configure AOM drives
        self.waveform_generator.generate_waveform(channel=self.LO_AOM_CHANNEL, type='Sine', frequency=self.LO_AOM_FREQ, amplitude=self.dBm_to_Vpp(LO_drive_power))
        self.waveform_generator.generate_waveform(channel=self.SIG_AOM_CHANNEL, type='Sine', frequency=self.SIG_AOM_FREQ, amplitude=self.dBm_to_Vpp(Sig_drive_power)) 
        #measure benlogs
        benlog_measurements = self.oscilloscope.get_data()
        LO_power_dBm= self.BenLogV_to_dBm(np.mean(benlog_measurements['ch1'])) 
        Sig_power_dBm = self.BenLogV_to_dBm(np.mean(benlog_measurements['ch2']))

        #measure BHD noise
        bhd_data = self.spectrum_analyzer.get_data()
        import matplotlib.pyplot as plt
        print("Estimated LO Power (dBm): ", LO_power_dBm)
        print("Estimated Signal Power (dBm): ", Sig_power_dBm)
        plt.semilogy(bhd_data['frequency'], bhd_data['ch1'])
        plt.show()
