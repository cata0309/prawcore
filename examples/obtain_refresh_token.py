#!/usr/bin/env python

"""This example demonstrates the flow for retrieving a refresh token.

In order for this example to work your application's redirect URI must be set
to http://localhost:8080.

This tool can be used to conveniently create refresh tokens for later use.

"""
import os
import prawcore
import random
import socket
import sys


def receive_connection():
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send('HTTP/1.1 200 OK\r\n\r\n{}'.format(message).encode('utf-8'))
    client.close()


def main():
    """main is the program's entry point when directly executed."""
    if len(sys.argv) < 2:
        print('Usage: {} SCOPE...'.format(sys.argv[0]))
        return 1

    authenticator = prawcore.Authenticator(
        os.environ['PRAWCORE_CLIENT_ID'],
        os.environ['PRAWCORE_CLIENT_SECRET'],
        os.environ['PRAWCORE_REDIRECT_URI'])

    state = str(random.randint(0, 65000))
    url = authenticator.authorize_url('permanent', sys.argv[1:], state)
    print(url)

    client = receive_connection()
    data = client.recv(1024).decode('utf-8')
    param_tokens = data.split(' ', 2)[1].split('?', 1)[1].split('&')
    params = {key: value for (key, value) in [token.split('=')
                                              for token in param_tokens]}

    if state != params['state']:
        send_message(client, 'State mismatch. Expected: {} Received: {}'
                     .format(state, params['state']))
        return 1
    elif 'error' in params:
        send_message(client, params['error'])
        return 1

    # TODO: Use the access code to obtain and then output the refresh token.
    send_message(client, 'Access code: {}'.format(params['code']))
    return 0


if __name__ == '__main__':
    sys.exit(main())