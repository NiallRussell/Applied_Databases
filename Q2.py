
# Main function
def main():
	# Initialise array
	array = []

	display_menu()
	
	while True:
		choice = input("Enter choice: ")
		
		if (choice == "1"):
			array = fill_array()
			display_menu()
		elif (choice == "2"):
			print(array)
			display_menu()
		elif (choice == "3"):
			find_gt_in_array(array)
			display_menu()
		elif (choice == "4"):
			break;
		else:
			display_menu()
			
			
def fill_array():
	array = []
	choice = int(input("Enter a Number:"))
	while choice != -1:
		array.append(choice)
		choice = int(input("Enter a Number"))
	print(array)


# Write the necessary code to fill the array.
# -1 should not be part of the array
# The following line of code is only to allow 
# the program to run.
# It should be deleted when you write your
# own code

	x = 1;


def find_gt_in_array(array):
# Write the necessary code to get a number from the user
# and print out all numbers in the array that are greater
# than this number

# The following line of code is only to allow 
# the program to run.
# It should be deleted when you write your
# own code
	x = 1;


def display_menu():
    print("")
    print("MENU")
    print("=" * 4)
    print("1 - Fill Array")
    print("2 - Print Array")
    print("3 - Find > in Array")
    print("4 - Exit")

if __name__ == "__main__":
	# execute only if run as a script 
	main()
