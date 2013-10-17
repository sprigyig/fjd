import gtk
import cairo

bg = (1,1,1)
fg = (0,0,0)

styles = [ (bg, fg), (fg, bg)]

class MyW(gtk.DrawingArea):
	__gsignals__ = { "expose-event":"override"}

	def __init__(self, csrc):
		self.csrc = csrc
		gtk.DrawingArea.__init__(self)

	def do_expose_event(self, event):
		width, height = self.window.get_size()
		cw,ch,cs = 8,12,11
		cr = self.window.cairo_create()
		cr.set_source_rgb(*bg)
		cr.rectangle(0,0,width,height)
		cr.fill()

		cr.set_source_rgb(*fg)
		cr.select_font_face("Courier")
		cr.set_font_size(cs)

		for row in range(height//ch)[::-1]:
			for col in range(width//cw):
				x = cw*col
				y = ch * (row +1)
				cr.set_source_rgb(*styles[self.csrc.style(row,col)][0])
				cr.rectangle(x,y-ch+3,cw,ch)
				cr.fill()
				cr.set_source_rgb(*styles[self.csrc.style(row,col)][1])
				cr.move_to(x, y)
				cr.show_text(self.csrc.content(row,col))


class ThrowawayDocument:
	def __init__(self):
		self.lines = [""]
		self.cursor = (0,0)

	def add(self, chr):
		row = self.cursor[0]
		col = self.cursor[1]
		if chr == '\n':
			cur, nl = self.lines[row][:col],self.lines[row][col:]
			self.lines = self.lines[:row]+[cur, nl]+self.lines[row+1:]
			self.cursor = (row+1, 0)
		else:
			self.lines[row] = self.lines[row][:col] + str(chr) + self.lines[row][col:]
			self.cursor = (row, col+1)

		print self.cursor
			

	def content(self, row, col):
		if row < len(self.lines):
			r = self.lines[row]
			if col < len(r):
				return r[col]
		return ' '

	def style(self, row, col):
		return 1 if row==self.cursor[0] and col==self.cursor[1] else 0

	def special(self, keycode):
		row, col = self.cursor[0], self.cursor[1]
		if keycode == gtk.keysyms.BackSpace:
			if col > 0:
				self.lines[row] = self.lines[row][:col-1]+self.lines[row][col:]
				self.cursor = (row, col-1)
			elif row > 0:
				print "cursor", self.cursor
				print "lines", self.lines
				self.cursor = (row-1, len(self.lines[row-1]))
				print "part1", self.lines[:row-1]
				print "part2", [(self.lines[row-1]+self.lines[row])]
				print "part3", self.lines[row+1:]
				self.lines = self.lines[:row-1]+ [(self.lines[row-1]+self.lines[row])] + self.lines[row+1:]
		if keycode == gtk.keysyms.Left: 
			if col > 0:
				self.cursor = (row, col-1)
			else:
				self.cursor = (row-1, len(self.lines[row-1]))
		elif keycode == gtk.keysyms.Right:
			if col < len(self.lines[row]):
				self.cursor = (row, col+1)
			else:
				self.cursor = (row+1, 0)

t = ThrowawayDocument()
w = MyW(t)
for c in "test\n123\nlol\n":
	t.add(c)
for i in range(26):
	t.add(chr(ord('a')+i));
t.add('\n')
for i in range(26):
	t.add(chr(ord('A')+i));
t.add('\n')

def kepress(w, e):
	if (e.keyval < 128):
		t.add(chr(e.keyval))
	elif (e.keyval == gtk.keysyms.Return):
		t.add('\n')
	else:
		t.special(e.keyval)
	w.queue_draw()

window = gtk.Window()
window.connect('delete-event', gtk.main_quit)
window.connect('key_press_event', kepress)
w.show()
window.add(w)
window.present()
gtk.main()

