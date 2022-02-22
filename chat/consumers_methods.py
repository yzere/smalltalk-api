def check_message_code(message):
    if message[0] == '#':
        try:
            x = int(message[1:4])
        except ValueError:
            return '#004'
        else:
            return message[0:4]
    else:
        return '#000'