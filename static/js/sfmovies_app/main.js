//Filename: main.js

define(["jquery", "underscore", "backbone"], function($, _, Backbone) {
    // Sample Data

    var App = {};
    App.init = function() {
        this.initAutoComplete();
        this.createMap();
    }

    App.initAutoComplete = function() {
        // Init the map with the most popular film locations
        this.loadFilmLocations("/api/locations/most_popular", this.updateAutoCompleteList, this.handleFail);
    }

    App.createMap = function() {
      var mapOptions = {
        center: new google.maps.LatLng(37.777, -122.444),
        zoom: 13,
      }
      // Instantiate map
      this.map = new google.maps.Map($("#map-canvas")[0], mapOptions);
    }

    App.updateAutoCompleteList = function(locations) {
        console.log(typeof locations);
        console.log(locations);
    }


    App.loadFilmLocations = function(url, success_handler, fail_handler) {
        console.log(url);
        $.ajax(url)
        .done(function(data_json) {
            var locations = $.parseJSON(data_json);
            success_handler(locations);
        })
        .fail(function() {
            fail_handler();
        });
    }

    App.handleFail = function() {
        alert("Error");
    }

    $(function() {
        $(document).ready(function() {
            App.init();
        });
    });
});