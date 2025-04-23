## wartracker-frontend
Streamlit dashboard for accessing data

The app is available on https://wartracker.streamlit.app/

## Contents
- [Description](#description)
- [Requirements](#requirements)
- [Installation and run](#installation-and-run)
- [Usage](#usage)

## Description
Part of [Wartracker project](https://github.com/users/F1End/projects/1/views/1?pane=info).


This is a Streamlit site that is used to access data processed and saved by upstream processes.
SQLite is used for storage due to compatibility with free streamlit hosting solution.

Currently configured display parse losses sourced from from Oryx's [Ukrainian](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html) and [Russian](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html) losses pages concerning the Russo-Ukrainian war.

Although updates are running on daily bases, **note that data is available only since 1st of April, 2025**.
Be patient, Data will be extended in the future retroactively, but this will be gradual.

Mid-term plans include refactoring the database and adding more query options/help.<br>
Long-term plans include extending coverage to other resources, e.g. pledges and other loss documenting sites.

## Requirements
The script uses python 3.13, but likely will work with most earlier versions after 3.8.

The external library requirements are Streamlit and Pandas.

## Installation and run
1. Git clone repo
2. Install requirements (and create venv if needed)
3. Run via command line: <br>
As this is a Streamlit script, it should be kicked off via the streamlit executable or binary.<br>
This should look something like this, assuming you are using virtual environment:<br>
.\venv\Scripts\Streamlit run main.py (on Windows)<br>
venv/bin/Streamlit run main.py (on Linux)<br>
4. For easy kick-off I also created a file for simplified running, 
that can be kicked off as a regular python script from your system or IDE: st_run_local.py


## Usage

1. Open the [website](https://wartracker.streamlit.app/) or kick off [locally](#Installation and starting script)
2. The default tab is "Predifined Queries". to filter based on listing or switch to "Direct SQL Query"
to run your own queries.
3. You can switch to tab "Direct SQL Query" if you want to run SQL queries written by yourself. 
This gives way more flexibility but requires more technical aptitude.
4. There is further information on "SQL Query Help" and "Technical Details" tabs.
