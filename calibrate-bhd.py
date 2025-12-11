#this setup uses the moku pro and a custom test jig to calibrate the BHDs

#roughly we need to drive an AOM for the LO, and a second AOM for the signal
#we use a BenLog to measure the input optical powers
#we then measure the BHD output noise levels to determine the optimal operating point

from MokuControl import BHD_Calibrator_MokuPro

#parameters
SIG_AOM_FREQ = 80e6
SIG_AOM_CHANNEL = 3
SIG_BENLOG_CHANNEL = 2

LO_AOM_CHANNEL = 1
LO_BENLOG_CHANNEL = 3
LO_AOM_FREQ = 40e6

BHD_CHANNEL = 1

moku_pro_ip = "10.42.0.55"

calibrator = BHD_Calibrator_MokuPro(device_ip=moku_pro_ip,
                                    LO_AOM_FREQ=LO_AOM_FREQ,
                                    LO_AOM_CHANNEL=LO_AOM_CHANNEL,
                                    LO_BENLOG_CHANNEL=LO_BENLOG_CHANNEL,
                                    SIG_AOM_FREQ=SIG_AOM_FREQ,
                                    SIG_AOM_CHANNEL=SIG_AOM_CHANNEL,
                                    SIG_BENLOG_CHANNEL=SIG_BENLOG_CHANNEL,
                                    BHD_CHANNEL=BHD_CHANNEL)

LO_drive_power = 0 #dBm
Sig_drive_power = 0 #dBm