# espyonage

Code for a bot to check the website of the Austrian Consulate for open appointments.

This repository contains a script for routinely checking the website of the Los Angeles Austrian Consulate for visa appointments. 
For that consulate, a user must begin by accessing the LA Austrian Consulate [website](https://appointment.bmeia.gv.at/?Office=los-angeles) and navigating to the schedule request page. 
The bot **does not** request an appointment. 

The bot checks the website routinely, but not constantly. 
The default time setting is for checks every 5 minutes, however if the bot finds an appointment the time between checks increases to every 3 hours.
For every check, the bot writes to the log file `appointments.log`.
If desired, the user can pass the bot command line arguments to activate routine status updates on the console or send email notices when it finds an available date.

**Note:** The only external dependency of this package is Selenium, but it must be run with Python 3.6 or greater.
An environment file is provided. Create the environment using 

```
conda env create -f environment.yml
```

and activate using 

```
conda activate espyonage
```


## Usage

The bot can be activated by running the `consulates.py` script.

```
python consulates.py
```

Two options are available on the command line.
The `-v` (or `--verbose`) option will activate routine printouts to the console with status updates.
The `-n` (or `--notify`) option will prompt the user for a GMail username and password enabling SMTP email notifications.

To enable both notifications and status updates, run the script with

```
python consulates.py -v -n
```

Quit the program at any point with the standard command to kill a process, `^C`. 

## User-defined parameters

Some command line arguments must be specified before executing the script.
Listed at the top of the file, the `target` and `latest_date` variables must be set manually.

* `target`: a list of email addresses for notifiaction recipients
* `latest_date`: the latest date that an appointment can be scheduled (the script will notify you if it finds a date available before this)
