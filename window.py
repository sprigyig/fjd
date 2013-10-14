import gtk
import cairo

bg = (1,1,1)
fg = (0,0,0)

class MyW(gtk.DrawingArea):
	__gsignals__ = { "expose-event":"override"}

	def __init__(self, csrc):
		self.csrc = csrc
		gtk.DrawingArea.__init__(self)

	def do_expose_event(self, event):
		width, height = self.window.get_size()
		cw,ch,cs = 8,11,11
		cr = self.window.cairo_create()
		cr.set_source_rgb(*bg)
		cr.rectangle(0,0,width,height)
		cr.fill()

		cr.set_source_rgb(*fg)
		cr.select_font_face("Courier")
		cr.set_font_size(cs)

		for row in range(height//ch):
			for col in range(width//cw):
				cr.move_to(cw*col, ch * (row + 1))
				cr.show_text(self.content(row,col))


class ThrowawayDocument:
	def __init__(self):
		self.lines = [[]]

	def add(self, chr):
		if chr == '\n':
			self.lines += [[]]
		else:
			self.lines[-1]+=[chr]

	def content(self, row, col):
		if row < len(self.lines):
			r = self.lines[row]
			if col < len(r):
				return r[col]
			elif col == len(r) and row == len(self.lines)-1:
				return '|'
		return ' '
	def back(self):
		if self.lines[-1]:
			self.lines[-1] = self.lines[-1][:-1]
		elif len(self.lines) - 1:
			self.lines = self.lines[:-1]

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
	elif (e.keyval == gtk.keysyms.BackSpace):
		t.back()
	w.queue_draw()

window = gtk.Window()
window.connect('delete-event', gtk.main_quit)
window.connect('key_press_event', kepress)
w.show()
window.add(w)
window.present()
gtk.main()

