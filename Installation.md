# Installation and Running Instructions

## Getting started
This section details how to download and set up the ctjot web generator.

### Clone the repo
Browse to your working area and:
`git clone https://github.com/Anguirel86/ctjot_web_generator.git `

### Create and set up a virtual environment

 1. `cd ctjot_web_generator`
 2. `virtualenv env`
 3. `source venv/Scripts/activate`
 4. `pip install -r requirements.txt`
**NOTE**: activate script assumes a Windows environment.  It will be venv/bin/activate on Linux.

### One-time setup for the web generator database
  In the webapp base directory:
    `python manage.py migrate`

### Install and prepare the randomizer
Clone the randomizer into the webapp's base directory (currently Pseudoarc's 3.2 beta)
`git clone https://github.com/Pseudoarc/jetsoftime.git`

Copy the following files/folders from jetsoftime/sourcefiles into the webapp's base directory:

 1. names.txt
 2. patch.ips
 3. flux/
 4. patches/
 5. pickles/

Copy a valid, headerless ROM to the base directory and name it ct.sfc

## Run the web generator
Source the environment file is not already done:
`source venv/Scripts/activate`

If running and testing locally: 
`python manage.py runserver`
  
If running on a VM or server and testing with a browser from a different address:
`python manage.py runserver 0.0.0.0:8000`
   
Open a web browser and browse to localhost:8000 (or the server's address if running on a VM or server)