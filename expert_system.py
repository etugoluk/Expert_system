#!/usr/bin/python

import argparse
import Parser

class LogicalError(Exception):
	def __init__(self, info):
		super(LogicalError, self).__init__("LogicalError: " + info + '.')

def calculate(x1, x2, op):
	if (x1 == None or x2 == None):
		if (op == '|' and (x1 == True or x2 == True)):
			return True
		if (op == '+' and (x1 == False or x2 == False)):
			return False
		return None

	if op == '+':
		res = x1 & x2
	elif op == '|':
		res = x1 | x2
	elif op == '^':
		res = x1 ^ x2

	return res

def is_var(token):
	offs = int(token[0] == '!')
	return token[offs:].isalpha()

def is_op(token):
	return token in '+|^'

def get_priority(op):
	return '^|+'.index(op)

def to_rpn(tokens):
	out_queue = []
	op_stack = []
	for token in tokens:
		if is_var(token):
			out_queue.append(token)
		elif is_op(token):
			for op in list(op_stack[::-1]):
				if op_stack[-1] != '(' and get_priority(op_stack[-1]) > get_priority(token):
					out_queue.append(op_stack[-1])
					del op_stack[-1]
				else:
					break
			op_stack.append(token)
		elif token == '(':
			op_stack.append(token)
		elif token == ')':
			for op in list(op_stack[::-1]):
				if op == '(':
					del op_stack[-1]
					break
				else:
					out_queue.append(op)
					del op_stack[-1]
	out_queue += op_stack[::-1]
	return out_queue

def get_val(key):
	if key[0] == '!':
		val = facts[key[1]]
		if val != None:
			val ^= True
	else:
		val = facts[key]
	return val

def compute_lhs(rule):
	if len(rule) < 3:
		return get_val(rule)

	op_queue = to_rpn(Parser.tokenize(rule))
	operands = []
	result = None

	for elem in op_queue:
		if is_op(elem):
			x1 = operands.pop()
			x2 = operands.pop()
			result = calculate(x1, x2, elem)
			operands.append(result)
		else:
			operands.append(get_val(elem))

	return result

def compute_fact_in_rhs(fact, rule, rule_value, facts):
	tokens = Parser.tokenize(rule)
	len_tokens = len(tokens)

	if len_tokens > 3:
		if verbose:
			print ('Too much facts in conclusion - should be no more than 2. Skipping rule...')
	elif len_tokens == 1:
		if len(tokens[0]) == 1:
			facts[fact] = rule_value
		elif len(tokens[0]) == 2:
			facts[fact] = not rule_value
	else:
		x1, op, x2 = tokens

		#x1 should be our search fact
		if fact in x2:
			x1, x2 = x2, x1

		if x2[0] == '!':
			x2_fact = x2[1]
		else:
			x2_fact = x2
		compute_fact(x2_fact, stack)
		x2_value = get_val(x2)
		if op == '+':
			if x2_value == True:
				facts[fact] = rule_value
				facts[fact] = get_val(x1)
			elif rule_value == True and x2_value == None:
				facts[fact] = True
				facts[x2_fact] = True
				facts[fact] = get_val(x1)
				facts[x2_fact] = get_val(x2)
		elif op == '|':
			if x2_value == False:
				facts[fact] = rule_value
				facts[fact] = get_val(x1)
			elif rule_value == False and x2_value == None:
				facts[fact] = False
				facts[x2_fact] = False
				facts[fact] = get_val(x1)
				facts[x2_fact] = get_val(x2)
		elif op == '^':
			if rule_value == x2_value:
				facts[fact] = False
				facts[fact] = get_val(x1)
			else:
				facts[fact] = True
				facts[fact] = get_val(x1)

def get_fact_rules(fact, rules):
	fact_rules = []
	for r in rules:
		if (fact in r['rhs']) or ((ch in r['lhs'] and r['sign'] == '<=>')):
			fact_rules.append(r)

	return fact_rules

