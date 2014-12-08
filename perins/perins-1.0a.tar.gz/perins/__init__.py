# Python 2 support
try: input = raw_input
except NameError: pass

print("Conversor Perin-Metros v0.1")
alturaPerin = 1.65
selecao = input('Metros -> Perins (1)\nPerins -> Metros(2)\nSair (0)\n')
while selecao != "0":
	if selecao == "1":
		metros = int(input('Insira metros: \n'))
		perins = metros/alturaPerin
		print('{} Perins'.format(perins))
	elif selecao == "2":
		perins = int(input('Insira perins: \n'))
		metros = perins*alturaPerin
		print('{}  metros'.format(metros))
	else:
		print("Selecione novamente!")
	selecao = input('Metros -> Perins (1)\nPerins -> Metros(2)\nSair (0)\n')

