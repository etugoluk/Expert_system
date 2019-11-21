import re

RULE_REG = re.compile(r"^([A-Z\(\)\+\^\|\!]+)(<?=>)([A-Z\(\)\+\^\|\!]+)$")
OUTPUT_REG = re.compile(r"^=[A-Z]*$")
QUERY_REG = re.compile(r"^\?[A-Z]+$")
TOKEN_REG = re.compile(r"!?\S")

class ParserError(Exception):
	def __init__(self, info):
		super(ParserError, self).__init__("ParserError: " + info + '.')

class LexicalError(Exception):
	def __init__(self, info):
		super(LexicalError, self).__init__("LexicalError: " + info + '.')

def tokenize(rule):
	return re.findall(TOKEN_REG, rule)

def is_rule_side_valid(line):
	left_br = 0
	right_br = 0
	fact = 0
	sign = 0

	for c in line:
		if right_br > left_br:
			raise ParserError('Invalid brackets')
		elif c >= 'A' and c <= 'Z':
			if fact == 1: #previous symbol was fact
				return False
			fact = 1
			sign = 0
		elif c in ('+|^'):
			if sign == 1: #previous symbol was sign
				return False
			fact = 0
			sign = 1
		elif c == '!':
			if fact == 1:
				return False
		elif c == '(':
			if fact == 1:
				return False
			left_br += 1
		elif c == ')':
			if sign == 1:
				return False
			right_br += 1
		else:
			raise LexicalError('Unknown symbol %s' %c)

	if (right_br != left_br):
		raise ParserError('Invalid brackets')

	return True

def parse_rule(line, facts):
	match = re.findall(RULE_REG, line)
	if (len(match) == 0):
		raise ParserError('Incorrect rule')

	rule = {}
	rule['lhs'], rule['sign'], rule['rhs'] = match[0]
	if is_rule_side_valid(rule['lhs']) == False or \
		is_rule_side_valid(rule['rhs']) == False:
		raise ParserError('Incorrect rule')
	rule['lhs_value'], rule['rhs_value'] = -1, -1

	for ch in rule['lhs']:
		if (ch >= 'A') and (ch <= 'Z'):
			facts[ch] = -1

	for ch in rule['rhs']:
		if (ch >= 'A') and (ch <= 'Z'):
			facts[ch] = -1

	return rule

def parse_output(line, facts):
	for i in range(1, len(line)):
		ch = line[i]
		facts[ch] = 1

def parse_query(line, facts):
	query_list = []
	for i in range(1, len(line)):
		ch = line[i]
		if ch not in facts:
			raise LexicalError("query not found: %s" %ch)
		query_list.append(ch)
	return query_list

def parse_file(file):
	facts = {}
	rules = []
	queries = []

	output_flag = 0
	query_flag = 0
	try:
		for i, line in enumerate(file):
			line = re.sub('#.*', '', line)
			line = re.sub('\\s*', '', line)
			if not line:
				continue
			elif len(RULE_REG.findall(line)) > 0:
				if output_flag:
					raise ParserError("rule after output")
				if query_flag:
					raise ParserError("rule after query")
				rule = parse_rule(line, facts)
				rules.append(rule)
			elif len(OUTPUT_REG.findall(line)) > 0:
				if query_flag:
					raise ParserError("output after query")
				parse_output(line, facts)
				output_flag = 1
			elif len(QUERY_REG.findall(line)) > 0:
				if query_flag:
					raise ParserError("multiple query")
				queries = parse_query(line, facts)
				query_flag = 1
			else:
				raise ParserError('incorrect input on line %d' %(i+1))

		if output_flag == 0:
			raise ParserError("no output expression")
		if query_flag == 0:
			raise ParserError("no query expression")
	except Exception as e:
		print (e)
		exit (0)

	return facts, rules, queries
