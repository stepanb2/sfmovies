//Filename: main.js

define(["jquery", "underscore", "backbone", "jqueryui"], function($, _, Backbone) {


    var FilmLocation = Backbone.Model.extend({
        /*
            Sample json object used to init FilmLocation:
            {  
               "release_year":"1988",
               "title":"The Dead Pool",
               "writer":"Harry Julian Fink",
               "actor_1":"Clint Eastwood",
               "locations":"Hall of Justice (850 Bryant Street)",
               "actor_2":"Liam Neeson",
               "actor_3":"",
               "director":"Buddy Van Horn",
               "distributor":"Warner Bros. Pictures",
               "production_company":"Warner Bros. Pictures",
               "lat":37.775471,
               "lng":-122.4037169,
               "id":"6982b8fdb56fbe28fc1ebb9899131c37"
            }
        */
        initialize: function(){
            var myLatlng = new google.maps.LatLng(this.get("lat"), this.get("lng"));
            var marker = new google.maps.Marker({
                position: myLatlng,
                title: this.get("title")
            });
            this.set("marker", marker);
            var infoWindow = new google.maps.InfoWindow({
                maxWidth: 300
            });
            this.set("infoWindow", infoWindow);
        }
    });


    var FilmLocationView = Backbone.View.extend({
        initialize: function(model, parent){
            this.render(parent);
        },

        template: _.template($("#film_marker_template").html()),

        render: function(parent){
            var content = this.template(this.model.toJSON());
            var map = parent.map;
            var marker = this.model.get("marker");
            var infoWindow = this.model.get("infoWindow");
            infoWindow.setContent(content);

            // add view to the map
            marker.setMap(map);
            
            // register click event
            google.maps.event.addListener(marker, 'click', function() {
                // hide all open info windows
                parent.clickInfoHandler();
                // show detailed info
                infoWindow.open(map, marker);
            });
            return this;
        },

    });


    var FilmLocationCollection = Backbone.Collection.extend({
        model: FilmLocation
    });


    var App = function() {};

    App.prototype.init = function() {
        // Defines how many suggestions will shown in the auto complete
        this.rowsPerAutocomplete = 6;
        // Defines list of fields that are visible in the autocomplete
        this.autocompleteShownColumns = ["title", "actor_1", "director", "locations"];

        this.dataCollection = new FilmLocationCollection();
        // Create map and center it to the center of the SF
        this.createMap(37.777, -122.444);
        // Load film locations
        this.loadFilmLocations("/api/locations/explore");
    }

    App.prototype.createMap = function(lat, lng) {
      var mapOptions = {
        // Center to the San Francisco
        center: new google.maps.LatLng(lat, lng),
        // fixme: change the map zoom based on the markers coordinates
        zoom: 12,
      }
      // Instantiate map
      this.map = new google.maps.Map($("#map-canvas")[0], mapOptions);
    }

    App.prototype.cleanData = function() {
        _.each(this.dataCollection.toArray(), function(filmModel) {
            // remove markers from the map
            filmModel.get("marker").setMap(null);
        });
        this.dataCollection.reset();
    }

    App.prototype.updateData = function(films) {
        this.cleanData();
        var self = this;
        _.each(films, function(film) {
            // Create Model
            var filmLocation = new FilmLocation(film);
            // Add to Collection
            self.dataCollection.add(filmLocation);
            // Create View
            var view = new FilmLocationView({
                model: filmLocation,
            }, self);
        });
    }

    App.prototype.clickInfoHandler = function(film_id) {
        _.each(this.dataCollection.toArray(), function(filmModel) {
            // hide detailed info for an open marker
            filmModel.get("infoWindow").close();
        });
    }

    App.prototype.loadFilmLocations = function(url) {
        var self = this;
        $.getJSON(url).done(function(data) {
            self.updateData(data);
        }).fail(function() {
            self.handleFail("Failed to load films.");
        });
    }

    App.prototype.handleFail = function(message) {
        // fixme: show the error in the modal window instead
        alert(message);
    }

    App.prototype.formatFilm = function(film) {
        // fixme: highlight the actual matched parts
        return _.map(this.autocompleteShownColumns, function(name){ return film[name]}).join(', ');
    }

    $(function() {
        $(document).ready(function() {
            var app = new App();
            app.init();
            $( "#autocomplete" ).autocomplete({
                source: function( request, response ) {
                    $.getJSON("/api/locations/search/", {q: request.term} ).done(function(films) {
                        // update map with the new films
                        app.updateData(films);
                        // show only to limited number of suggestions in the autocomplete
                        items = _.map(_.take(films, app.rowsPerAutocomplete), function(film) {
                            return { label: app.formatFilm(film), value: film }
                        });
                        response(items);
                    }).fail(function() {
                        app.handleFail("Failed to load films.");
                    });
                },
                minLength: 2,
                focus: function() {
                    // prevent value inserted on focus
                    return false;
                },
                select: function(event, ui) {
                    event.preventDefault();
                    $("#autocomplete").val(ui.item.label);
                    app.updateData([ui.item.value]);
                }
            });
        });
    });
});