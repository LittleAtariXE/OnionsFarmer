from time import sleep

# Import the OnionsFarmer class.
from onions_farmer import OnionsFarmer

# Initialize the OnionsFarmer instance.
farmer = OnionsFarmer()

# Create and configure a random Onion instance with default settings.
my_onion = farmer.plantOnion()

# Create and configure a specific Onion instance to listen on local port 4444 and enable console logging.
my_onion2 = farmer.plantOnion(local_socks_port=4444, print_log=True)

# Start the Onion instance's thread, initiating the Tor process.
my_onion2.start()

# Loop until the Onion instance establishes a connection with the Tor network.
while not my_onion2.isTorConn:
    sleep(0.5)
print("TOR Works !!!")

# Retrieve and print the Exit Node IP address for the Onion instance.
print("Exit Node IP: ", my_onion2.IP)

# Wait for user input and then display the Onion instance's configuration.
input("Press ENTER to display Onion configuration.")
my_onion2.infoConf()

# Wait for user input again before stopping the Onion instance's thread.
input("Press ENTER to stop the Onion.")
my_onion2.stop()

# Ensure the Onion instance has time to shut down properly.
sleep(2)

# Final user prompt before exiting the script.
input("Press ENTER to EXIT")
