# Running Locally Without Docker
These are the instructions for setting up the web generator locally.
The web generator will be run using the built-in Django test server and sqlite database.  By default,
this server will only be accessible on localhost.

Running with Docker and the deploy.sh script is the preferred method.  These instructions will 
allow for setting up a local test environment in environments without Docker.

## Clone the repo
Browse to your working area and:
`git clone https://github.com/Anguirel86/ctjot_web_generator.git`

The Jets Of Time randomizer is included in this repo as a submodule.  It will need to be initialized.
If running with the deploy.sh script then this will be handled automatically.  If not, then run:
 1. `git submodule init`
 2. `git submodule update`

## Copy a vanilla ROM
 1. Copy an unheadered Chrono Trigger ROM to the repo base directory and name it ct.sfc

## Set up a Python virtual environment

 1. Create a virtual environment named venv:
    1. `python3 -m venv venv`
 2. Enter the virtual environment:
    1. `source venv/bin/activate` (Linux)
    2. `source venv/Scripts/activate` (Windows)
 3. Install dependencies:
    1. `pip install -r requirements.txt`

## Run the server

 1. Set a SECRET_KEY.  Either:
    1. Set the SECRET_KEY environment variable, or
    2. Modify the SECRET_KEY line in the ctjot/settings.py file
 2. Set the app to DEBUG mode.  Either:
    1. Set the DEBUG environment variable to '1' or
    2. Modify the DEBUG line in the ctjot/settings.py file
    3. This will allow the test server to see static files and allow tracebacks on errors
 3. Copy or link the following files into the web app's base directory:
    1. jetsoftime/sourcefiles/names.txt
    2. jetsoftime/sourcefiles/patch.ips
    3. jetsoftime/sourcefiles/flux/
    4. jetsoftime/sourcefiles/patches/
    5. jetsoftime/sourcefiles/pickles/
 4. Enter the virtual environment (if not already done):
    1. `source venv/bin/activate` (Linux)
    2. `source venv/Scripts/activate` (Windows)
 5. Apply database migrations:
    1. `python manage.py migrate`
 6. Run the test server:
    2. `python manage.py runserver`
    
