def fill_array():
	array = []
	choice = int(input("Enter a Number:"))
	while choice != -1:
		array.append(choice)
		choice = int(input("Enter a Number"))
	print(array)

fill_array()