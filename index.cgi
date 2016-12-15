#!/usr/bin/python 

import cgitb; cgitb.enable()
import sys;
import os;
import cgi;
import time, getopt, sys

FONT = "Helvetica"
FONTSIZE = 48

class page:
	global FONT
	global FONTSIZE
	def __init__(self):
		self.font = FONT
		self.buf = "%!\nletter\n"
		self.width = 8.5
		self.height = 11

	def define_inlines(self):
		self.buf += "/inch { 72 mul } def \n"


	# all units are in inches except for linewidth, which is in 1/72s of an inch
	def define_params(self, cardwidth, cardheight, margin, linewidth, radius, nrows=3, ncols=3):
		self.left = (self.width - ncols*cardwidth - (ncols-1)*margin)/2
		self.bottom = (self.height - nrows*cardheight - (nrows-1)*margin)/2
		self.rows = nrows
		self.cols = ncols
		self.cardwidth = cardwidth
		self.cardheight = cardheight
		self.margin = margin
		self.linewidth = linewidth
		self.radius = radius
	
	def setup_font(self, font, fontheight):
		self.buf += "/" + font + " findfont "
		self.buf += str(fontheight) + " scalefont "
		self.buf += "setfont\n"
		self.fontheight = fontheight
		


	# Making the rounded rectangle
	# 1) draw a line from x1, y1 to x2, y2-r
	# 2) draw a circular arc of radius r from x2, y2-r to x2+r, y2
	# 3) where x1=x2 and y2=y3

	def line(self, x1, y1, x2, y2):
		self.buf += "newpath %g %g moveto %g %g lineto stroke\n" % (x1, y1, x2, y2)

	def setlinewidth(self, w):
		self.buf += "%g setlinewidth\n" % w

	def arcto(self, x1, y1, x2, y2, x3, y3, r):
		self.buf += "newpath %g inch %g inch moveto \n" % (x1, y1)
		self.buf += "%g inch %g inch %g inch %g inch %g inch arcto stroke \n" % (x2, y2, x3, y3, r)
		self.buf += "4 {pop} repeat "

	# Remember, PostScript uses lower-left origin
	def rounded_rectangle(self, x, y, w, h, r):
		self.arcto(x, y+r, x, y+h, x+w, y+h, r)
		self.arcto(x+r, y+h, x+w, y+h, x+w, y, r)
		self.arcto(x+w, y+h-r, x+w, y, x, y, r)
		self.arcto(x+w-r, y, x, y, x, y+h, r)

	# show text centered at cx, cy, using default fontsize
	def showcenteredtext(self, text, cx, cy):
		# self.buf += "(Text center: " + str(cx) + ", " + str(cy) + ")"
		self.buf += str(cx) + " inch (" + text + ") stringwidth pop 2 div sub \n" # x-left
		self.buf += str(cy) + " inch " + str(self.fontheight * .35) + " sub moveto\n"
		self.buf += "(" + text + ") show\n"
	
	def showpage(self):
		self.buf += '\nshowpage\n\n'

	def pstack_checkpoint(self, n):
		self.buf += "(checkpoint " + str(n) + ") pstack pop\n"

	def test_grid(self, factor):
		# cardwidth, cardheight, margin, linewidth, radius, nrows=3, ncols=3
		self.setup_font(self.font, FONTSIZE)
		self.define_params(2.5, 3.3, 0, 3, .2)  
		self.define_inlines()
		for half in ['expr', 'soln']:
			self.setlinewidth(self.linewidth)
			for i in range(0, self.rows):
				for j in range(0, self.cols):
					left = self.left + j*self.cardwidth + (j-1)*self.margin
					bottom = self.bottom + i*self.cardheight + (i-1)*self.margin
					self.rounded_rectangle(left, bottom, 
																 self.cardwidth, self.cardheight, self.radius)
				#	self.rounded_rectangle(self.left   + j*self.cardwidth  + (j-1)*self.margin,
				#												 self.bottom + i*self.cardheight + (i-1)*self.margin,
				#												 self.cardwidth, self.cardheight, self.radius)
					self.showcenteredtext(cards[factor][half][i*self.cols + j],
																left + self.cardwidth/2, bottom + self.cardheight/2)
			self.showpage()
		return self.buf

# end of page class



