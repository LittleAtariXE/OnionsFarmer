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
    <a href="#req">Requirements</a> &nbsp;|&nbsp;
    <a href="#Whatis">Install</a>  &nbsp;|&nbsp;
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

