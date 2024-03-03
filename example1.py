from time import sleep

# import OnionFarmer
from onions_farmer import OnionFarmer


# Make Farmer
farmer = OnionFarmer()

# Plant a random Onion
my_onion = farmer.plantOnion()

# Plant a specify Onion on local port 4444 and print all logs to console output
my_onion2 = farmer.plantOnion(local_socks_port=4444, print_log=True)

# Start onion thread
my_onion2.start()

# wait until the onion connects to TOR
while not my_onion2.isTorConn:
    sleep(0.5)
print("TOR Works !!!")

# start obtain Exit Node IP
print("Exit Node IP: ", my_onion2.IP)

# pause keypresed and print onion config
input()
my_onion2.infoConf()

# pause keypresed and stop onion thread
input()
my_onion2.stop()
input("Press ENTER to EXIT")
