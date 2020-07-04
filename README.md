# gtfs-static

## Information
```
* All data will be reset on page reloading - so do not reload, if you don't want to reset everything.

* All realtime data will be reset after creating or loading a static dataset - so you have to save all changes before doing this over the menu, if you want to.

* The file 'public/gtfs-static.xml' will only be used to generate gtfs structures, when serving the project. In production mode a constant string created from this file will be used instead - because of same-origin-policy. Keep that in mind, when changing this file. (see mounted function in 'src/App.vue' for more information)
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

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
