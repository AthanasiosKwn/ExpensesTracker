import bcrypt

password = "your_desired_password"
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
