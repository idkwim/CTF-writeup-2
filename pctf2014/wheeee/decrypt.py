from hashlib import sha512,sha1
import random,commands

KEY = [0, 0]

M = 12
N = M * 2
K = N
numrounds = 2 ** 24 # Protip: would not bruteforce this if I were you.

def genTable(seed="Function shamelessly stolen from bagre"):
  fSub = {}
  i = 0
  prng = sha512()
  prng.update(seed)
  seed = prng.digest()
  cSeed = ""
  for x in xrange(2048):
    cSeed+=prng.digest()
    prng.update(str(x)+prng.digest())
  fCharSub = [0]*(2**M)
  gCharSub = [0]*(2**M)
  unused = range(2**M)
  for x in xrange(0,2**(M+1),2):
    curInd = (ord(cSeed[x]) + (ord(cSeed[x + 1]) << 8)) % len(unused)
    toDo = unused[curInd]
    del unused[curInd]
    fSub[x / 2] = toDo
  return fSub

def inv_table(table):
	f_inv = {}
	for i in xrange(2**M):
		f_inv[table[i]] = i

	return f_inv

f = genTable()
f2 = genTable("Good thing I didn't also steal the seed!")

f_inv = inv_table(f)
f2_inv = inv_table(f2)


def gen_key():
  k0 = random.randint(0,2**(K/2)-1)
  k1 = random.randint(0,2**(K/2)-1)
  return [k0, k1]

def F(s, k):
  return f[s ^ k]

def F2(s, k):
  return f2[s^k]

def get_key(key, n):
  return key[n & 1]

def decrypt_block(ciphertext, key):
	txt = ciphertext
	l, r = (txt >> M) & ((1 << M) - 1), txt & ((1 << M) - 1)
	for x in xrange(numrounds):
		if x % 2 == 1:
			r1 = l
			l1 = r ^ F(l,key[0])
			l,r = l1,r1
		else:
			l1 = l
			r1 = f2_inv[r^l] ^ key[1]
			l,r = l1,r1

	return l << M | r
				

def encrypt_block(plaintext, key):
  txt = plaintext
  l, r = (txt >> M) & ((1 << M) - 1), txt & ((1 << M) - 1)
  for x in xrange(numrounds):
    if x % 2 == 0:
      l1 = r
      r1 = l ^ F(r, key[0])
      l, r = l1, r1
    else:
      l1 = l
      r1 = l ^ F2(r, key[1])
      l, r = l1, r1
  return l << M | r

def extract(s):
  c = 0
  for x in s:
    c = (c << 8) | ord(x)
  return c

def intract(n):
  s = []
  while n > 0:
    s.append(chr(n & 0xff))
    n = n >> 8
  return ''.join(s[::-1])

def get_blocks(txt):
  n = N / 8
  if len(txt) % n != 0:
    txt += '\x00' * (n - len(txt) % n)
  block_strs = [txt[i*n:i*n+n] for i in range(len(txt) / n)]
  return [extract(s) for s in block_strs]

def unblocks(l):
  z = [intract(x) for x in l]
  s = ''.join(z)
  s = s.strip('\x00')
  return s

def encrypt(plaintext,key):
  blocks = get_blocks(plaintext)
  out = [encrypt_block(block, key) for block in blocks]
  return unblocks(out)

def decrypt(ciphertext, key):
	blocks = get_blocks(ciphertext)
	out = [decrypt_block(block, key) for block in blocks]
	return unblocks(out)



def dblround(plaintext, key):
	txt = plaintext
	l, r = (txt >> M) & ((1 << M) - 1), txt & ((1 << M) - 1)
	for x in xrange(2):
		if x % 2 == 0:
			l1 = r
			r1 = l ^ F(r, key[0])
			l, r = l1, r1
		else:
			l1 = l
			r1 = l ^ F2(r, key[1])
			l, r = l1, r1
	return l << M | r


def get_key(plain1, plain2, enc1, enc2):
	possible = []
	for key1 in xrange(0, 2**(K/2)):
		for key2 in xrange(0, 2**(K/2)):
			if dblround(plain1, [key1,key2]) == plain2 and dblround(enc1, [key1,key2]) == enc2:
				possible.append([key1,key2])

	return possible

enc = "ed0c07f92d22901889faf1322a792eb5cd6898094cf68fdd4a89c27a3c3cbbf9361bdda5ccdd20e1b575faf132d050e40d81dd70188496308e29c1da3bd85786f021e3b1e3754cb240d98c"
print decrypt(enc.decode("hex"), [962,4064])
print decrypt(enc.decode("hex"), [2161,850])

"""
f = open('enc_data', 'r')
data = f.read().replace("\n", "")
f.close()
print len(data)
plain1 = 0
enc1 = int(data[:6],16)
data = data[6:]
print len(data)
print "plain1 : %x, enc1 : %x" % (plain1, enc1)
data = [int(data[x:x+6],16) for x in xrange(0, len(data), 6)]
for x in xrange(0, len(data)):
	plain2 = x + 1
	enc2 = data[x]
	#print "plain2 : %x, enc2 : %x" % (plain2, enc2)
	result = commands.getstatusoutput("./crack_dblround %d %d %d %d" %(plain1,plain2,enc1,enc2))[1]
	if result != '':
		print result
"""
