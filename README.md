Bricklink Cart Manager
======================

Python modules for building and optimizing Bricklink Orders

*Overview*

BCM is intended to read in a wanted list, search Bricklink for the related prices, then export an optimized
shopping list in the form of XML "want" lists that can be imported back into Bricklink for easy ordering.

The optimization problem is a difficult one.  For any wanted list, there are n unique parts (different colors are
 different parts).  For each part, there is a wanted quantity w.

The customer pays shipping on every order (usually around $3).  It can easily take orders from multiple vendors to
complete even small orders of multiple unique parts. The goal of the optimization is to find the combination(s)
of vendors and associated quantities that satisfies the wanted list and minimizes the total cost.


*Usage*

You must have a working Bricklink account in order to login and download the price data. The program will
log in for you.

Running main.py will read in the bcm.ini file.  It should contain the entries below.

````ini
[filenames]
wanted = ../Sampledata/One Element.bsx
prices = ../Sampledata/One Element Prices.xml

[options]
reloadpricesfromweb = False

[bricklink]
username = Geekly
password = **redacted**
````

Create an xml inventory file using Brickstore and change *wanted* to point to it

````python
wantedlistfilename = '../Sampledata/Inventory for 6964-1.bsx
````

run main.py

*Required Modules*

- Numpy
- BeautifulSoup