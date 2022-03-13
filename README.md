# cube-timer
Open source cube solve timing hardware and software.

Directories:
arduino:
Sketch intended to run on an Uno board or the older 2009.   Minor changes would work on other boards, like the card select pin for the SD card.

case:
Freecad designs for a basic case and lid.

desktop:
Python GUI app for configuring and controlling the timer.

docs:
Original plan and some current parts costs examples

pcd:
Work in progress PCB layouts.

SD Card Note:
In order for the SD card to be considered valid, it must have a fiel on it containing the configuration you want to run with, this a a CSV file named CONF.TXT with the content Inspection Limit, First Alert, and Second Alert (15,8,12).  For events with no inspection time use 0,0,0.