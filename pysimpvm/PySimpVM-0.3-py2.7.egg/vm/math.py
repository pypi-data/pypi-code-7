def add(stack):
	topush = stack[-1] + stack[-2]
	stack.pop()
	stack.pop()
	stack.append(topush)
def subtract(stack):
	topush = stack[-1] - stack[-2]
	stack.pop()
	stack.pop()
	stack.append(topush)
def divide(stack):
	topush = stack[-1] / stack[-2]
	stack.pop()
	stack.pop()
	stack.append(topush)
def multiply(stack):
	topush = stack[-1] * stack[-2]
	stack.pop()
	stack.pop()
	stack.append(topush)