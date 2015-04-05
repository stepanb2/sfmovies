requirejs.config({
    baseUrl: "js/lib",
    shim: {
        underscore: {
          exports: '_'
        },
        backbone: {
          deps: ["underscore", "jquery"],
          exports: "Backbone"
        }
    },
    paths: {
      app: "../sfmovies_app",
      jquery: "https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min",
      underscore: "https://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.8.2/underscore-min",
      backbone: "https://cdnjs.cloudflare.com/ajax/libs/backbone.js/1.1.2/backbone-min",
      jqueryui:  "https://code.jquery.com/ui/1.11.3/jquery-ui.min",
    }
});

// Load the main app module to start the app
requirejs(["app/main"]);