# Create card content
def make_problems(operand, operator, n):
	ret = []
	for i in range(1, n+1):
		ret.append( str(i) + ' ' + operator + ' ' + str(operand)) 
	return ret

def make_products(factor, n):
	ret = []
	for i in range(1, n+1):
		ret.append(str(i*factor))
	return ret

# bad coding p
number_names = { 'twos' : 2, 'threes' : 3, 'fours': 4, 'fives': 5, 'sixes' : 6, 'sevens' : 7, 'eights' : 8, 'nines' : 9 }
cards = {}
for key in number_names:
	cards[key] = {}
	cards[key]['expr'] = make_problems(number_names[key], 'x', 9)
	cards[key]['soln'] = make_products(number_names[key], 9)


cgiform = """
<html>
<head>
<link rel="stylesheet" type="text/css" href="http://www.threerightangles.com/css/green-blue.css">
<title>Multiplication Memory Deck Generator | threerightangles.com</title>
<style>
	select, input, option {
		color: black;
		margin: 3px 10px;
	}
</style>
</head>
<body onkeydown="toggle(event)">
<div id="title">
Multiplication Memory Deck Generator
</div>
<h2 style="margin: 5px 10px 0px; padding: 5px 10px 0px">Rules</h2>
<p style="margin: 10px 20px">
<ol style="margin: 0px 5px">
<li>This game is based on the game Memory.</li>
<li>On your turn, begin by flipping over a card</li>
<li>Announce what the matching card should be.</li>
<li>Before the game starts, decide as a group whether to let someone try again if they make the wrong guess, or if they lose their turn.</li>
<li>Flip over a second card.</li>
<li>If you make a match, keep the pair and get another turn</li>
</ol>
<div id="content">
<form action="index.cgi" method=post>
<input type=hidden name="post" value="value">
<input type=hidden size=20 length=20 name="font" value="Helvetica">
<table style="border: 0">
<tr><td>
Set</td><td> <select name="multiples">
	<option value="twos">multiples of 2</option>
	<option value="threes">multiples of 3</option>
	<option value="fours">multiples of 4</option>
	<option value="fives">multiples of 5</option>
	<option value="sixes">multiples of 6</option>
	<option value="sevens">multiples of 7</option>
	<option value="eights">multiples of 8</option>
	<option value="nines">multiples of 9</option>
</select></td>
</tr>
<tr>
<td></td><td>
<input type=submit value="download cards!"></td>
</table>
</form>
</div>
<hr>
<p style="margin: 5px 20px">Card design by Eric Welch</p>
<hr>
<p style="margin: 5px 20px"><a style="color: lightblue" href="http://threerightangles.com">[Home]</a></p>
<script>
	function toggle(event) {
		if(event.keycode == 65) {
			var switch = document.getElementById("secret")
			switch.value = "billy"
		}
	}
</script>
</body>
"""

##########################
#   Put it all together  #
##########################
def render_form():
	print "Content-type: text/html"
	print
	print cgiform



def make_ps(font, multiples):
	paper = page()
	paper.font = font
	paper_ps = paper.test_grid(multiples)
	return paper_ps

def make_pdf(font, multiples):
	import os
	import tempfile
	ps_file  = tempfile.NamedTemporaryFile("w+")
	pdf_file = tempfile.NamedTemporaryFile("w+")
	debugname = 'temp.ps'
	ps_debug = open(debugname, 'w')
	ps_file.write(make_ps(font, multiples))
	ps_debug.write(make_ps(font, multiples))
	ps_debug.close()
	ps_file.seek(0)
	cmd = "ps2pdf " + ps_file.name + " " + pdf_file.name
	os.system(cmd)
	pdf_file.seek(0)
	return pdf_file.read()

def print_source(filename):
	sys.exit(0)
	print "Content-type: text/text\r\n\r\n"
	for line in open(filename, "r"):
		sys.stdout.write(line)



def handle_cgi():
	import tempfile
	form = cgi.FieldStorage()

	if form.has_key("source"):
		print_source(form.getfirst("source"))
		sys.exit(0)

	if form.has_key("post"):
		pdf = make_pdf(form.getfirst("font", "Helvetica"), form.getfirst("multiples", "twos"))
		print "Content-Type: application/pdf"
		print
		print pdf
	
	render_form()


########
# MAIN #
########
if __name__ == "__main__":
	if(os.getenv("REQUEST_METHOD") != None):
		handle_cgi()
		sys.exit(0)

