#!/usr/bin/env python
# coding=utf-8

from xbee import DigiMesh
from random import randint
from textwrap import wrap
from umsgpack import packb, unpackb
import serial
import time
import json

# Configuration
XBEE_PORT   	= "/dev/ttyUSB0"
XBEE_BAUD   	= 115200
XBEE_MESH_ID	= "1234"	# Xbee DigiMesh Network ID (0x0000 - 0xFFFF)
XBEE_MESH_CH	= "0C"		# Xbee DigiMesh Channel ## (0x0C - 0x17)
XBEE_MESH_DL	= "0xFFFF"	# Default destination
XBEE_MESH_DESC	= "\x00\x00\x00\x00\x00\x00\xFF\xFF"	# Escaped Destination

ser_xbee = serial.Serial(XBEE_PORT, XBEE_BAUD, timeout=1)
xbee = DigiMesh(ser_xbee)

# main
def main():
	# Switch to API Mode
	print ">> Configuring Xbee"
	time.sleep(1)
	ser_xbee.write("+++")				# enter command mode
	time.sleep(1)
	if (ser_xbee.read(3) == "OK\r"):
		print "AT  \tOK"
		ser_xbee.write("ATAP 1\r")					# switch to API mode
		print "ATAP\t%s" %ser_xbee.read(3)			# wait for reply
		ser_xbee.write("ATID %s\r" %XBEE_MESH_ID)	# mesh id
		print "ATID\t%s" %ser_xbee.read(3)			# wait for reply
		ser_xbee.write("ATCH %s\r" %XBEE_MESH_CH)	# mesh ch
		print "ATCH\t%s" %ser_xbee.read(3)			# wait for reply
		ser_xbee.write("ATWR\r")					# apply settings
		print "ATWR\t%s" %ser_xbee.read(3)			# wait for reply
		ser_xbee.write("ATAG %s\r" %XBEE_MESH_DL)	# apply settings
		print "ATAG\t%s" %ser_xbee.read(3)			# wait for reply
		ser_xbee.write("ATCN\r")					# exit command mode	
	else:
		print "AT  \tFAIL"

	# Configure Xbee
	#xbee.at(command="CE", parameter="0")			# router mode
	#xbee.at(command="ID", parameter=XBEE_MESH_ID)	# mesh id 
	#xbee.at(command="CH", parameter=XBEE_MESH_CH)	# mesh channel
	#xbee.at(command="WR")							# apply
	#xbee.at(command="AG", parameter=XBEE_MESH_DL)	# broadcast as master

	# Receive packets
	frames = {}							# buffer for storing unprocessed frames
	packet = ""							# buffer for placing string after processing
	packets = []						# all packets received
	while True:
		frame = xbee.wait_read_frame()		# wait for frames
		print frame["source_addr"]
		frame = unpackb(frame["data"])		# decode json
		pid   = frame["id"]					# get id
		pnum  = frame["pn"]					# get packet number
		pdata = frame["dt"]					# get data

		if not pid in frames:				# if new packet stream
			frames[pid] = {}				# initialize slot
		frames[pid][pnum] = pdata			# store data from frame
		#print frame

		if 0 in frames[pid]:				# if we already have the header
			if frames[pid][0] == len(frames[pid]):	# and we have all the frames
				for i in range(1, frames[pid][0]):	# join data from frames
					packet += frames[pid][i]
				frames[pid] = {}
				packet = unpackb(packet)
				timestamp = time.strftime("%H:%M:%S", time.localtime())
				print "Got packet from: %s at %s" %(packet["ant_mac"], timestamp)
				packets += (timestamp, packet)
				packet = ""
		

if __name__ == "__main__":
	main()
