#!/usr/bin/env python
import sys, time
import iio
import argparse
import numpy as np
import json
import subprocess
import logging
import signal


logger = logging.getLogger('main.py')
logger.setLevel(logging.DEBUG)
formatstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(formatstr)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

def terminate(signalNumber, frame):
    logger.debug(f'Recieved {signalNumber}')
    sys.exit()

def parse_config(arguments):
    """ чтение .json файла """
    f = open(arguments.config, 'r', encoding='utf-8')
    json_conf = json.load(f)
    return json_conf

class Arguments:
    """Class for parsing the input arguments."""

    def __init__(self):
        """Arguments class constructor."""
        self.parser = argparse.ArgumentParser(description="iio_readdev")
        self._add_parser_arguments()
        self.args = self.parser.parse_args()
        self.config = str(self.args.config)
        self.log_file = self.args.log_file

    def _add_parser_arguments(self):
        self.parser.add_argument(
            "-c",
            "--config",
            type=str,
            help="Scan for available contexts and if only one is available use it.",
        )
        self.parser.add_argument(
            "-l",
            "--log-file",
        )


class DataReader:
    """Class for reading samples from the device."""

    def __init__(self, ctx, config):
        self.ctx = ctx
        self.config = config

        self._devices()
        self._activate_channels(self.acc_dev)

    def _devices(self):
        self.acc_dev = self.ctx.find_device(self.config['accel'])
        if (self.acc_dev is None):
            raise Exception("Devices not found!")
        return self

    def _activate_channels(self, device):
        for channel in device.channels:
            channel.enabled = True
        return self

    def _read(self, device):
        """ """
        x = self._get_value_from_channel(device.channels[0])
        y = self._get_value_from_channel(device.channels[1])
        logger.debug(f'x: {x}, y: {y}')
        return np.array([x, y])


    def read(self):
        acc = self._read(self.acc_dev)
        return np.array(acc)

    def _get_value_from_channel(self, channel):
        raw_value = channel.attrs['raw'].value
        scale_value = channel.attrs['scale'].value
        return np.float64(raw_value) * np.float64(scale_value)


def rotate(config, accel):
    """Изменяем поворот экрана и матрицу координат"""
    x = accel[0]
    y = accel[1]

    touchscreen_id = config['touchscreen_id']

    if (-6.0 <= x <= 6.0) and (-9.0 <= y <= -0.5):
        subprocess.run(f'xrandr -o normal', shell=True)
        subprocess.run(f"xinput set-prop {touchscreen_id} 'Coordinate Transformation Matrix' 1 0 0 0 1 0 0 0 1", shell=True)
        logger.debug('normal')
    elif (5.0 <= x <= 10.0) and (-5.0 <= y <= -0.2):
        subprocess.run(f"xrandr -o left", shell=True)
        subprocess.run(f"xinput set-prop {touchscreen_id} 'Coordinate Transformation Matrix' 0 -1 1 1 0 0 0 0 1", shell=True)
        logger.debug('left')
    elif (-9.0 <= x <= -2.0) and (-7.0 <= y <= 6.0):
        subprocess.run(f"xrandr -o right", shell=True)
        subprocess.run(f"xinput set-prop {touchscreen_id} 'Coordinate Transformation Matrix' 0 1 0 -1 0 1 0 0 1", shell=True)
        logger.debug('right')
    elif (-6.0 <= x <= 6.0) and (2.0 <= y <= 10.0):
        subprocess.run(f"xrandr -o inverted", shell=True)
        subprocess.run(f"xinput set-prop {touchscreen_id} 'Coordinate Transformation Matrix' -1 0 1 0 -1 1 0 0 1", shell=True)
        logger.debug('inverted')

def main():
    """ Добавляем обработчики сигналов """
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)

    ctx = iio.LocalContext()
    arguments = Arguments()
    config = parse_config(arguments)

    reader = DataReader(ctx, config)

    """ Если пользователь указал файл логирования, то логируем в него """
    if arguments.log_file is not None:
        fh = logging.FileHandler(arguments.log_file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    while True:
        accel = reader.read()
        rotate(config, accel)
        time.sleep(1)

if __name__ == "__main__":
    main()

