Bricklink Cart Manager
======================

Python modules for building and optimizing Bricklink Orders

BCM is intended to read in a wanted list, search Bricklink for the related prices, then export and optimized
shopping list in the form of XML "want" lists that can be imported back into Bricklink for easy ordering.

The optimization

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
