# gtfs-static
created as part of "Praktikum Algorithmen" (TU Darmstadt, summer semester 2020)

## Notes
```
* All data will be reset on page reloading.
  So do not reload, if you don't want to reset everything - or just save your changes before.

* All realtime data will be reset after creating or loading a static dataset.
  So you have to save all changes before doing this over the menu, if you want to.

* The file 'public/gtfs-static.xml' will only be used to generate gtfs structures, when serving the project.
  In production mode a constant string created from it will be used instead - because of same-origin-policy.
  Keep that in mind, when changing this file. (see mounted function in 'src/App.vue' for more information)
  Solving the SOP problem, allows you to delete this string and always use the human readable file instead.
  
* Any trip update in a loaded realtime feed should have a non-empty start day inside the trip descriptor.
  Trip updates created by this app will always have this value - which is needed to compute times for the ui.
```

## NPM dependencies
```
npm install jquery
npm install vue bootstrap-vue bootstrap
npm install gtfs-realtime-bindings
npm install --save vue-fragment
npm install --save v-calendar@next
npm install --save jszip
npm install --save file-saver
npm install --save mapbox-gl
```

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```


## Links
* ![GTFS Static](https://developers.google.com/transit/gtfs)
* ![GTFS Realtime](https://developers.google.com/transit/gtfs-realtime)

### NPM
* ![jQuery](https://github.com/jquery/jquery)
* ![Vue](https://github.com/vuejs/vue)
* ![BootstrapVue](https://github.com/bootstrap-vue/bootstrap-vue)
* ![Bootstrap](https://github.com/twbs/bootstrap)
* ![vue-fragment](https://github.com/Thunberg087/vue-fragment)
* ![V-Calendar](https://github.com/nathanreyes/v-calendar)
* ![JSZip](https://github.com/Stuk/jszip)
* ![FileSaver](https://github.com/eligrey/FileSaver.js)
* ![gtfs-realtime-bindings](https://github.com/MobilityData/gtfs-realtime-bindings)
* ![Mapbox GL JS](https://github.com/mapbox/mapbox-gl-js)


## Screenshots

### User interface: station
![Screenshot](/screenshots/station.png?raw=true)

### User interface: trip
![Screenshot](/screenshots/trip.png?raw=true)

### User interface: entry picker
![Screenshot](/screenshots/picker.png?raw=true)

### User interface: trip update
![Screenshot](/screenshots/realtime.png?raw=true)

### User interface: full file table
![Screenshot](/screenshots/file.png?raw=true)
