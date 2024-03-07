<div id="intro" align="center">
  <h1 align="center">Onions Farmer</h1>
  <p>A powerful utility for managing multiple Tor instances</p>
  <img src="img/f1.png" alt="OnionFarmer Intro">
</div>
<div id="description">
  <h2>About OnionsFarmer</h2>
  <p>OnionsFarmer empowers users to cultivate "Onions" — a playful metaphor for independent Tor network instances. This sophisticated Python utility facilitates the simultaneous management of multiple Tor processes. For optimal functionality, it requires the Tor software installation on the user's system and proper user permissions. OnionsFarmer streamlines the initiation and supervision of Tor network connections, enhancing both security and usability.</p>
  <h2>Key Features</h2>
  <ul>
    <li><strong>Create Tor Instances:</strong> With the <code>plantOnion</code> method, users can seed new, individually manageable Tor instances.</li>
    <li><strong>Independent Operation:</strong> Each Onion instance operates independently, providing detailed control over its respective Tor process.</li>
    <li><strong>Graceful Shutdown:</strong> For orderly Tor process termination, employing the <code>Onion.stop()</code> method is advised before exiting the application.</li>
    <li><strong>Direct Control and Termination:</strong> The <code>plantOnion</code> method returns an Onion instance along with an external stop event, enabling straightforward control and shutdown operations.</li>
    <li><strong>Persistent Configuration:</strong> OnionsFarmer auto-generates a "ONIONS" directory for storing logs, configuration, and Tor library files. Reutilizing the same Tor instance names can speed up subsequent startups by leveraging existing files.</li>
    <li><strong>OnionsBag - Bulk Management:</strong> A convenient feature for handling multiple Tor instances collectively. It allows for the swift creation and management of several Onions, simplifying the orchestration of numerous Tor connections.</li>
  </ul>
</div>

<div id="toc">
  <h2 align="center">Contents</h2>
  <div align="center">
    <a href="#requirements">Requirements</a> &nbsp;|&nbsp;
    <a href="#installation">Install</a>  &nbsp;|&nbsp;
    <a href="#methods"> Onion Farmer Methods</a>  &nbsp;|&nbsp;
    <br>
    <a href="#onionobj"> Onion</a>  &nbsp;|&nbsp;
    <a href="#onionobj"> Onions Bag</a>  &nbsp;|&nbsp;
    <br/>
  </div>
</div>

<div id="requirements">
    <h2>Requirements</h2>
    <p>To ensure the proper functioning of Onions Farmer, the following requirements must be met:</p>
    <ul>
        <li>Tor Software Installed - Onions Farmer relies on direct interactions with the Tor network, requiring the Tor software to be installed on the user's system.</li>
        <li>Python 3.11 or Newer - Utilizes features and syntax introduced in Python 3.11, necessitating this or a newer version of Python.</li>
        <li>Python 'socks' Library - This dependency is crucial for managing SOCKS protocol interactions, allowing Onions Farmer to communicate over Tor network connections effectively.</li>
    </ul>
</div>

<div id="installation">
    <h2>Installation</h2>
    <p>OnionsFarmer is versatile and can function both as a standalone application or as an imported module in your projects. The choice of how you wish to use it is yours.</p>
    <h3>Downloading OnionsFarmer:</h3>
    <p>To get started with OnionsFarmer, clone the repository using Git:</p>
    <pre><code>git clone https://github.com/LittleAtariXE/OnionsFarmer.git</code></pre>
    <h3>Installing Dependencies:</h3>
    <p>After cloning the repository, navigate to the OnionsFarmer directory and install the necessary Python libraries by running:</p>
    <pre><code>pip install -r requirements.txt</code></pre>
</div>

