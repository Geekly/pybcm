
Work on this project took a long hiatus and in the meantime, BL added some great functionality to order filling, including some
optimization of the "cart". There are still some things that can be done to improve it, so this project is pivoting to cover some of those gaps.

1. Help with part substitutions - does BL always choose the cheaper option? Add the ability to also compare alternate colors.
2. Help with vendor ranking - look at prices to determine which vendors are "cheap" and which are "to be avoided"
3. Re-balance orders from a pre-selection of vendors
4. Get a rough price-guide for a given set. If there were helpers for substitutions, even better.
___
Bricklink Cart Manager
======================

Python modules for building and optimizing Bricklink Orders

BCM is intended to read in a wanted list, search Bricklink for the related prices, then export an optimized
shopping list in the form of XML "want" lists that can be imported back into Bricklink for easy ordering.

The optimization problem is a difficult one.  For any wanted list, there are n unique parts (different colors are
 different parts).  For each part, there is a wanted quantity w. The goal of the solution is to minimize the total
 cost of all the orders by finding the optimal order quantities by vendor and part.

The customer pays shipping on every order (usually around $3) and it can easily take orders from multiple vendors to
complete even small orders of multiple unique parts.

*Usage*

You must have a working Bricklink account in order to login and download the price data. The program will
log in for you.

Running main.py will read in the bcm.ini file.  It should contain the entries below.

````ini
[filenames]
wanted = ../Sampledata/One Element.bsx                  # the Brickstore BOM
prices = ../Sampledata/One Element Prices.xml           # file to store the prices in after downloading

[options]
reloadpricesfromweb = False                             # should the prices be re-read from Bricklink?

[bricklink]
username = Geekly
password = **redacted**
````

run main.py

*Required Modules*

- Numpy
- Pandas
- lxml
