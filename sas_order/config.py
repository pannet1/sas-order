login_id = "HW105"
password = "Hd04@now"
Totp = 'SVT7OUVZ4KGBE7T5'

try:
    access_token = open('access_token.txt', 'r').read().rstrip()
except Exception as e:
    print('Exception occurred :: {}'.format(e))
    access_token = None


login_id = "HW105"
password = "Hd04@now"
Totp = 'SVT7OUVZ4KGBE7T5'