<div id="methods">
  <h2 align="center">Onions Farmer Methods</h2>
  <div align="center">
    <img src="img/f2.png" alt="Onions Market">
  </div>
  <div id="method-plantOnion">
      <h2>OnionsFarmer.plantOnion() Method</h2>
      <p>The <code>plantOnion()</code> method, literally "plant an onion", is responsible for creating a new <code>Onion</code> object, which represents an instance of Tor. This method offers a variety of parameters for customization:</p>
      <ul>
          <li><strong>name</strong>: An optional parameter that assigns a reference name to the Onion instance. This name can be used later with the <code>getOnion()</code> method to retrieve the object. If not provided, a default name is generated.</li>
          <li><strong>local_socks_port</strong>: Specifies the local port for the Tor SOCKS proxy. This parameter determines on which local port the SOCKS proxy will be created.</li>
          <li><strong>outside_socks_ip</strong>: Indicates the IP address and port (in the format "192.168.0.23:8000") to be used for creating a Tor SOCKS proxy accessible from other machines.</li>
          <li><strong>torrc</strong>: An optional parameter that allows specifying a path to a custom <code>torrc</code> file. If this parameter is omitted, a new torrc file will be generated automatically.</li>
          <li><strong>print_log</strong>: Enables direct printing of Tor logs to the console. This is not recommended for multiple instances due to potential text flooding on the screen. Note: Each <code>Onion</code> object maintains its own log file.</li>
          <li><strong>http_bridge</strong>: Creates a special HTTP Proxy server linked to the Tor SOCKS proxy. This parameter accepts three types of values:
              <ul>
                  <li>A specific IP and port (e.g., "192.168.0.22:5000") will create an HTTP -> SOCKS bridge on the specified port, accessible from other machines.</li>
                  <li>A port number only (e.g., "5000") will create the HTTP proxy on the local port 5000.</li>
                  <li>The value "random" will establish the HTTP proxy on a randomly selected port.</li>
              </ul>
          </li>
          <li><strong>config</strong>: A dictionary that may contain additional optional parameters, which will be detailed further in this documentation.</li>
      </ul>
      <p>This method allows for flexible creation and management of Tor instances, catering to a wide range of use cases and preferences.</p>
  </div>
  <div id="instance-naming">
    <h2>Optimizing Tor Connection Initialization</h2>
    <p>When selecting names for Onion instances, either through <code>plantOnion()</code> or <code>makeOnionsBag()</code>, consistently using the same names can lead to faster connection and configuration times with the Tor network. This efficiency gain is due to the Tor library files already being downloaded. The difference becomes noticeable when rerunning the same script. The initial startup always takes the longest, as Tor needs to download all necessary files, descriptors, etc.</p>
  </div>

  <div id="method-getOnion">
    <h2>OnionsFarmer.getOnion() Method</h2>
    <p>The <code>getOnion()</code> method retrieves an <code>Onion</code> object previously created by the OnionsFarmer. This method facilitates access to individual Onion instances for management and interaction:</p>
    <ul>
        <li><strong>name</strong>: The name of the previously created Onion instance. Providing this name as a parameter allows for the retrieval of the specific Onion object. If this parameter is omitted, a <code>dict</code> object containing all Onion objects managed by OnionsFarmer is returned.</li>
    </ul>
    <p>Onion objects are typically assigned to variables for easy access. OnionsFarmer internally stores every Onion object created, enabling efficient management and retrieval of these instances as needed.</p>
  </div>

  <div id="method-stopOnion">
    <h2>OnionsFarmer.stopOnion() Method</h2>
    <p>The <code>stopOnion()</code> method is designed to halt a specified Onion instance. It serves as a convenient way to terminate Tor processes directly from the OnionsFarmer, complementing the individual stop methods within each Onion object:</p>
    <ul>
        <li><strong>name</strong>: The name of the Onion object to be stopped. When this parameter is provided, OnionsFarmer will attempt to stop the specified Onion instance. If the <code>name</code> parameter is omitted, OnionsFarmer will proceed to stop all Onion instances it manages.</li>
    </ul>
    <p><strong>REMEMBER:</strong> It is crucial to stop all running Onion instances before exiting your script or application. This ensures a proper shutdown of the Tor processes and prevents any potential resource leaks or orphaned processes.</p>
  </div>

  <div id="method-makeOnionsBag">
    <h2>OnionsFarmer.makeOnionsBag() Method</h2>
    <p>The <code>makeOnionsBag()</code> method facilitates the creation of an <code>OnionsBag</code> object, which is a collection containing multiple Onion objects. This method is ideal for quickly generating and managing numerous Tor instances:</p>
    <ul>
        <li><strong>count</strong>: Specifies the number of Onion objects to be created. The default value is 1.</li>
        <li><strong>name</strong>: Optionally provides a base name for the Onion instances. The farmer will append a unique ID to each name, based on the total number of Onions.</li>
        <li><strong>local_sock_port_num_start</strong>: Optionally sets the starting port number. Subsequent Tor SOCKS will be placed on increasing port numbers from this starting point.</li>
        <li><strong>out_proxy_ip</strong>: Optionally specifies an external proxy IP address that can be connected to from another machine. The script will assign the port.</li>
        <li><strong>torrc</strong>: Optionally allows specifying a path to a custom torrc file to be used as a template.</li>
        <li><strong>print_log</strong>: Optionally enables the printing of logs to the console for each Onion object. Be cautious as this can lead to extensive output on the console, especially with many instances!</li>
        <li><strong>http_bridge</strong>: For each Onion, an HTTP Proxy connected to Tor's SOCKS will be created, with the port assigned by the script.</li>
    </ul>
    <p><strong>Remember:</strong> Each created Onion object has its configuration, which you can inspect. This includes SOCKS addresses, HTTP Bridge addresses and ports, among other settings.</p>
  </div>
  <br>
