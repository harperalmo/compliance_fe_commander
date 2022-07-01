commander

Language: Python 3.7 with PyQt5 for GUI

PROJECT DESCRIPTION:
This is the main controller gui from which a user of this system controls
operations to measure and save scripts to test the compliance of a guitar
top. These measurements are taken according to David Hurd's Left Brain
Lutherie book.

The front end will contain a command creator and sender, a scripting
service to store commands so they can be rerun, and a graphing module
that displays the isobar graph of the compliance values that are collected.

HARDWARE TARGET:
The front end runs mostly on a Raspberry Pi. It communicates with an esp32
called the marshaller via serial TX/RX wires. The marshaller's job is to
manage commands it sends to the backend axis contollers (also esp32 uprocs)
and get their responses sent off to the appropriate front end message
handler. The marshaller/back end axis controllers use esp-now radio
messaging. 

