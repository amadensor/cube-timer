# cube-timer
Open source cube solve timing hardware and software.

Directories:
arduino:
Sketch intended to run on an Uno board or the older 2009.   Minor changes would work on other boards, like the changing the card select pin for the SD card.

case:
Freecad designs for a basic case and lid.

desktop:
Python GUI app for configuring and controlling the timer.

docs:
Original plan and some current parts costs examples

pcb:
Work in progress PCB layouts.

SD Card Note:
In order for the SD card to be considered valid, it must have a fiel on it containing the configuration you want to run with, this a a CSV file named CONF.TXT with the content Cut Off, Inspection Penalty, Inspection DNF, First Alert, and Second Alert (600,15,17,8,12).  For events with no inspection time use zero for the inspection and alert times, but you can still include a cutoff 600,0,0,0,0.  The SD card should be seen as a backup just in case, writing to the card has been tempermental, affected by power supply voltage as well as static.   When in doubt, format the card.
