% Interaction Techniques and Technologies
  Assignment 7: Sensors, PyQtGraph
% Summer Semester 2021
% **Submission due: Wednesday, 16. June 2021, 23:55**

**Hand in in groups of max. two.**

Your task is to get comfortable with Sensors and PyQtGraph

7.1: A short introduction to Digital Signal Processing
======================================================

Skim the chapters of [*The Scientist and Engineer's Guide to Digital Signal Processing*](http://www.dspguide.com/) so that you have a good overview of the topics covered by this guide.

Concisely answer the following questions:

* What is the defining property of Gaussian noise?
* What does a low-pass filter do in general?
* Is a *moving average* filter a low-pass or a high-pass filter? Why?

Points
------------

* **2** Good answer to first question 
* **2** Good answer to second question 
* **2** Good answer to third question 


7.2: A Sensor Game
====================

Write a small Python application `dippid_game.py` that takes the port of a DIPPID device as its only parameter.
This application should implement a fun game that involves your device:

* The application should `import DIPPID` (do not modify `DIPPID.py` itself).
* On launch, print instructions for the game to `stdout` or show them in a Qt window.
* Automatically connect to the DIPPID device with the given Port.
* Utilize at least two input modality of the DIPPID device
* If you want, you may also implement a graphical user interface for the game - but you can also just use the DIPPID device without any display.

If you are looking for inspiration on game concepts, check out e.g., [Bop It](https://en.wikipedia.org/wiki/Bop_It) or [ball-in-a-maze puzzles](https://en.wikipedia.org/wiki/Labyrinth_(marble_game)).


Hand in the following file:

**dippid_game.py**: a Python script that implements your game

(Please also hand in the `DIPPID.py` version you are using)

Points
------------

* **1** The python script has been submitted, is not empty, and does not print out error messages.
* **1** The script is well-structured and follows the Python style guide (PEP 8) and contains comments in regard of workload distribution.
* **2** The game is fun to play (at least a little bit)
* **1** The game utilizes at least two input modalities of the DIPPID device


7.3: A custom PyQtGraph flowchart using the SensorNode
========================================================

Read the source code for `DIPPID-pyqtnode.py` (from the [*DIPPID.py* GitHub repository](https://github.com/PDA-UR/DIPPID-py)) and the [PyQtGraph documentation](http://pyqtgraph.org/documentation/).
Install the PyQtGraph Debian package (e.g. `sudo apt install python3-pyqtgraph`
Write a small Python application `analyze.py` that takes the Port of a DIPPID device as its only parameter.
This application should generate a PyQtGraph flowchart with the following elements:

* a DIPPIDNode.
* a *BufferNode* (see `DIPPID-pyqtnode.py`) for each of the accelerometer channels,
* three `PlotWidget`s that plot the accelerometer data for each channel and another `PlotWidget` that displays the output of the `NormalVectorNode` (see below)
* a *NormalVectorNode* (to be implemented by you) that calculates the rotation around one axis from the accelerometer values of the other two axes and outputs a vector (i.e., two 2D points) that can be plotted by a `PlotWidget` to indicate the rotation (see video in GRIPS) - this node should accept accelerometer values on its two input terminals and provide a list/tuple of two tuples, such as ((0, 0),(1.0,1.0)) on its output terminal.
* a *LogNode* that reads values (e.g., accelerometer data) from its input terminal and writes them to `stdout`.

Your application should import `DIPPID-pyqtnode.py` and use the two nodes defined there.

Hand in the following file:

**analyze.py**: a Python script that implements this flowchart.

Points
------------

* **1** The python script has been submitted, is not empty, does not print out error messages and follows follows the Python style guide (PEP 8).
* **2** The script correctly implements and displays a flowchart.
* **2** The script correctly reads accelerometer data from the DIPPID device and plots it.
* **3** The script contains a working *NormalVectorNode* as described above.
* **1** The script contains a working *LogNode* as described above.


Submission 
=========================================
Submit via GRIPS until the deadline

All files should use UTF-8 encoding and Unix line breaks.
Python files should use spaces instead of tabs.
If you need to submit further supporting files, please add a comment describing their use.

                                                               Have Fun!
