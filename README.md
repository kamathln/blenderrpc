# blenderrpc

Installation
------------

* Place this in &lt;BlenderFolder&gt;/&lt;BlenderVersion&gt;/scripts/addons/
* enable this addon in Blender > Main Menu > File > Preferences > Addons


Using
-----

* Once installed, and Blender starts,
* Point your mobiles phone's (recent, html5 compliant) browser to yourpc'sipaddress:9000
* for rotating, press and hold one of the rotation buttons and rotate your phone.  


Warnings
--------

* This set was written for my purposes (playing around) and put on the web in the hopes someone may find it usefull or gets inspired for a solution in real world.
* Different browsers report the angle in different scales. So your mileage may vary. Feel free to "calibrate" your index.html. Also Dear lazy web, feel free to write an initial calibration section to the index.html


Developing:
----------

* There is a websocket listening on port 9001. Currently accepts direct commands that are mentioned in the "commands" array defined in the register funciton of \__init\__.py

* Read the registered functions to know their parameters. 
You *will* need to refresh the page on your browser if you restart blender.
* The code is a pile of hacks and the protocol *will* change if I get more time to work on this. 
* Why Am I struggling so much in \__init\__.py to maintain context? Because inside the server threads, the context is not properly available via bpy.context .  

Happy hacking!
