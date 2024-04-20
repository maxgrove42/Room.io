import bcrypt


def hash_password(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())


def check_password(password_to_test, hashed_password):
    return bcrypt.checkpw(password_to_test.encode(), hashed_password.encode())
