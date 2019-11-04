import argparse
import re

def parse_rule(line):
	line = re.sub('#.*', '', line)
	line = re.sub('\\s*', '', line)
	print (line)
	lhs, rhs = re.compile("<=>|=>").split(line)
	pass

def parse_output(line):
	line = re.sub('#.*', '', line)
	line = re.sub('\\s*', '', line)

	for i in range(1, len(line)):
		ch = line[i]
		symbols_dict[ch] = True

def parse_query(line):
	line = re.sub('#.*', '', line)
	line = re.sub('\\s*', '', line)

	for i in range(1, len(line)):
		ch = line[i]
		query_list.append(ch)

parser = argparse.ArgumentParser()
parser.add_argument('file', help='input file')
args = parser.parse_args()

comment_reg = re.compile("^\\s*#.*")
rule_reg = re.compile("^!?\\w ((\\+|\\||\\^)( !?\\w ))*(=>|<=>) !?\\w( ((\\+|\\||\\^)( !?\\w ))*)*(#.*)?")
output_reg = re.compile("^=\\w+\\s*#.*")
query_reg = re.compile("^\?\\w+\\s*#.*")
symbols_dict = {}
query_list = []

f = open(args.file, 'r')
for i, line in enumerate(f):
	if len(line) < 2 or len(comment_reg.findall(line)) > 0:
		continue
	elif len(rule_reg.findall(line)) > 0:
		parse_rule(line)
	elif len(output_reg.findall(line)) > 0:
		parse_output(line)
	elif len(query_reg.findall(line)) > 0:
		parse_query(line)
	else:
		print ('Line %d: incorrect input' %(i+1))
	
f.close()