#!/usr/bin/env python
import time

import iio
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation
from collections import deque
import argparse
import numpy as np
from ahrs.filters import Madgwick

import quatlib

import json
import subprocess


def parse_config(arguments):
    f = open(arguments.config, 'r', encoding='utf-8')
    json_conf = json.load(f)
    return json_conf

class Arguments:
    """Class for parsing the input arguments."""

    def __init__(self):
        """Arguments class constructor."""
        self.parser = argparse.ArgumentParser(description="iio_readdev")
        self._add_parser_arguments()
        args = self.parser.parse_args()
        self.config = str(args.config)

    def _add_parser_arguments(self):

        self.parser.add_argument(
            "-c",
            "--config",
            type=str,
            help="Scan for available contexts and if only one is available use it.",
        )


class DataReader:
    """Class for reading samples from the device."""

    def __init__(self, ctx, config):
        self.ctx = ctx
        self.config = config

        self._devices()
        self._activate_channels(self.acc_dev)
        # self._activate_channels(self.gyr_dev)
        # self._activate_channels(self.mag_dev)

    def _devices(self):
        self.acc_dev = self.ctx.find_device(self.config['accel'])
        # self.gyr_dev = self.ctx.find_device(self.config['gyro'])
        # self.mag_dev = self.ctx.find_device(self.config['magn'])
        if (self.acc_dev is None):
            raise Exception("Devices not found!")
        return self

    def _activate_channels(self, device):
        for channel in device.channels:
            channel.enabled = True
        return self

    def _read(self, device):
        x = self._get_value_from_channel(device.channels[0])
        y = self._get_value_from_channel(device.channels[1])
        z = self._get_value_from_channel(device.channels[2])
        # print('x:', x, 'y:', y, 'z:', z)
        return np.array([x, y])

    # def _calibrate(self):
    #     num_samples = 100
    #     acc_avr = np.array([0., 0., 0.])
    #     gyr_avr = np.array([0., 0., 0.])
    #     mag_avr = np.array([0., 0., 0.])
    #     for i in range(num_samples):
    #         acc, gyr, mag = self.read()
    #         acc_avr += acc
    #         gyr_avr += gyr
    #         mag_avr += mag
    #     self.normalizer = np.array([acc_avr / num_samples, gyr_avr / num_samples, mag_avr / num_samples])
    #     print(self.normalizer)

    def read(self):
        acc = self._read(self.acc_dev)
        # gyr = self._read(self.gyr_dev)
        # mag = self._read(self.mag_dev)
        # return np.array([acc])
        return np.array(acc)

    def _get_value_from_channel(self, channel):
        raw_value = channel.attrs['raw'].value
        scale_value = channel.attrs['scale'].value
        return np.float64(raw_value) * np.float64(scale_value)

    # def _get_timestamp(self):
    #     now = datetime.now()
    #     current_time = now.strftime("%D %H:%M:%S")
    #     return current_time

def rotate(config, accel):
    x = accel[0]
    y = accel[1]
    touchpad_id = config['touchpad_id']

    if (-6.0 <= x <= 6.0) and (-9.0 <= y <= -0.5):
        subprocess.run(f'xrandr -o normal', shell=True)
        subprocess.run(f"xinput set-prop {touchpad_id} 'Coordinate Transformation Matrix' 1 0 0 0 1 0 0 0 1", shell=True)
    elif (5.0 <= x <= 10.0) and (-5.0 <= y <= -0.2):
        subprocess.run(f"xrandr -o left", shell=True)
        subprocess.run(f"xinput set-prop {touchpad_id} 'Coordinate Transformation Matrix' 0 -1 1 1 0 0 0 0 1", shell=True)
    elif (-9.0 <= x <= -2.0) and (-7.0 <= y <= 6.0):
        subprocess.run(f"xrandr -o right", shell=True)
        subprocess.run(f"xinput set-prop {touchpad_id} 'Coordinate Transformation Matrix' 0 1 0 -1 0 1 0 0 1", shell=True)
    elif (-6.0 <= x <= 6.0) and (2.0 <= y <= 10.0):
        subprocess.run(f"xrandr -o inverted", shell=True)
        subprocess.run(f"xinput set-prop {touchpad_id} 'Coordinate Transformation Matrix' -1 0 1 0 -1 1 0 0 1", shell=True)


# def view(plt, name, times, x, y, z):
#     plt.clf()
#     plt.plot(times, x, label=f'{name} X')
#     plt.plot(times, y, label=f'{name} Y')
#     plt.plot(times, z, label=f'{name} Z')
#     plt.xlabel('Sample Index')
#     plt.ylabel(f'{name} value')
#     plt.legend()
#     plt.pause(0.1)
    
def main():
    """Module's main method."""
    ctx = iio.LocalContext()
    arguments = Arguments()
    config = parse_config(arguments)

    reader = DataReader(ctx, config)


    # mf = Madgwick(gain=0.041)
    # prev = np.tile([1., 0., 0., 0.], 1)  # Allocate for quaternions
    #
    # gyro_history = deque(maxlen=22)
    # timestamps   = deque(maxlen=22)
    # index = 0

    while True:
        # indexdex = index + 1
        # acc = reader.read()
        # cur = mf.updateMARG(prev, gyr=gyr)
        # rot = Rotation.from_quat(cur)
        # angles = rot.as_euler('xyz', degrees=True)
        accel = reader.read()
        rotate(config, accel)


        # gyro_history.append(angles)
        # timestamps.append(index)

        # Рисуем график значений гироскопа
        #
        # if (len(gyro_history) > 10):
        #     timestamps.popleft()
        #     gyro_history.popleft()
        #
        # view(plt, 'Эйлеровский угол по оси', timestamps,
        #      [item[0] for item in gyro_history],
        #      [item[1] for item in gyro_history],
        #      [item[2] for item in gyro_history])
        #
        # # print(angles)
        #
        time.sleep(1)
        # prev = cur.copy()

if __name__ == "__main__":
    main()