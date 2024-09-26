var dataSet = anychart.data.set(getData());

var firstSeriesData = dataSet.mapAs({ x: 0, value: 1 });
var secondSeriesData = dataSet.mapAs({ x: 0, value: 2 });
var thirdSeriesData = dataSet.mapAs({ x: 0, value: 3 });
var fourthSeriesData = dataSet.mapAs({ x: 0, value: 4 });

var chart = anychart.line();
chart.animation(true);
chart.title('Регистрация пользователей и загрузка файлов');
chart.crosshair().enabled(true).yLabel(false).yStroke(null);

var firstSeries = chart.line(firstSeriesData);
firstSeries
.name('Пользователей зарегистрировано')
.stroke('3 #f49595')
.tooltip()
.format("Пользователей зарегистрировано: {%value}");

var secondSeries = chart.line(secondSeriesData);
secondSeries
.name('Всего пользователей')
.stroke('3 #f9eb97')
.tooltip()
.format("Всего пользователей: {%value}");

var thirdSeries = chart.line(thirdSeriesData);
thirdSeries
.name('Файлов получено')
.stroke('3 #a8d9f6')
.tooltip()
.format("Файлов получено: {%value}");

var fourthSeries = chart.line(fourthSeriesData);
fourthSeries
.name('Всего файлов')
.stroke('3 #e2bbfd')
.tooltip()
.format("Всего файлов: {%value}");

chart.legend().enabled(true);
chart.container('container');
chart.draw();

function getData() {
  var myData = JSON.parse(document.getElementById('data').textContent);
  return myData;
}