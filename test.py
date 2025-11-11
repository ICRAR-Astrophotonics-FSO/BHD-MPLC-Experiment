import MokuControl

freq= 1e3
test_moku = MokuControl.Moku(ip_address='10.42.0.52', aom_frequencies=[freq, freq])
exit()
# test_moku.generate_sinewave(channel=1, power=0)
# test_moku.generate_sinewave(channel=2, power=-10)
# # cal_power_dBm = -30.0
# # test_moku.configure_source(power_chA_w=0.5e-6, power_chB_w=0.1, cal_power_a_dBm=cal_power_dBm, cal_power_b_dBm=cal_power_dBm)
# test_moku.log_data(duration=10, sample_rate=1e4, notes="test log", title_prefix="test_log")
import numpy as np
test_data = np.load("test_log2.npy")

#print the column names
print(test_data.dtype.names)
time = test_data['Time (s)']
channel1 = test_data['Input 1 (V)']
channel2 = test_data['Input 2 (V)']
import matplotlib.pyplot as plt
plt.figure()
plt.plot(time, channel1, label='Channel 1')
plt.plot(time, channel2, label='Channel 2')
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Moku Datalogger Test Data")
plt.legend()
plt.show()

# #read in a binary file
# file_name = 'test_data.li'
# with open(file_name, 'rb') as f:
#     data = f.read()
# print(f"Read {len(data)} bytes from {file_name}")
# # process the binary data as needed
# # For example, convert to a list of integers
# int_data = list(data)
# print(f"First 10 bytes as integers: {int_data[:10]}")
