"""
author - Ofri Guz
date   - 19/11/23
client server
"""

import socket
import logging
import protocol

MAX_PACKET = 1024
IP = '127.0.0.1'
PORT = 8820
LIST = 'list'
PHOTO = 'photo'
TEXT = 'text'
ERROR = 'error'
SEPERATOR = '|'


def protocol_client_send(message):
    """
    send message with protocol
    :param message: message to be sent
    :return: message after protocol
    """
    try:
        message_len = len(message)
        final_message = str(message_len) + SEPERATOR + message
        return final_message
    except Exception as e:
        return f"Error: {e}. Client message failed to send to server with protocol"


def parse_command(user_input):
    """
    Split message with seperator
    :param user_input: Message to split with seperator
    :return: Split message
    """
    parts = []
    current_part = ''
    inside_quotes = False
    for char in user_input:
        if char == ' ' and not inside_quotes:
            if current_part:
                parts.append(current_part)
                current_part = ''
        elif char == '"' or char == "'":
            inside_quotes = not inside_quotes
        else:
            current_part += char
    if current_part:
        parts.append(current_part)
    my_string = SEPERATOR.join(parts)
    return my_string


def main():
    """
    Sends messages to server and get responses
    :return:
    """
    logging.basicConfig(filename="client.log", level=logging.DEBUG)
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((IP, PORT))
        print("Enter one of the following commands:\n\rDIR, DELETE, COPY, EXECUTE, TAKE_SCREENSHOT, SEND_PHOTO")
        while True:
            msg = input("Enter message: ")
            logging.debug("User input: " + msg)
            final_msg = parse_command(msg)
            my_socket.send(protocol_client_send(final_msg).encode())
            response = protocol.protocol_receive(my_socket)
            type1 = response[0]
            if type1 == LIST:
                response_list = response[1:]
                for item in response_list:
                    print(item)
            elif type1 == TEXT:
                if len(response) != 2:
                    print('unexpected response for message type text')
                else:
                    print(response[1])
            elif type1 == ERROR:
                if len(response) != 2:
                    print('unexpected response for message type error')
                else:
                    print("error received " + response[1])
            elif type1 == PHOTO:
                if len(response) != 2:
                    print('unexpected response for message type error')
                else:
                    size_str = response[1]
                    size = int(size_str)
                    picture2 = my_socket.recv(size)
                    my_file = open(r'screen_client.jpg', 'wb')
                    my_file.write(picture2)
                    my_file.close()
            if msg == "EXIT":
                break
    except socket.error as err:
        print('received socket error ' + str(err))
    finally:
        logging.debug("Closing Client Socket")
        my_socket.close()


if __name__ == "__main__":
    main()
