# -*- coding: utf-8 -*-
SHORT = (False,'Password too short')
LONG = (False,'Password too long')
MISSED_CHAR = (False,'Character is missed')
MISSED_NUMBER = (False,'Number is missed')
MISSED_SMALL_LETTER = (False,'Small letter is missed')
MISSED_BIG_LETTER = (False,'Big letter is missed')
TOO_MANY_BIG_LETTERS = (False, 'Too many big letters')
NOT_ALLOWED_CHAR = (False, 'Character not allowed')
PASSWORD_OK = (True, 'Password OK')
MIN_LENGTH = 8
MAX_LENGTH = 63

def password(password):
    ''' At least 8 characters, small/big letters (up to 2 big letters)
        At least 1 number
        At least one special character'''
    
    def check_len(password):
        if len(password) < MIN_LENGTH :
            return SHORT 
        elif len (password) > MAX_LENGTH:
            return LONG
        else:
            return None
        
    def countr_chars(password):
        small_ctr, big_ctr, numbers_ctr, char_ctr, not_all = 0, 0, 0, 0, 0
        small_all = 'abcdefghijklmnopqrstuvwxyz'
        big_all = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        numbers_all = '1234567890'
        char_all ='!@#$%^&*()'
        
        for letter in password:
            if letter in small_all:
                small_ctr +=1
            elif letter in big_all:
                big_ctr +=1
            elif letter in numbers_all:
                numbers_ctr += 1
            elif letter in char_all:
                char_ctr +=1
            else:
                not_all +=1 
        return small_ctr, big_ctr, numbers_ctr, char_ctr, not_all
        
            
    def check_conditions(small_ctr, big_ctr, numbers_ctr, char_ctr, not_all):
        if not_all >0:
            return NOT_ALLOWED_CHAR
        elif char_ctr < 1:
            return MISSED_CHAR
        elif numbers_ctr < 1:
            return MISSED_NUMBER
        elif big_ctr <1:
            return MISSED_BIG_LETTER
        elif small_ctr <1:
            return MISSED_SMALL_LETTER
        elif big_ctr >2:
            return TOO_MANY_BIG_LETTERS
        return PASSWORD_OK
        
    if check_len(password) != None:
        return check_len(password)
    else:
        small_ctr, big_ctr, numbers_ctr, char_ctr, not_all = countr_chars(password)
        return check_conditions(small_ctr, big_ctr, numbers_ctr, char_ctr, not_all)

if __name__ =='__main__':
    arr = ['smallL!ft62','sa)Light14','lu(kyBlob20','br@veOwl20','loudBo@t66',\
           'qu!ckBull66','limeL@mp98','sl!myKite79','h@ppyLeaf24','blu3Flower81',\
           'sillymass40','ultratime70','sMartrose','itchyfang96','hotthing65',\
           'swettpassword','sweet24','pass','fas+Walrus70','fasfSD-s70','78fsdSAD!',\
           'braV3TREe1!','!09@$%BD','3$5^PO1(','abbaBD!@','pos#fm@#$R','ytr12)(!',\
           '#$asds21']
    for sngl_pass in arr:
        print (sngl_pass,password(sngl_pass))