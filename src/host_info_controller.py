#!/usr/bin/env python

import logging
import threading
import time

logger = logging.getLogger(__name__)

class HostInfoController(object):
    def __init__(self, host_info, polling_freq=5):
        self.host_info = host_info
        self.polling_freq = polling_freq
        self.polling_running = False
        self.polling_last_time = 0
        self.polling_thread = None
        self.callback = None

    def get_polling_freq(self):
        return self.polling_freq

    def set_polling_freq(self, polling_freq):
        self.polling_freq = polling_freq

    def start_polling(self):
        self.polling_running = True
        self.polling_thread = threading.Thread(target=self.__polling)
        self.polling_thread.start()
        logger.debug("Polling job started")

    def stop_polling(self):
        self.polling_running = False
        if self.polling_thread:
            self.polling_thread.join()
        logger.debug("Polling job stopped")

    def on_update(self, callback):
        if self.callback:
            logger.error("Callback for on_update already registered")
        else:
            self.callback = callback
    
    def __polling(self):
        while(self.polling_running):
            if (time.time() - self.polling_last_time > self.polling_freq):
                has_changed = self.host_info.update()
                if has_changed and self.callback:
                    logger.debug("Changes in the provider!")
                    self.callback(self.host_info.to_list())
                self.polling_last_time = time.time()
            time.sleep(0.5)