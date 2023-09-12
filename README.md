## Установка Python 3.11
``` sudo apt-get install python 3.11 ```

## Запуск
```sh
git clone https://github.com/juliadod/rotate_display
cd rotate_display
pip install -r requirements.txt
python3 rotate_display.py
```

Чтобы запустить программу, необходимо правильно настроить конфигурационные файлы, которые находятся в каталоге `config`.

Пример готового конфигурационного файла (в формате JSON):

```json
{
  "accel": "accel_3d",
  "display": "eDP-1",
  "touchscreen_id": "13"
}
```
* `accel`: название акселерометра. Можно получить с помощью команды ```iio_info | grep accel```;
* `name_display`: название дисплея, который собираемся вращать. Можно узнать с помошью команды  ```xrandr ```;
* `touchscreen_id`: идентификатор тачскрина. Посмотреть можно с помощью команды ```xinput | grep "Wacom HID 484E Finger touch" | awk '{print $8}' | sed 's/id=//'```.
 
 
 

