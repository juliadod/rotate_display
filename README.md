## Install Python 3.11
``` sudo apt-get install python 3.11 ```

## Запуск
```sh
git clone https://github.com/juliadod/rotate_display
cd rotate_display
pip install -r requirements.txt
python3 rotate_display.py
```

## json файл

"accel": "имя устройства"
посмотреть имя акселерометра:
```iio_info | grep accel```

 "name_display": "имя дисплея",
 посмотреть имя дистплея:
 ```xrandr ```
 
 "touchscreen_id": "id"
 посмотреть id Finger touch
 ``` xinput | grep "Wacom HID 484E Finger touch" | awk '{print $8}' | sed 's/id=//' ```
 
 
 
 

