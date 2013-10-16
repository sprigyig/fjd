import sys
def dprint(*args):
	#sys.stdout.write(' '.join([str(x) for x in args])+'\n')
	pass

class _Node:
	__join_min = 16
	__imbal_tol = 5

	def __init__(s, l, r):
		s.l = l
		s.r = r
		s.len = l.len + r.len
		s.nl = s.l.nl+s.r.nl
		s.leaf = False

	def normalize(s):
		s.len = s.l.len + s.r.len
		s.nl = s.l.nl+s.r.nl

		if (s.l.leaf and s.r.leaf and s.len < _Node.__join_min):
			return _Leaf(s.l.c + s.r.c)

		elif (not s.l.leaf and s.l.len - s.r.len > _Node.__imbal_tol):
			l = s.l
			r = s.r
			ll, lr = l.l, l.r

			return _Node(ll, _Node(lr, r))

		elif (not s.r.leaf and s.r.len - s.l.len > _Node.__imbal_tol):
			l = s.l
			r = s.r
			rl, rr = r.l, r.r

			return _Node(_Node(l, rl), rr)

		return s

	def insert(s, seq, index):
		if index <= s.l.len:
			s.l = s.l.insert(seq, index)
		else:
			s.r = s.r.insert(seq, index-s.l.len)

		return s.normalize()

	def delete(s, index):
		if index < s.l.len:
			s.l.delete(index)
		else:
			s.r.delete(index)

		return s.normalize()

	def __getitem__(s, idx):
		if type(idx)==int:
			return s.l[idx] if idx < s.l.len else s.r[idx-s.l.len]
		elif type(idx)==slice:
			if idx.start < s.l.len:
				first = s.l[idx.start:min(idx.stop, s.l.len)]
				if idx.stop >= s.l.len+1:
					return first + s.r[:idx.stop-s.l.len]
				else:
					return first
			else:
				return s.r[idx.start-s.l.len:idx.stop-s.l.len]

	def line_index(s, line):
		if line > s.l.nl:
			return s.l.len+s.r.line_index(line-s.l.nl)
		else:
			return s.l.line_index(line)

	def row_col(s, index):
		if index > s.l.len:
			rc = s.r.row_col(index-s.l.len)
			return (rc[0]+s.l.nl, rc[1])
		else:
			return s.l.row_col(index)

	def index(s, row, col):
		if row > s.l.nl:
			return s.r.index(row-s.l.nl, col)+s.l.len 
		else:
			return s.l.index(row, col)

	def row_bounds(s, first, num, offset, list, depth = 0):
		added = 0
		if first > s.l.nl:
			dprint (' '*depth, 'going right only')
			added += s.r.row_bounds(first - s.l.nl, num, offset+s.l.len, list, depth=depth+1)
		else:
			dprint (' '*depth,'going left')
			added += s.l.row_bounds(first, num, offset, list, depth=depth+1)
			num -= added
			if num > 0:
				dprint (' '*depth, 'going right as well')
				added+=s.r.row_bounds(0, num, offset+s.l.len, list, depth=depth+1)

		return added

class _Leaf:
	__split_min = 32

	def __init__(s, content):
		s.c = content
		s.len = len(content)
		s.nl = s.c.count('\n')
		s.leaf = True

	def normalize(s):
		if s.len > _Leaf.__split_min:
			return _Node(_Leaf(s.c[:s.len//2]), _Leaf(s.c[s.len//2:]))
		return s

	def insert(s, seq, index):
		s.c = s.c[:index] + seq + s.c[index:]
		s.len += len(seq)
		s.nl += seq.count('\n')
		return s.normalize()

	def delete(s, index):
		s.len -=1
		s.nl -= 1 if s.c[index]=='\n' else 0
		s.c = s.c[:index]+s.c[index+1:]

	def __getitem__(s, idx):
		return s.c[idx]

	def line_index(s, line):
		if line > s.nl:
			return s.len
		else:
			last = -1
			for i in range(line):
				last = s.c.index('\n', last+1)
			return last+1

	def row_col(s, index):
		lastnl = s.c[:index].rfind('\n')
		return (s.c[:index].count('\n'), index-lastnl-1 if lastnl !=-1 else index)

	def index(s, row, col):
		if row > s.nl:
			return s.len
		i = 0
		while row:
			if s.c[i]=='\n':
				row-=1
			i+=1

		return i+col

	def row_bounds(s, first, num, offset, list, depth=0):
		dprint (' '*depth, first, num, offset, list, s.c.__repr__())
		added = 0
		if offset == 0 and first == 0:
			dprint(' '*depth, 'adding bare 0')
			list.append(0)
			added+=1
			num-=1

		i = 0
		while i<len(s.c) and first:
			if s.c[i]=='\n':
				first-=1
			i+=1

		if i:
			i-=1

		while i<len(s.c) and num:
			if s.c[i]=='\n':
				num-=1
				added+=1
				dprint(' '*depth, 'adding', i, offset, i+offset+1)
				list.append(i+offset+1)
			i+=1

		return added
				

class Rope:
	def __init__(self, init="", node=None):
		if not node:
			self.node = _Leaf(init)
		else:
			self.node = node

	def __len__(self):
		return self.node.len

	def __getitem__(self, idx):
		return self.node[idx]

	def line_index(self, num):
		return self.node.line_index(num)

	def line(self, num):
		return self[self.line_index(num):self.line_index(num+1)]

	def row_col(self, index):
		return self.node.row_col(index)

	def index(self, row, col):
		return self.node.index(row, col)

	def insert(self, seq, index):
		self.node = self.node.insert(seq, index)

	def row_bounds(self, first, num):
		l = []
		self.node.row_bounds(first, num + 1, 0, l)
		return l

	def lines(self, first, num):
		bounds = self.row_bounds(first, num)
		dprint(bounds)
		return [self[a:b] for a,b in zip(bounds[:-1],bounds[1:])]

test = Rope(node=_Node(_Leaf("line1 \nline2\n"),_Node(_Leaf("line3"),_Leaf("\nline4"))))
test2 = Rope()
for i in range(100):
	test2.insert("line %d\n"%i, len(test2))



for i in range(98):
	lines = tuple(test2.lines(i, 3))
	if lines != tuple(['line %d\n'%(i+x) for x in range(3)]):
		print test2.lines(i, 3), 'vs', ['line %d\n'%(i+x) for x in range(3)]

