//Filename: main.js

define(["jquery", "underscore", "backbone", "jqueryui"], function($, _, Backbone) {


    var FilmLocation = Backbone.Model.extend({
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

            // Ensures that nulls are not passed
            var fields = [
                "actor_1", "actor_2", "actor_3",
                "production_company", "director", "writer"
            ];
            _.each(fields, function(field) {
                if (!this.get(field)) this.set(field, "");
            }.bind(this));   
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
            var entity_id = this.model.get("id");
            var infoWindow = this.model.get("infoWindow");
            infoWindow.setContent(content);

            // add view to the map
            marker.setMap(map);
            
            // register click event
            google.maps.event.addListener(marker, 'click', function() {
                // hide all open info windows and increase rank of the film
                parent.clickInfoHandler(entity_id);
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
        this.dataCollection = new FilmLocationCollection();
        this.createMap();
        // Init map with the most popular films
        this.loadFilmLocations("/api/locations/most_popular");
    }

    App.prototype.createMap = function() {
      var mapOptions = {
        center: new google.maps.LatLng(37.777, -122.444),
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
        _.each(films, function(film) {
            // Create Model
            var filmLocation = new FilmLocation(film);
            // Add to Collection
            this.dataCollection.add(filmLocation);
            // Create View
            var view = new FilmLocationView({
                model: filmLocation,
            }, this);
        }.bind(this));
    }

    App.prototype.clickInfoHandler = function(film_id) {
        _.each(this.dataCollection.toArray(), function(filmModel) {
            // hide detailed info for an open marker
            filmModel.get("infoWindow").close();
        });
        // increase rank of the clicked film
        this.increaseRank(film_id);
    }

    App.prototype.loadFilmLocations = function(url) {
        $.ajax(url)
        .done(function(data_json) {
            var films = $.parseJSON(data_json);
            this.updateData(films);
        }.bind(this))
        .fail(function() {
            this.handleFail("Failed to load films.");
        }.bind(this));
    }

    App.prototype.handleFail = function(message) {
        alert(message);
    }

    App.prototype.increaseRank = function(film_id) {
        console.log(film_id);
    }

    App.prototype.loadSearch = function(query) {
        var encoded_q = encodeURIComponent(query);
        // load search result
        this.loadFilmLocations("/api/locations/search/" + encoded_q);
    }

    $(function() {
        $(document).ready(function() {
            var app = new App();
            app.init();
            $( "#autocomplete" ).autocomplete({
                source: function( request, response ) {
                $.ajax("/api/locations/search/" + encodeURIComponent(request.term))
                    .done(function(data_json) {
                        var films = $.parseJSON(data_json);
                        // update map with the new films
                        app.updateData(films);
                        // show only to 6 suggestions in the autocomplete
                        items = [];
                        for (var i=0; i<Math.min(films.length, 6); i++) {
                            var item = {
                                label: films[i].title + '(' + films[i].release_year + '), ' + films[i].actor_1 + ', ' + films[i].director,
                                value: films[i]
                            }
                            items.push(item);
                        }
                        response(items);
                    }.bind(this))
                    .fail(function() {
                        app.handleFail("Failed to load films.");
                    }.bind(this));
                }.bind(this),
                minLength: 2,
                focus: function() {
                    // prevent value inserted on focus
                    return false;
                },
                select: function( event, ui ) {
                    event.preventDefault();
                    $("#autocomplete").val(ui.item.label);
                    app.updateData([ui.item.value]);
                }.bind(this)
            });
        });
    });
});