# gtfs-static

## Information
```
* All data will be reset on page reloading.
  So do not reload, if you don't want to reset everything.

* All realtime data will be reset after creating or loading a static dataset.
  So you have to save all changes before doing this over the menu, if you want to.

* The file 'public/gtfs-static.xml' will only be used to generate gtfs structures, when serving the project.
  In production mode a constant string created from it will be used instead - because of same-origin-policy.
  Keep that in mind, when changing this file. (see mounted function in 'src/App.vue' for more information)
```

## Project setup
```
npm install jquery
npm install vue bootstrap-vue bootstrap
npm install gtfs-realtime-bindings
npm install --save vue-fragment
npm install --save v-calendar@next
npm install --save jszip
npm install --save file-saver
npm install --save mapbox-gl
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

## Screenshots

### User Interface: Station
![Screenshot](/screenshots/station.png?raw=true)

### User Interface: Trip
![Screenshot](/screenshots/trip.png?raw=true)

### User Interface: Entry Picker
![Screenshot](/screenshots/picker.png?raw=true)

### User Interface: Trip Update
![Screenshot](/screenshots/realtime.png?raw=true)

### User Interface: Full File Table
![Screenshot](/screenshots/file.png?raw=true)
