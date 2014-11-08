from select import *
from sys import stdin, stderr

inputs = [ stdin ]
outputs = []

print >> stderr, '\nwaiting for the next event'
readable, writable, exceptional = select(inputs, outputs, inputs,10)