</div>

<div id="onionobj">
  <h2 align="center">Onion Object</h2>
  <div align="center">
    <img src="img/f3.png" alt="Onion Linux">
  </div>
  <div id="onion-object">
      <h2>The Onion Object</h2>
      <p>The <code>Onion</code> object embodies an individual Tor instance within the OnionsFarmer framework. It encapsulates the configuration and management of a Tor process, offering a variety of properties and methods for interaction:</p>
      <h3>Properties</h3>
      <ul>
          <li><strong>Onion.conf</strong>: Returns a dictionary object containing the Onion's configuration, including SOCKS addresses, HTTP Bridge details, etc.</li>
          <li><strong>Onion.isTorConn</strong>: Returns <code>True</code> if the Onion has successfully connected to the Tor network.</li>
          <li><strong>Onion.IP</strong>: Retrieves the IP address of the Exit Node. If the address cannot be obtained, it returns <code>None</code>.</li>
      </ul>
      <h3>Methods</h3>
      <ul>
          <li><strong>Onion.start()</strong>: Initiates the connection to the Tor network. This method begins the Tor process associated with the Onion instance.</li>
          <li><strong>Onion.stop()</strong>: Terminates the Onion's Tor process. <strong>Important:</strong> Always close each Tor connection with this method before ending your program to prevent errors and orphaned processes.</li>
          <li><strong>Onion.sendCMD()</strong>: Sends a command through the Tor Control Socket and returns the response. This method allows for direct interaction with the Tor process.</li>
          <li><strong>Onion.newCircuit()</strong>: Generates a new circuit for the Onion, potentially altering the exit node and IP address.</li>
          <li><strong>Onion.status()</strong>: Displays the current status of the Onion object, which can be "ready to start", "working", or "terminated".</li>
          <li><strong>Onion.infoConf()</strong>: Prints a readable configuration of the Onion object to the screen, detailing its current setup and parameters.</li>
      </ul>
  </div>
</div>

<div id="onionsBag">
  <h2 align="center"> Onions Bag </h2>

  <div>
    <h2>The OnionsBag Object</h2>
    <p>The <code>OnionsBag</code> object, or "Bag of Onions," represents a collection of multiple Tor instances (Onion objects). It allows for efficient and quick management of all contained Onions simultaneously.</p>
    <h3>Properties</h3>
    <ul>
        <li><strong>OnionsBag.len</strong>: Returns the number of Onion objects contained within the bag.</li>
        <li><strong>OnionsBag.isTorConn</strong>: Checks if all Onion objects have successfully established a full connection to the Tor network. Returns <code>False</code> if at least one Onion is not connected, and <code>True</code> if all are connected.</li>
    </ul>
    <h3>Methods</h3>
    <ul>
        <li><strong>OnionsBag.start()</strong>: Initiates the Tor connection process for all Onion objects within the bag.</li>
        <li><strong>OnionsBag.stop()</strong>: Terminates the Tor processes for all Onion objects, effectively stopping all connections.</li>
        <li><strong>OnionsBag.openBag()</strong>: Returns a list object that contains all the Onion objects within the bag.</li>
        <li><strong>OnionsBag.getIP()</strong>: Begins the process of obtaining the Exit Node IP addresses for all contained Onion objects.</li>
        <li><strong>OnionsBag.newCircuit()</strong>: Instructs all Onion objects to start the process of creating a new circuit, potentially changing their exit nodes and IP addresses.</li>
        <li><strong>OnionsBag.__str__()</strong>: Displays a tabular overview of the basic configuration for all Onion objects, including SOCKS addresses, HTTP Bridge statuses, connection statuses, and more. This method provides a quick and readable summary of the entire OnionsBag state.</li>
    </ul>
  </div>
</div>

<div id="examples">
  <h2>Examples</h2>
  <p>Below are examples illustrating how to use the OnionsFarmer utility to manage Tor instances.</p>

  <h3>Basic Usage</h3>
  <p>Here's how to initialize OnionsFarmer, create Onion instances, and manage their Tor connections:</p>

  ```python
  from time import sleep
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
  ```
</div>

<div id="example2">
  <h2>Advanced Example: Managing Multiple Onions</h2>
  <p>This example demonstrates creating, starting, and managing multiple Onion instances simultaneously, including renewing their circuits for new identities:</p>

  ```python
  from time import sleep
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
  ```
</div>

