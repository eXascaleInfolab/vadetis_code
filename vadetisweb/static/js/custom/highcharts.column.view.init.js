"use strict";

var VadetisColumnHighcharts = function () {

    var initHighcharts = function (html_id, url, is_spatial) {
        var dataset_series = [];
        var settings = settingsFromCookie();

        Highcharts.setOptions({
            global: {
                useUTC: true,
            }
        });

        // create the chart
        var highchart = new Highcharts.chart(html_id, {
            chart: {
                type: 'column',
                height: 650,
            },

            title: {
                text: null,
            },

            legend: {
                enabled: true,
                layout: 'horizontal',
            },
            xAxis: {
                categories: [
                    'Accuracy',
                    'F1-Score',
                    'Precision',
                    'Recall',
                ],
                crosshair: true
            },
            yAxis: {
                min: 0,
                max: 100,
                title: {
                    text: 'Score (in %)',
                }
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px"><strong>{point.key}</strong></span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.3f}</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.1,
                    borderWidth: 0
                }
            },
            series: []
        });

        // load chart
        initAlgorithmScores(highchart, url, is_spatial);
    };
    return {
        init: function (html_id, url, is_spatial) {
            initHighcharts(html_id, url, is_spatial);
        }
    };
}();