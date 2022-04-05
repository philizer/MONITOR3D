# MONITOR3D
A simple interface to monitor and control your 3D printer

The software aims to monitor and control a printer remotely with a light, simple debugging and user-friendly interface. It is easy to understand, modify and improve with new functions.

For now, the software only works on Linux-based systems. Windows and Raspberry pi OS versions are coming.
(Also, this software is optimized for PRUSA printers. Depending on your printer, a few modifications to the serial_comm.py file might be needed for the temperature display. See the **Modify** section)

## Quickstart
1) Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) according to the documentation (if not already installed).
2) Clone the Git repository.
3) Go to the "MONITOR3D" file in a terminal window.
4) Run the ```docker-compose up ``` command.
5) Plug the 3D printer into a USB port.
6) Open the "index.html" file in a web browser. Let's fix the "Page not found" error.
7) In your browser, open a window and go to http://localhost:3000 (Grafana interface).
8) Login with the ID and PASSWORD defined in the docker-compose.yml file if needed (id: admin, password: password).
9) Import a data source: Configuration > Data sources > InfluxDB.
  Fill in these fields:
- Query language: InfluxQL
- URL: http://influxdb:8086
- Access: Server
- Database: db
- User: admin
- Password: password
- Click Save and test
10) Create a new dashboard: Create > Dashboard > Add a new panel > select InfluxDB data source > New query: SELECT * FROM data
11) The temperature of your printer should log on the graph.
12) Name the panel if you want, set the time range to "Last 5 min", apply and save changes.
13) Click on the name of the panel > Share > Embed > uncheck the "Current time range" and copy the link.
14) Open the index.html file in a code editor and replace the <iframe> HTML tag with the copied one. Adjust the height to 500  and save the file.
15) Refresh the dashboard. You should now see the temperature graph.
16) When you are done using MONITOR3D, stop the containers (Ctrl + C) from the terminal and run a ``` docker-compose down ``` command to make sure containers stop running on your machine.
 
### Commands
Run any command you like from the drop-down list.

### Print a model
Slice a .stl model with your favorite slicer and upload the .gcode file on the dashboard. Send it.
You should now see the commands sent to the printer in the terminal opened (step 3). After heating and calibration, the print will start.
Click on the related buttons to monitor the advancement and axis position (refreshed every 10 seconds).


## Modify the software to your needs
In the docker-compose.yml file, the "monitor3d" docker image is loaded by default.
Comment the "image" field and uncomment the "build" field to make modifications.
 
### Adapt to your printer if it is not a PRUSA
Go to the serial_comm.py file. Modify the "parseRcvTemp()" and "parseRcvXYZ()" function according to the response of your printer to an "M105" and "M114" Gcode command if needed.  
### Requirements
The software only runs on Linux-based systems for now.
Docker and docker-compose are needed. 
You can find the python libraries in the requirements.txt file.

## Upcoming
The following steps of this project are : more Unit testing, Windows and Raspberry pi OS versions.

## Bugs
The docker-compose might need to be relaunched if the interface is not used for a long time.
The displayed temperature can have a delay.
