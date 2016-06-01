# RustHP
Python &amp; NodeJS implementation of a raid HP viewer for Rust

Uses per-second screengrabs via pyscreenshot which are processed using OpenCV to determine health, thirst, hunger and weapons on action bar in Rust. These values are sent to a node.js server which relays the information to a web client.

## Installation

To run the Python script the following libraries are required:

* numpy
* cv2
* pyscreenshot
* socketIO_client

These can all be downloaded via pip with the exception of OpenCV (cv2) which can be installed from binaries found on their website.

After installing these libraries, install node.js and navigate to the server folder and run 'npm install' to download the node modules required to run the server. 

The client is configured by default to connect to localhost (connecting to remote servers is untested if you're reading this, but should work). To alter this, edit the 'host' field in the main clause of main.py.
