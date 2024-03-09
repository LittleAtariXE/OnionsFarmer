# OnionsBag example

from time import sleep
from onions_farmer import OnionsFarmer

# Initialize OnionsFarmer
Farmer = OnionsFarmer()

# Create an OnionsBag with 10 Onion instances. 
# The first creation might take longer due to initial Tor network connections and configurations.
bag = Farmer.makeOnionsBag(10)

# Start all Onion instances within the bag.
# This initiates the Tor connections for each Onion.
bag.start()

# Wait for user input to continue. This is a good moment to ensure all Onions have connected to the Tor network.
input("All Onions are starting. Press Enter after they've connected...")

# Print the current state of all Onion instances in the bag.
# This displays basic configurations like SOCKS and HTTP Bridge addresses, and their connection statuses.
print(bag)

input("Press Enter to make a new circuit for all Onions.")

# Request new circuits for all Onion instances in the bag.
# This can help refresh the network paths and potentially result in new Exit Node IPs.
bag.newCircuit()

input("Press Enter to check the Exit Node IPs for all Onions.")

# Trigger the process to obtain and print the Exit Node IP addresses for all Onion instances.
bag.getIP()

input("Waiting for all Onions to obtain new IP addresses...")

# Print the updated state of all Onion instances in the bag, including their new Exit Node IP addresses.
print(bag)

input("Press Enter to stop all Onions.")

# Stop all Onion instances within the bag.
# This ensures a graceful shutdown of all Tor connections.
bag.stop()

# Pause to allow time for all Onion instances to shut down properly.
sleep(2)

# Final input prompt to exit the script.
input("Press Enter to Exit. All Onions have been stopped.")
