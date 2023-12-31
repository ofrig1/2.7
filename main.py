"""
author - Ofri Guz
date   - 19/11/23
socket server
"""
import socket
import logging
import glob
import os
import shutil
import subprocess
import pyautogui
import protocol

IP = '127.0.0.1'
PORT = 8820
QUEUE_SIZE = 1
MAX_PACKET = 1024
PERSON_NAME = "Ofri"
DIR = 'DIR'
DELETE = 'DELETE'
COPY = 'COPY'
EXECUTE = 'EXECUTE'
TAKE_SCREENSHOT = 'TAKE_SCREENSHOT'
SEND_PHOTO = 'SEND_PHOTO'
EXIT = 'EXIT'
SEPERATOR = '|'
LIST = 'list'
PHOTO = 'photo'
TEXT = 'text'
ERROR = 'error'


def protocol_send(message, message_type):
    """
    Protocol to send message from server to client
    :param message: message to send
    :param message_type: TEXT, PHOTO, LIST, ERROR
    :return: message with message len and message type (message after protocol)
    """
    try:
        message_payload = str(message_type) + SEPERATOR + str(message)
        message_len = len(message_payload)
        final_message = str(message_len) + SEPERATOR + message_payload
        logging.debug("final msg " + final_message)
        return final_message
    except Exception as e:
        return f"Error: {e}. Server message failed to send to client with protocol"


def dir1(directory):
    """
    DIR function
    :param directory:
    :return: str of files in dir separated by SEPERATOR
    """
    try:
        if not os.path.exists(directory):
            print(f"The directory '{directory}' does not exist.")
            return 'Directory does not exist'
        directory += os.path.sep + '*.*'
        files_list = glob.glob(directory)
        file_str = ""
        for item in files_list:
            file_str += item + SEPERATOR
        return file_str
    except Exception as e:
        return f"Error: {e}. Dir function failed"


def delete(file):
    """
    remove file
    :param file: file to be removed
    :return: file removed/can not be removed message
    """
    try:
        os.remove(file)
        return "% s removed" % file
    except OSError:
        return "File path can not be removed"


def copy(text1, text2):
    """
    Copies text1 to text2
    :param text1: file to be copied
    :param text2: file to copy to
    :return: Contents copied/not copied
    """
    try:
        shutil.copy(text1, text2)
        return f"Content of {text1} copied to {text2}"
    except Exception as e:
        return f"Error: {e}. Text could not be copied"


def execute(app):
    """
    Open application
    :param app: application wanted to open
    :return: A msg indicating success or failure
    """
    try:
        subprocess.call(app)
        return "% s opened" % app
    except Exception as e:
        return f"Error: {e}. App could not be opened"


def take_screenshot():
    """
    take a screenshot
    :return: A msg indicating success or failure
    """
    try:
        image = pyautogui.screenshot()
        image.save(r'screen.jpg')
        return "took screenshot"
    except pyautogui.FailSafeException:
        return "Cannot take screenshot: Mouse is in the upper-left corner"
    except Exception as e:
        return f"An error occurred: {e}"


def send_photo(client_socket):
    """
    Sends photo to client
    :return:
    """
    try:
        file_path = r'screen.jpg'
        if os.path.exists(file_path):
            my_file = open(file_path, 'rb')
            bytes1 = my_file.read()
            my_file.seek(0)
            my_file.close()

            pic_stats = os.stat(file_path)
            pic_size = pic_stats.st_size

            reply = str(pic_size)
            client_socket.send(protocol_send(reply, PHOTO).encode())
            client_socket.send(bytes1)
        else:
            client_socket.send(protocol_send('file doesn\'t exist ', ERROR).encode())
    except Exception as e:
        return f"Error: {e}. Send photo failed"


def exit_client():
    """
    close the client connection
    :param:
    :return: "Socket Connection Closed" message
    """
    return "Socket Connection Closed"


def random_word(client_socket):
    """
    client sent a message - not one of the available functions
    :param client_socket:
    :return: "Not one of the available functions" message
    """
    try:
        print("Client sent random word")
        client_socket.send(protocol_send("Not one of the available functions", ERROR).encode())
    except Exception as e:
        return f"Error: {e}."


def handle_msg(client_socket):
    """
    Handles message that client sent
    Sends client what they requested
    :param client_socket:
    :return:
    """
    try:
        while True:
            request_list = protocol.protocol_receive(client_socket)
            print("Client sent " + str(request_list))
            if request_list[0] == DIR:
                if len(request_list) == 2:
                    dir_response = dir1(request_list[1])
                    if dir_response == 'Directory does not exist':
                        client_socket.send(protocol_send(dir_response, ERROR).encode())
                    else:
                        client_socket.send(protocol_send(dir1(request_list[1]), LIST).encode())
                else:
                    client_socket.send(protocol_send('Expecting one argument', ERROR).encode())
            elif request_list[0] == DELETE:
                if len(request_list) == 2:
                    client_socket.send(protocol_send(delete(request_list[1]), TEXT).encode())
                else:
                    client_socket.send(protocol_send('Expecting one argument', ERROR).encode())
            elif request_list[0] == COPY:
                if len(request_list) == 3:
                    client_socket.send(protocol_send(copy(request_list[1], request_list[2]), TEXT).encode())
                else:
                    client_socket.send(protocol_send('Expecting two argument', ERROR).encode())
            elif request_list[0] == EXECUTE:
                if len(request_list) == 2:
                    client_socket.send(protocol_send(execute(request_list[1]), TEXT).encode())
                else:
                    client_socket.send(protocol_send('Expecting one argument', ERROR).encode())
            elif request_list[0] == TAKE_SCREENSHOT:
                client_socket.send(protocol_send(take_screenshot(), TEXT).encode())
            elif request_list[0] == SEND_PHOTO:
                send_photo(client_socket)
            elif request_list[0] == EXIT:
                client_socket.send(protocol_send(exit_client(), TEXT).encode())
                break
            else:
                random_word(client_socket)
            logging.debug("Server received " + str(request_list))
            print('server received ' + str(request_list))
    except socket.error as err:
        print('received socket error on client socket' + str(err))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        client_socket.close()
        logging.debug("Client Socket Disconnected")


def main():
    logging.basicConfig(filename="server.log", level=logging.DEBUG)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        while True:
            client_socket, client_address = server_socket.accept()
            handle_msg(client_socket)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    assert dir1('C:\\work\\cyber') != 'Directory does not exist', "Existing directory shouldn't return an error message"
    # Test case: Try to delete a nonexistent file
    assert delete('C:\\work\\cyber\\nonexistent.txt') == 'File path can not be removed', "Can't delete nonexistent file"
    # Test case: Try to execute a nonexistent application
    assert execute('no.exe') == "Error: [WinError 2] The system cannot find the file specified. App could not be opened"
    # Test case: Create a test file and copy it
    test_file_path = 'C:\\work\\cyber\\test_file.txt'
    with open(test_file_path, 'w') as test_file:
        test_file.write("This is a test file.")
    copy_test = copy(test_file_path, 'C:\\work\\cyber\\copy_file.txt')
    assert copy_test == 'Content of C:\\work\\cyber\\test_file.txt copied to C:\\work\\cyber\\copy_file.txt'
    # Test case: Delete the copied file
    delete_result = delete('C:\\work\\cyber\\copy_file.txt')
    main()
