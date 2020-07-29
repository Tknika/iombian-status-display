#!/usr/bin/env python

import logging
import signal
import time

from epd_controller import EPDController
from iombian_info_provider import IoMBianInfoProvider
from host_info_controller import HostInfoController
from waveshare_epd import epd2in13_V2

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)-20s  - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    logger.debug("Stoping 'IoMBian Status Display' program...")
    info_controller.stop_polling()
    display.shutdown(["IoMBian Off", "{}".format(time.strftime('%H:%M'))])
    logger.info("'IoMBian Status Display' program stopped")


if __name__ == "__main__":
    logger.info("Starting 'IoMBian Status Display' program...")
    display = EPDController(epd2in13_V2)
    display.initialize()
    iombian_info = IoMBianInfoProvider()
    info_controller = HostInfoController(iombian_info)
    info_controller.on_update(display.render)
    info_controller.start_polling()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.pause()