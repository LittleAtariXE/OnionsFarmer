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
    <a href="#How_works">Methods</a>  &nbsp;|&nbsp;
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
  
</div>


