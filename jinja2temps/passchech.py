#!/usr/bin/env python
import re
import getpass

password = ""
correctPassword = "1"
def passwordchecker(passwd=password, corpass=correctPassword):
    while passwd != corpass:
        passwd = getpass.getpass('Please enter password: ')
        corpass = getpass.getpass('Please repeat password: ')
        if re.search(r'[a-z]', passwd) and re.search(r'[A-Z]', passwd) and re.search(r'\d', passwd) and passwd == corpass:
            print('The password policy is worked!!!')
            break
        else:
            continue
#        else:
#            print(' Minimal length of password is 8. One upper case, one number and one lower case must be there... ')
#            continue
#        if passwd == corpass:
#            print('The password set successfully!')
#            break
        print('Entered passwords must be the same. Please enter passwords again. ')

passwordchecker(password, correctPassword)
#print('Success')