def compute_fact(ch, stack):
	if verbose:
		print ("Let's find out what %c is." %ch)
	#check if symbol is known already
	if facts[ch] != None:
		return

	#check for recursive
	if ch in stack:
		if verbose:
			print ("Fact %c is already in stack." %ch)
		return
	stack.insert(0, ch)

	undefined_ch_flag = 0

	#find all rhs in rules with symbol
	fact_rules = get_fact_rules(ch, rules_list)
	for f_rule in fact_rules:
		if verbose:
			print ('Look at the rule: %s%s%s.' %(f_rule['lhs'], f_rule['sign'], f_rule['rhs']))

		lhs = 'lhs' if ch in f_rule['rhs'] else 'rhs' #TODO: process case when variable in two sides
		rhs = 'rhs' if ch in f_rule['rhs'] else 'lhs'

		if f_rule[lhs + '_value'] == None:
			for c in f_rule[lhs]:
				if (c >= 'A') and (c <= 'Z'):
					compute_fact(c, stack)
					if verbose:
						print ('%s is %d' %(c, facts[c]))

			f_rule[lhs + '_value'] = compute_lhs(f_rule[lhs])

		if f_rule[lhs + '_value'] == None:
			if verbose:
				print ('Can\'t make decision about condition side. Skipping rule...')
			continue
		if verbose:
			print ('So condition side %s is equal %d.' %(f_rule[lhs], f_rule[lhs + '_value']))

		if f_rule[rhs + '_value'] == None:
			if f_rule['sign'] == '<=>':
				f_rule[rhs + '_value'] = f_rule[lhs + '_value']
			elif f_rule['sign'] == '=>' and f_rule[lhs + '_value'] == True:
				f_rule[rhs + '_value'] = True

		if f_rule[rhs + '_value'] == None: #invalid rule
			if verbose:
				print ('Can\'t make decision about conlusion side. Skipping rule...')
			continue

		if verbose:
			print ('So conclusion side %s is equal %d.' %(f_rule[rhs], f_rule[rhs + '_value']))

		prev_fact = facts[ch]
		compute_fact_in_rhs(ch, f_rule[rhs], f_rule[rhs + '_value'], facts)
		if prev_fact != None and prev_fact != facts[ch]:
			raise LogicalError('Contradiction in rules for %c' %ch)

		if facts[ch] == None:
			undefined_ch_flag = 1
		else:
			undefined_ch_flag = 0

	if undefined_ch_flag == 1:
		return

	if facts[ch] == None:
		if verbose:
			print ("No appropriate rules for fact %c. Setting it to False by default." %ch)
		facts[ch] = False

def read_new_statements():
	global queries
	print('\nEnter new statements (=XYZ)')
	statements = input()
	if len(Parser.OUTPUT_REG.findall(statements)) == 0:
		raise Parser.ParserError("incorrect statements")
	Parser.parse_output(statements, facts)
	print('Enter new queries (?XYZ)')
	query = input()
	if len(Parser.QUERY_REG.findall(query)) == 0:
		raise Parser.ParserError("incorrect query")
	queries = Parser.parse_query(query, facts)

def reset_conclusions():
	for key in facts:
		facts[key] = None

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('file', help='input file')
	parser.add_argument('-v', '--verbose', help='verbose logs', default=False, action='store_true')
	parser.add_argument('-i', '--interactive', help='interactive mode', default=False, action='store_true')
	args = parser.parse_args()
	verbose = args.verbose
	interactive = args.interactive

	file = open(args.file, 'r')
	facts, rules_list, queries = Parser.parse_file(file)
	file.close()

	try:
		if interactive:
			with open(args.file, 'r') as file:
				print('=====Initial rules====')
				for line in file:
					print(line, end = '')
				print('=======================')
		while True:
			for ch in queries:
				stack = []
				compute_fact(ch, stack)
				if facts[ch] != None:
					print ("%c is %s" %(ch, facts[ch]))
				else:
					print ("%c is undetermined" %ch)
			if not interactive:
				break
			reset_conclusions()
			read_new_statements()
	except Exception as e:
		print (e)
		exit (0)
