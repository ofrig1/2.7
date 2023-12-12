SEPERATOR = '|'


def protocol_receive(my_socket):
    """
    Protocol to receive message from client to server
    :param my_socket:
    :return: message sent from client
    """
    try:
        cur_char = ''
        message_len = ''
        while cur_char != SEPERATOR:
            cur_char = my_socket.recv(1).decode()
            # print("char "+cur_char)
            if cur_char != SEPERATOR:
                message_len += cur_char
        final_message = my_socket.recv(int(message_len)).decode()
        final_list = final_message.split(SEPERATOR)
        return final_list
    except Exception as e:
        return f"Error: {e}. Server failed to receive client message"
