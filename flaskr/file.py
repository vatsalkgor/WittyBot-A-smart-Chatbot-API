def file_len(fname1,fname2):
    with open(fname1) as f:
    	f1 = open(fname2) 
        for i,j in zip(f,f1):
           	# print(i,l)
           	print(i,j)

file_len('templates/dashboard.html','templates/login.html')