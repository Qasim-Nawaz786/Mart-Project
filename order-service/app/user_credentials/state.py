
user_credentials = set()


for credential in user_credentials:
    user_id, user_email, user_message = credential
    print(f"User ID: {user_id}, Email: {user_email}, Message: {user_message}")

    if user_email == 'user@example.com':
        print(f"Found the email: {user_email}")
