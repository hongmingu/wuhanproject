$(function () {
// Create map instance
    var chart = am4core.create("chartdiv1", am4maps.MapChart);
// Disable zoom and pan
    chart.maxZoomLevel = 1;
    chart.seriesContainer.draggable = false;
    chart.seriesContainer.resizable = false;
// Set map definition
    chart.geodata = am4geodata_worldLow;

// Set projection
    chart.projection = new am4maps.projections.Miller();

// Create map polygon series
    var polygonSeries = chart.series.push(new am4maps.MapPolygonSeries());

// Make map load polygon (like country names) data from GeoJSON
    polygonSeries.useGeodata = true;

// Configure series
    var polygonTemplate = polygonSeries.mapPolygons.template;
    polygonTemplate.tooltipText = "{name} \n infected people:{value.value.formatNumber('#')}";
    polygonTemplate.fillOpacity = 0.6;

// Create hover state and set alternative fill color
    var hs = polygonTemplate.states.create("hover");

    hs.properties.fillOpacity = 0.9;

// Remove Antarctica
    polygonSeries.exclude = ["AQ"];

// Bind "fill" property to "fill" key in data
    polygonTemplate.propertyFields.fill = "fill";
    polygonTemplate.propertyFields.fill = "fill1";
    hs.propertyFields.fill = "fill1";

    /* Create a heat rule */
    polygonSeries.heatRules.push({
        property: "fill",
        target: polygonSeries.mapPolygons.template,
        min: am4core.color("#30bfea"),
        max: am4core.color("#71ff42")
    });


    /* Create a heat legend */
// add heat legend
    var heatLegend = chart.chartContainer.createChild(am4maps.HeatLegend);
    heatLegend.valign = "bottom";
    heatLegend.align = "left";
    heatLegend.width = am4core.percent(25);
    heatLegend.series = polygonSeries;
    heatLegend.orientation = "vertical";
    heatLegend.padding(30, 30, 30, 30);
    heatLegend.valueAxis.renderer.labels.template.fontSize = 10;
    heatLegend.valueAxis.renderer.minGridDistance = 40;
    heatLegend.minValue = 0;
    heatLegend.maxValue = 12000;


// Add some data
    polygonSeries.data = [{
        "id": "US",
        "name": "United States",
        "value": 200,

    }, {
        "id": "FR",
        "name": "France",
        "value": 11000,

    }, {
        "id": "CN",
        "name": "China",
        "value": 11791,

    }, {
        "id": "TH",
        "name": "Thailand",
        "value": 19,

    }
        , {
            "id": "MY",
            "name": "Malaysia",
            "value": 16,

        }
        , {
            "id": "JP",
            "name": "Jpan",
            "value": 15,

        }
        , {
            "id": "HK",
            "name": "Hongkong",
            "value": 13,

        }
        , {
            "id": "KR",
            "name": "Korea",
            "value": 12,

        }
        , {
            "id": "TW",
            "name": "Republic of China",
            "value": 10,

        }, {
            "id": "AU",
            "name": "Austraila",
            "value": 9,

        }, {
            "id": "MO",
            "name": "Makao",
            "value": 7,

        }, {
            "id": "DE",
            "name": "Germany",
            "value": 5,

        }, {
            "id": "VN",
            "name": "Vietnam",
            "value": 5,

        }, {
            "id": "AE",
            "name": "Arabemirates",
            "value": 10,

        }, {
            "id": "CA",
            "name": "Canada",
            "value": 3,

        }, {
            "id": "NP",
            "name": "Nepal",
            "value": 2,

        }, {
            "id": "GB",
            "name": "England",
            "value": 2,

        }, {
            "id": "IT",
            "name": "Italia",
            "value": 2,

        }, {
            "id": "RU",
            "name": "Russia",
            "value": 2,

        }, {
            "id": "KH",
            "name": "Cambodia",
            "value": 1,

        }, {
            "id": "LK",
            "name": "Srilanka",
            "value": 1,

        }, {
            "id": "FI",
            "name": "Finland",
            "value": 1,

        }, {
            "id": "PH",
            "name": "Philippines",
            "value": 1,

        }, {
            "id": "IN",
            "name": "Republic of India",
            "value": 1,

        }, {
            "id": "SE",
            "name": "Sweden",
            "value": 1,

        }, {
            "id": "ES",
            "name": "Spain",
            "value": 1,

        }];

})
