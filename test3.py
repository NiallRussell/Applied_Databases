month = 6
nums = list(range(1,13))
words = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
valid = dict(zip(words, nums))

if month not in valid.values():
	print("no")