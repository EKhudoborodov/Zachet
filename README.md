# Веб-приложение с нейросетью для детектирования черт лица с веб-камеры

# Установка приложения
## Запуск контейнера с проектом:
```bash
$ git clone https://github.com/EKhudoborodov/Zachet
$ cd Zachet
$ docker build . -t docker
$ docker run -p 0.0.0.0:8080:8080 -p 0.0.0.0:8081:8081 docker
```

# Использование веб-приложения
## Перейдите по ссылке http://127.0.0.1:8080/ .
<img src="https://github.com/EKhudoborodov/Zachet/blob/0c099c460a5e75bb393ed789f92f6322ab471154/photos/photo_2022-06-08_22-34-43.jpg">

## Проверьте что доступ к веб-камере разрешен в вашем браузере.
<img src="https://github.com/EKhudoborodov/Zachet/blob/0c099c460a5e75bb393ed789f92f6322ab471154/photos/photo_2022-06-08_22-34-57.jpg">

## Результат:
<img src="https://github.com/EKhudoborodov/Zachet/blob/0c099c460a5e75bb393ed789f92f6322ab471154/photos/photo_2022-06-08_22-35-02.jpg">
