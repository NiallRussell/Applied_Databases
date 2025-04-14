array2 = [4,5,6,7,2,9]

def find_gt_in_array(array):
	list =[]
	choice = int(input("Enter a Number:"))
	for element in array:
		if element > choice:
			list.append(element)
		else:
			continue
	print(list)
		

find_gt_in_array(array2)