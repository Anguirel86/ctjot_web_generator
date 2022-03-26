# Installation and Running Instructions
These are the instructions for setting up a test environment for the web generator.

## Getting started
This section details how to download and set up the ctjot web generator. There are two options: running locally or running in Docker.

### Clone the repo
Browse to your working area and:
`git clone https://github.com/Anguirel86/ctjot_web_generator.git `

### Create and set up a virtual environment

 1. `cd ctjot_web_generator`
 2. `virtualenv env`
 3. `source venv/Scripts/activate`
 4. `pip install -r requirements.txt`

**NOTE**: activate script assumes a Windows environment.  It will be venv/bin/activate on Linux.

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

### One-time setup for the web generator database
  In the webapp base directory:
    `python manage.py migrate`

### Using Docker

Docker handles most of the above steps. Assuming Docker already installed, run:
`docker build -t ctjot-web .`

This will create the image. The image includes an included database, but not a ROM. Copy a valid, headerless ROM somewhere; you'll need to mount it into the container.

To run the generator (assuming `ct.sfc` in the directory you're in):
`docker run -p 8000:8000 -v-v $(pwd)/ct.sfc:/usr/src/app/ct.sfc ctjot-web`

The web generator will be available on port 8000 locally.

As mentioned, this uses an included database. This database will go away when the container exits. You may, instead, wish to copy it locally while the above container is running, then reuse it in a later container. To do so, first run:

`docker ps`

You should see an output like:
```
CONTAINER ID   IMAGE       COMMAND                  CREATED              STATUS              PORTS                                       NAMES
cd916bfcfc35   ctjot-web   "python manage.py ru…"   About a minute ago   Up About a minute   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   quirky_taussig
```

You'll need the name of the running container; in the above, it's `quirky_taussig`. Then, run:

`docker cp <that name>:/usr/src/app/db.sqlite3 db.sqlite3` (or, if you prefer, a different name for the second part locally).

After that, you can run using that database with the following:

`docker run -p 8000:8000 -v $(pwd)/db.sqlite3:/usr/src/app/db.sqlite3 -v $(pwd)/db.sqlite3-shm:/usr/src/app/db.sqlite3-shm -v $(pwd)/db.sqlite3-wal:/usr/src/app/db.sqlite3-wal -v $(pwd)/ct.sfc:/usr/src/app/ct.sfc ctjot-web`

(That command assumes that the sqlite database has been set to WAL mode, but should work fine if it hasn't).

To run the docker container in the background, add `-d` to the `docker run` command line. If you do so, you can access the logs which would otherwise be printed to the screen using the `docker logs` command.

## Run the web generator
Source the environment file if not already done:
`source venv/Scripts/activate`

If running and testing locally: 
`python manage.py runserver`
  
If running on a VM or server and testing with a browser from a different address:
`python manage.py runserver 0.0.0.0:8000`
   
Open a web browser and browse to localhost:8000 (or the server's address if running on a VM or server)
