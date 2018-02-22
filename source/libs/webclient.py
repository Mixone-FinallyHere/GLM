#!/usr/bin/env python3

import json
import socket
import signal
import threading
from time import sleep
from ..libs.rainbow import msg

BUFFSIZE = 512


class WebClient():
    def __init__(self, server_ip="localhost", server_port=9999):
        super(WebClient, self).__init__()
        self.server_port = server_port
        self.server_ip = server_ip

        # Catch process closing
        signal.signal(signal.SIGTERM, self.close_connection)
        self.kill = False

        self.connected = False

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, server_port))

        self.data = ["<a href='google.com'>google</a>","<button>ok</button>"]

    def close_connection(self, signum, frame):
        self.kill = True

    def _get_data(self):
        """ Get web data from plugin
        """
        pass

    def _send_event(self):
        """ Send event to plugin
        """
        pass

    def _get_event_loop(self, user):
        """ Threaded event receive
        """
        self.client.send(user.encode()) # Send user name
        response = self.client.recv(BUFFSIZE).decode()
        msg(response, 0, "plugin_handler")
        if response == "a:client_connected":
            while not self.kill:
                if self.kill:
                    self.client.send(b"EOT") # Sending end signal to server
                    self.client.close()
                    self.connected = False
                    msg("killed", 3, "Process")
                # Get event
                event = json.loads(self.client.recv(BUFFSIZE).decode())
                msg("receive", 0, "plugin_handler", event)
                # Send data back
                self.client.send(json.dumps(self.data).encode())
                msg("send", 0, "plugin_handler", self.data)
        else:
            msg("Connection refused", 3)

    def handle_data(self, user="plugin"):
        """ Change handle_data name
        """
        if not self.connected:
            get_event = threading.Thread(
                target=self._get_event_loop,
                args=(user,),
                daemon=True
                )
            get_event.start()
            self.connected = True
            msg("starting", 2, "Thread")
