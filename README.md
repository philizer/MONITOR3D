# MONITOR3D
A simple interface to monitor and control your 3D printer

The software aims to monitor and control a printer remotely with a light, simple debugging, and user-friendly interface. 
For now, the software only works on Linux-based systems. Windows and Raspberry pi OS versions are comming.
(Also, this software is optimized for PRUSA printers. A few modifications to the serial_comm.py file might be needed depending on your printer, for the temperature display.)

## Quickstart
1) Install Docker and docker-compose according to the documentation (if not already installed).
2) Clone the Git repository.
3) Go to the "MONITOR3D" file in a terminal window.
4) Run the ```console docker-compose up ``` command.
5) Plug the 3D printer to a USB port.
6) Open the "index.html" file in a web browser. Let's fix the "Page not found error".
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
10) Create a bew dashboard: Create > Dashboard > Add a new panel > New query: SELECT * FROM data
11) The temperature of your printer should log on the graph.
12) Name the panel if you want, set the time range to "Last 5 min", apply and save changes.
13) Click on the name of the panel > Share > Embed > uncheck the "Current time range" and copy the link.
14) Open the index.html file in a code editor and replace the <iframe> html tag with the copied one.Save the file.
15) Refresh the dashboard. You should now see the temperature graph.
 
### Commands
Run any command you like from the drop-down list.

### Print a model
Slice a .stl model with your favourite slicer and uplad the .gcode file on the dashboard. Send it.
You should now see in the terminal opended (step 3) the command sent to the printer. After heating and calibration, the print will start.

 
## Adapt to your printer if it is not a PRUSA

```console
$ 

```

### Requirements

## Upcomming
Next steps of this project are: Unit testing, Windows and Raspberry pi OS versions.

## Bugs
