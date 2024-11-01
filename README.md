# Pyembroider
Телеграм-бот, создающий схему для вышивки по картинке

## Основной функционал

1) Получение схемы для вышивания из картинки формата jpg/png
2) Учет допустимых цветов и цветов, имеющихся у пользователя
3) Поиск выгодных предложений для покупки недостающих ниток на маркетплейсах
4) Подсчет количества необходимого материала (длина нитей)
5) Подсчет примерного размера картинки (optional)
*) TBD

## Способ работы

### Взаимодействие с ботом
  1) Составление базы данных доступных цветов ниток и их длины
  2) Загрузка картинки
  3) Указание размера канвы и уровня детализации (примерного кол-ва цветов)
  4) Указание коэффициента допустимости покупки новых ниток. В зависимости от него бот будет решать, какие цвета брать из имеющихся, а какие предлагать купить.
  5) Обработка картинки и получение схемы.
### Обработка картинки
  1) Разбиение картинки на квадратики нужного размера (в зависимости от детализации и канвы)
  2) Нахождение усредненного цвета для каждого квадратика
  3) Сопоставление цветов с базой данных DMC (Dollfus-Mieg et Compagnie) с учетом имеющихся и коэффициента допустимости покупок
  4) Нумерация цветов и создание схемы
  5) Подсчет длины ниток и запуск парсера цен для отсутствующих цветов
### Парсер цен
  1) В базе данных храним цены на нитки разных цветов на разных маркетплейсах (Ozon, Wildberries, Я.Маркет, Теплостановский рынок (очный парсер))
  2) Парсинг цен на нитки и предложение пользователю наиболее выгодных вариантов со ссылками.

## Роли
  1) Копнев Максим - парсер маркетплейсов и база данных DMC с ценами
  2) Сиволоцкий Алексей - телеграмм-бот + очный парсинг (с фотоотчетом) + проверка качества схем для вышивки (с фотоотчетом) + фотоотчет (с фотоотчетом)
  3) Дятлова Мария - обработка картинки и база данных имеющихся цветов

**Standartenführer:** Kopnev Maksim - @Oladiy2504
   
