import argparse
import Parser

#FOR TEST
import os

# Symbols dictionary values:
# 1 symbol=True
# 0 symbol=False
#-1 symbol=Undefined

# def check_rule(rule):
# 	lhs_value = compute(rule['lhs'])
# 	rhs_value = compute(rule['rhs'])

# 	if lhs_value == True and rhs_value == False:
# 		return False
# 	if lhs_value == False and rhs_value == True and rule['sign'] == '<=>':
# 		return False

# 	return True

# def check(fact_rules):
# 	for rule in fact_rules:
# 		if (check_rule(rule) == False):
# 			return False
# 	return True


def evaluate(x1, x2, op):
	if (x1 == -1 or x2 == -1):
		if (op == '|' and (x1 == 1 or x2 == 1)):
			return 1
		if (op == '+' and (x1 == 0 or x2 == 0)):
			return 0
		return -1

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
				if get_priority(op_stack[-1]) > get_priority(token):
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
		if val != -1:
			val ^= 1
	else:
		val = facts[key]
	return val

def compute(rule):
	if len(rule) < 3:
		return get_val(rule)

	op_queue = to_rpn(Parser.tokenize(rule))
	operands = []
	result = None

	for elem in op_queue:
		if is_op(elem):
			x1 = operands.pop()
			x2 = operands.pop()
			result = evaluate(x1, x2, elem)
			operands.append(result)
		else:
			operands.append(get_val(elem))

	return result

def get_fact_rules(fact, rules):
	fact_rules = []
	for r in rules:
		if (fact in r['rhs']) or ((ch in r['lhs'] and r['sign'] == '<=>')):
			fact_rules.append(r)

	return fact_rules

def get_fact(ch, stack):
	#check if symbol is known already
	if facts[ch] != -1:
		return facts[ch]

	#check for recursive
	if ch in stack:
		return -1
	stack.insert(0, ch)

	#find all rhs in rules with symbol
	fact_rules = get_fact_rules(ch, rules_list)

	#if no rules for symbol then it is false by default
	if len(fact_rules) == 0:
		return -1

	for f_rule in fact_rules:
		lhs = 'lhs' if ch in f_rule['rhs'] else 'rhs' #TODO: process case when variable in two sides
		rhs = 'rhs' if ch in f_rule['rhs'] else 'lhs'

		for c in f_rule[lhs]:
			if (c >= 'A') and (c <= 'Z'):
				facts[c] = get_fact(c, stack)

		lhs_value = compute(f_rule[lhs])
		if lhs_value == -1:
			continue

		# rules_list[lhs_value] = lhs_value
		f_rule[lhs_value] = lhs_value

		if f_rule['sign'] == '<=>':
			# rules_list['rhs_value'] = lhs_value
			f_rule['rhs_value'] = lhs_value
		elif f_rule['sign'] == '=>' and lhs_value == 1:
			# rules_list['rhs_value'] = lhs_value
			f_rule['rhs_value'] = 1

		if f_rule['rhs_value'] == -1: #invalid rule
			continue

		if len(f_rule[rhs]) < 3: #if only element in rhs
			if f_rule[rhs][0] == '!':
				facts[ch] = not f_rule['rhs_value']
			else:
				facts[ch] = f_rule['rhs_value']
			return facts[ch]
		else:
			for c in f_rule[rhs]:
				if (c >= 'A') and (c <= 'Z') and (c != ch):
					facts[c] = get_fact(c, stack)

			#pretend symbol = false
			facts[ch] = 0
			ch_false = compute(f_rule[rhs])

			facts[ch] = 1
			ch_true = compute(f_rule[rhs])

			if ch_true == ch_false or \
				ch_true == -1 or ch_false == -1:
				facts[ch] = -1
				continue
			elif (ch_false == f_rule['rhs_value']):
				facts[ch] = 0
				return 0
			elif (ch_true == f_rule['rhs_value']):
				facts[ch] = 1
				return 1

	return facts[ch]

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('file', help='input file')
	args = parser.parse_args()

	file = open(args.file, 'r')
	facts, rules_list, queries = Parser.parse_file(file)
	file.close()

	for ch in queries:
		stack = []
		res = get_fact(ch, stack)
		if res == 1:
			print ("%c is True" %ch)
		elif res == 0:
			print ("%c is False" %ch)
		else:
			print ("%c is undefined" %ch)
