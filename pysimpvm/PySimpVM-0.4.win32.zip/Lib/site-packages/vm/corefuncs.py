def push(i, l, stack):
	topush = int(l[i + 1], 16)
	stack.append(topush)
def pop(stack):
	stack.pop()
def clear_s(stack):
	for item in stack:
		stack.remove(item)