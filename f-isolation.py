#!/usr/bin/python
#coding: utf-8

# F-Isolation v0.1 - F**k isolated enviroments

# Because we hate that kind of pentests where you start at an isolated citrix where our
# clipboard is useless, we do not have internet access inside the machine and we can not
# map a local resource to upload our tools.

# OCR + Keyboard emulation FTW!


import argparse
import pyautogui
import pytesseract
import time
import sys
import os.path
import base64

from PIL import Image
from tqdm import tqdm


def banner():
	print '''
 ██████╗    ██╗███████╗ ██████╗ ██╗      █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
██╔════╝    ██║██╔════╝██╔═══██╗██║     ██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
█████╗█████╗██║███████╗██║   ██║██║     ███████║   ██║   ██║██║   ██║██╔██╗ ██║
██╔══╝╚════╝██║╚════██║██║   ██║██║     ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
██║         ██║███████║╚██████╔╝███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
╚═╝         ╚═╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

   by X-C3LL & SoA
'''

startpoint = "[HERE-STARTS]"
stoppoint = "[HERE-STOPS]"

# Convert image object to string and return the text
def imageToString(image):
	text = pytesseract.image_to_string(image)
	return text

# Take a screenshot of notepad
def takeScreenshot(y,sizex,sizey):
	im = pyautogui.screenshot(region=(0,y,sizex,sizey))
	return im

# Extract the text
def extractInfo(text):
	return text[text.index(startpoint) + len(startpoint):text.index(stoppoint)]

def exfiltrate():
	print "[+] Starting the transfer!"
	finalText = ""
	while 1:
		currentText = imageToString(takeScreenshot(args.axisy, args.sizex,args.sizey))
		try:
			currentText.index(stoppoint)
			finalText = finalText + currentText
			break
		except:
			finalText = finalText + currentText
			pyautogui.press('pagedown')
	print "[+] Transfer finished!"
	return extractInfo(''.join(finalText.split("\n")))

#Read file in binary mode
def read_file_b(input_f):
	if os.path.isfile(input_f):
		try:
			with open(input_f, 'rb') as f:
				data = f.read()
		except:
			print "[!] Error. File could not be opened in 'rb' mode!"
	else:
		print "[!] Input file does not exist!"
		exit(-1)
	print "[+] Read the file!"
	return data

#Emulate keyboard
def keyboard_action(data, interval):
	if '\n' in data: #in case multiline data to help visualize progress
		data = data.split('\n')
		for line in tqdm(data):
			pyautogui.typewrite(line, interval=interval)
			pyautogui.press('return') #enter
	else:
		pyautogui.typewrite(data, interval=interval)
	print "[+] Finished writing with keyboard!"

#save output to file
def dump_info(output_f, data):
	if not os.path.isfile(output_f):
		try:
			with open(output_f, 'wb') as outfile:
				outfile.writelines(data)
				print "[+] Information saved to "+ str(output_f) +"!"
		except:
			print "[!] Error. Could not write to output file!"
			exit(-1)
	else:
		print "[!] File already exists!"
		exit(-1)

#timeout before keyboard emulation
def time_out_k(time_out):
	for i in reversed(xrange(1,time_out+1)): 
		sys.stdout.write("[+] Sleeping for "+str(i)+'s...\r')
		sys.stdout.flush()
		time.sleep(1)
	print ""

#b64 encode data
def tranform_to_b64(data):
	return base64.b64encode(data)

# Parameters for "exfiltration"
parser = argparse.ArgumentParser()
parser.add_argument("--exfiltrate", dest="ofile", help="File where to save extracted data")
parser.add_argument("--axisy", dest="axisy", help="Screenshot starting point")
parser.add_argument("--sizey", dest="sizey", help="Size of screenshot (Y Axis)")
parser.add_argument("--sizex", dest="sizex", help="Size of screenshot (X Axis)")

#Parameters for "infiltration"
parser.add_argument('-k', "--keyboard",  action="store_true", default=False, help="Use keyboard (if not present, saves to file)")
parser.add_argument("-i", "--input", help="Input file to transfer")
parser.add_argument("-t", "--timeout", type=int, default=5,
					help="Timeout before writing with keyboard (default 5s)")
parser.add_argument("-int", "--interval", type=float, default=0.0,
					help="Interval between keypresses (default pyautogui 0.0s)")
parser.add_argument('-b64', "--base64",  action="store_true", default=False, help="Encode payload as base64 (default False)")
parser.add_argument("-o", "--output", help="Output file (debug)")

args = parser.parse_args()


# Main
banner()

if args.ofile: #exfiltration
	if args.axisy and args.sizey and args.sizex:
		print "==========\n Exfiltration mode\n==========\n"
		time_out_k(args.timeout)	
		data = exfiltrate()
		dump_info(args.ofile, data)

elif args.input: #infiltration
	print "==========\n Infiltration mode\n==========\n"
	data = read_file_b(args.input)
	if args.base64:
		data = tranform_to_b64(data)
	if args.keyboard:
		time_out_k(args.timeout)
		keyboard_action(data, args.interval)
	if args.output:
		dump_info(args.output, data)
	
else:
	print "[!] Wrong operation mode :("
