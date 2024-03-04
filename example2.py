from time import sleep

# Import the OnionsFarmer class for managing Tor instances.
from onions_farmer import OnionsFarmer

# Initialize the OnionsFarmer.
farmer = OnionsFarmer()

# Create two Onion instances with specified local SOCKS ports and enable logging.
my_onion1 = farmer.plantOnion(local_socks_port=4000, print_log=True)
my_onion2 = farmer.plantOnion(local_socks_port=5000, print_log=True)

# Start both Onion instances' threads, launching the Tor processes.
my_onion1.start()
my_onion2.start()

# Wait until both Onion instances have established connections to the Tor network.
while not my_onion1.isTorConn or not my_onion2.isTorConn:
    sleep(0.5)

# Confirm that both Tor instances are operational.
print("Tor Works !!")
sleep(1)

# Display the initial Exit Node IP addresses for both Onion instances.
print("my_onion1 IP: ", my_onion1.IP)
print("my_onion2 IP: ", my_onion2.IP)

# Wait for user input before requesting new circuits for both Onion instances.
input("Press ENTER to renew circuits.")
my_onion1.newCircuit()
my_onion2.newCircuit()

# Wait until both Onion instances have re-established connections with the new circuits.
while not my_onion1.isTorConn or not my_onion2.isTorConn:
    sleep(0.5)

# Confirm that new circuits have been established and display the new Exit Node IP addresses.
print("New Circuit")
print("my_onion1 IP: ", my_onion1.IP)
print("my_onion2 IP: ", my_onion2.IP)

# Wait for user input before stopping both Onion instances.
input("Press ENTER to stop Onions.")
farmer.stopOnion()

# Ensure there's enough time for both Onion instances to shut down properly.
sleep(2)

# Final input to exit the script, ensuring a graceful termination.
input("Press ENTER to exit.")

