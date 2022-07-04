# Project Title: Scripts I made to Support with C1 Capstone

## Motivation: I wrote these scripts to support m team to determine whether the weather has an impact on MTA Transit Timeliness. 

timetableScraper.py - Scrapes the MTA schedules from https://new.mta.info/schedules and downloads the selected PDF schedules to the current working directory.


mtaTimeTableCleaner.py - Takes the PDFs downloade from timetableScraper.py and scrapes the tables from the pdf files. It then removes erroneous data from the tables (whether the trains are local trains, express, or have stars) and calculates the projected amount of time each trip takes. It takes all of those values, and dumps them into a CSV file for easy viewing that has the train name, the train departure time, the arrival time at the last station, and the amount of time the trip took in total.
