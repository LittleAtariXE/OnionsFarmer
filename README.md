<div id="intro" align="center">
  <h1 align="center">Onions Farmer</h1>
  <img src="img/f1.png" alt="OnionFarmer Intro">
  
</div>

<div id="description">
  <h2>OnionsFarmer: The Tor Instance Gardener</h2>
  OnionFarmer is a sophisticated utility designed to cultivate "Onions", metaphorically speaking. Each "Onion" is an independent instance of the Tor network, allowing users to manage multiple Tor processes simultaneously. This Python-based class requires the Tor software to be installed on the system and the user to be added to the Tor group. This setup enables the OnionFarmer to initiate and manage Tor network connections directly.
  <h2>Key Features</h2>
  <ul>
    <li><strong>Create Tor Instances:</strong> The <code>plantOnion</code> method seeds a new Tor instance, functioning as a separate, manageable object.</li>
    <li><strong>Independent Operation:</strong> Each Onion operates independently, offering granular control through built-in methods tailored for interaction and management of the Tor network.</li>
    <li><strong>Graceful Shutdown:</strong> It is highly recommended to invoke the <code>Onion.stop()</code> method before closing your application to ensure a proper shutdown of the Tor process.</li>
    <li><strong>Return Objects:</strong> The <code>plantOnion</code> method returns two pivotal objects - the Onion instance and an external stop event. These objects are essential for direct control and termination of the Tor instance.</li>
    <li><strong>Persistent Configuration:</strong> Upon the initial creation, OnionFarmer generates a directory named "ONIONS" within its folder. This directory houses logs, necessary configuration files, and Tor's "lib" files. Reusing the same Tor instance name enhances startup times, leveraging previously downloaded files for quicker initialization.</li>
    <li><strong>OnionsBag:</strong> Literally a "Bag of Onions". This object stores multiple Onion (Tor instances) objects, allowing for the rapid creation of a specified number of Tor instances and facilitating their bulk management. The OnionsBag simplifies the process of managing multiple Tor connections, providing an efficient way to control and interact with several instances simultaneously.</li>
  </ul>
</div>
