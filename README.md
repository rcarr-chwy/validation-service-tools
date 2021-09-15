# HMS Validation Service Tools (unofficial)
Scripts used to interact with MedPro.  

** A collection of scripts that have been created while working with MedPro and their
data. 

## Summary
**Note:** The best way to run these is inside a Docker container since it keeps your machine relatively clean.  Of course, docker and docker-compose should already be installed.

## Quickstart
If you just want to start the service with minimal fuss, do the following:
- copy file file **umber.env.sample** to **umber.env**
- edit **umber.env** : MEDPRO_API_CLIENT_ID, MEDPRO_API_CLIENT_SECRET
- Start the service with `docker-compose up -d`

Once the service is up and running, connect to the container using:
`connect.sh`

## Scripts

- **universe_check.py** See if a vet is in our universe
` python universe_check.py -i <medpro id>`
