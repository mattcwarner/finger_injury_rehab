# YOUR PROJECT TITLE
#### Video Demo:  https://youtu.be/wWO20AGduLs
#### Description:
#### Intended use:
This program is supposed to act as a guide through the journey of an annular pulley injury in a finger. Diagnosis and treatment should be undertaken by a suitable medical professional, especially in the case of severe injury. The program will want to know all about your injury including when it happened and the severity. From this information and based on clinical estimates, it will be able to give you a very rough estimation of the timeframes for recovery. The next stage is recording a baseline from the other hand and then moving on to slow progressive overload of your injured digit (when you are in the appropriate recovery phase). The rehabilitation is currently split into stages, single finger open and single finger at 90 degress of flexion at the DIP joint, 4 finger half crimp and full crimp hangs, though you are suggested to tailor your stages to your specific injury.
#### Reccomended way to load your fingers:
The reccomended method of loading is using small incremental weights, hung from a sling, then attached directly to your finger or onto a 20-15mm crimp block, the exercise will then involve picking the weight off the floor and holding it for the specified amount. Getting a set of weights for this might be too much to ask, in the past I have done it with variously filled old milk bottles, which works but is nowhere near as convenient as weights. Another option is to do hangs from a hangboard with weight taken off with pulleys or simply standing on a scale and pulling until you get the desired resistance, this is a bit harder to get right although will be more fun than deadlifting more than your body weight on a crimp.
#### Choice of project:
The project was of specific interest to me as I ruptured a pulley just as I was looking for inspiration for a project. I considered making a web app version but had other ideas for projects to learn those skills so I thought I would experiment with a desktop app, hence the use of tkinter.
#### Design choices:
The app originally began as a command line program that worked well and output a graph after each workout. The use of tkinter made the code a lot more detailed and I had to abstract a lot of things, creating separate python files for various types of objects that I created to simplify the process. 
#### Testing:
The main part of the app that requires testing is the initial inputting of a users injury data, the tests can be run using pytest from the app_package folder and tests various ways in which the diagnosis process could be derailed.
#### Package structure:
The package is structured for conversion to a single file exectable program that users can use without getting involved with the command line. To use the unbundled code, run app/app.py from the app_package directory.
#### A note on the information provided in the app:
The information included in recovery_schedule.py is an approximation of guidance and loading protocols gleaned from my limited reading and own experimentation in the area and is no substitute for professional opinions, in fact this information is separated into a separate file on the basis that it would make it easier for someone with a clue to make corrections and input decent advice on the matter.
