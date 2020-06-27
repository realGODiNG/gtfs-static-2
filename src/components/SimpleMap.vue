<template>
    <fragment>
        <div id="simple-map" />
        <div v-for="(record, index) in data" :key="'marker-' + index" :id="'marker-' + index">
            <b-icon icon="geo-alt" :variant="getVariant(index)"
                :class="(isSelected(record) ? 'h2' : 'h4') + ' mb-2'"
                v-b-tooltip.hover="{ placement: 'top', title: getDisplayText(index) }"
                @click="select(record)"
                v-if="isShown(index)"
            />
        </div>
    </fragment>
</template>

<script>
    import mapboxgl from 'mapbox-gl'
    import 'mapbox-gl/dist/mapbox-gl.css'

    /**
     * @typedef {Object} Position
     * @property {!Number} lat
     * @property {!Number} lon
     */

    export default {
        name: 'SimpleMap',

        data() {
            return {
                /** @type {!Object} */
                map: null,

                /** @type {!Array.<?Object>} */
                markers: new Array()
            };
        },
        mounted() {
            const center = this.getPosition(0);
            // eslint-disable-next-line
            this.map = new mapboxgl.Map({
                container: 'simple-map',
                style: {
                    "version": 8,
                    "sources": {
                        "simple-tiles": {
                            "type": "raster",
                            "tiles": [
                                "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
                                "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            ],
                            "tileSize": 256
                        }
                    },
                    "layers": [ {
                        "id": "simple-tiles",
                        "type": "raster",
                        "source": "simple-tiles",
                        "minzoom": 0,
                        "maxzoom": 22
                    } ],
                    "customAttribution": '<a href="https://www.openstreetmap.org/">© OpenStreetMap contributors</a>'
                },
                center: this.first !== null ? [ this.first.lon, this.first.lat ] : [ center.lon, center.lat ],
                zoom: this.first !== null ? this.first.zoom : this.data[0]['stop_lat'].isEmpty() || this.data[0]['stop_lon'].isEmpty() ? 4 : 16
            });
            this.markers.length = 0;
            for (var index = 0; index < this.data.length; index++) {
                const position = this.getPosition(index);
                this.markers.push(
                    new mapboxgl.Marker(document.getElementById('marker-' + index)).setLngLat([ position.lon, position.lat ]).addTo(this.map)
                );
            }
            this.map.on('contextmenu', event => {
                if (event.originalEvent.ctrlKey) {
                    var index = 0;
                    for (; index < this.data.length; index++) {
                        if (this.isSelected(this.data[index])) {
                            break;
                        }
                    }
                    this.setPosition(index, { lat: event.lngLat.lat, lon: event.lngLat.lng })
                }
            });
            this.map.on('move', () => this.$emit('moved', {
                lat: this.map.transform._center.lat,
                lon: this.map.transform._center.lng,
                zoom: this.map.transform._zoom 
            }));
        },
        props: {
            'data': Array,
            'isSelected': Function,
            'refreshParent': Function,
            'select': Function,
            'first': Object
        },

        methods: {
            /**
             * @param {!Number} index
             * @returns {!Boolean}
             */
            isShown(index) {
                const stop = this.data[index];
                return stop !== undefined && !stop['stop_lat'].isEmpty() && !stop['stop_lon'].isEmpty();
            },

            /**
             * @param {!Number} index
             * @returns {!String}
             */
            getDisplayText(index) {
                const stop = this.data[index];
                if (stop === undefined) {
                    return '';
                }
                return '(' + stop['stop_id'].get() + ') ' + stop['stop_name'].get()
                    + (!stop['platform_code'].isEmpty() ? ' - ' + stop['platform_code'].get() : '');
            },
            /**
             * @param {!Number} index
             * @param {!String} property
             * @param {!Boolean} willBeNativeGTFSValue
             * @returns {?String}
             */
            getProperty(index, property, willBeNativeGTFSValue) {
                if (this.data[index] === undefined) {
                    return null;
                }
                const entry = this.data[index][property];
                switch (property) {
                    case 'stop_id':
                        // fallsthrough
                    case 'stop_code':
                        // fallsthrough
                    case 'stop_name':
                        // fallsthrough
                    case 'stop_desc':
                       // fallsthrough
                    case 'stop_lat':
                        // fallsthrough
                    case 'stop_lon':
                        // fallsthrough
                    case 'zone_id':
                        // fallsthrough
                    case 'stop_url':
                        // fallsthrough
                    case 'location_type':
                        // fallsthrough
                    case 'parent_station':
                        // fallsthrough
                    case 'stop_timezone':
                        // fallsthrough
                    case 'wheelchair_boarding':
                        // fallsthrough
                    case 'level_id':
                        // fallsthrough
                    case 'platform_code':
                        if (!willBeNativeGTFSValue) {
                            return entry.get();
                        }
                        return entry.isEnumeration()
                            ? entry.fieldType.enumeration.fromHTML(entry.get())
                            : entry.fieldType.structure.fromHTML(entry.get());
                    default:
                        return null;
                }
            },
            /**
             * @param {!Number} index
             * @returns {!Position}
             */
            getPosition(index) {
                const stop = this.data[index];
                return stop !== undefined && !stop['stop_lat'].isEmpty() && !stop['stop_lon'].isEmpty()
                    ? { lat: parseFloat(stop['stop_lat'].get()), lon: parseFloat(stop['stop_lon'].get()) }
                    : { lat: 50.6418783, lon: 10.3618556 };
            },
            /**
             * @param {!Number} index
             * @returns {!String}
             */
            getVariant(index) {
                switch (this.getProperty(index, 'location_type', true)) {
                    case '0':
                        return 'danger';
                    case '1':
                        return 'primary';
                    case '2':
                        return 'success ';
                    case '3':
                        return 'warning';
                    case '4':
                        return 'light';
                    default:
                        return 'dark';  
                }
            },

            /**
             * @param {!Number} index
             * @param {!Position} position
             * @returns {!Boolean}
             */
            setPosition(index, position) {
                if (this.data[index] === undefined) {
                    return false;
                }
                this.data[index]['stop_lat'].set(position.lat.toString());
                this.data[index]['stop_lon'].set(position.lon.toString());
                if (this.markers[index] !== null) {
                    this.markers[index].setLngLat([ position.lon, position.lat ]);
                }
                return true;
            }
        }
    };
</script>

<style scoped>
    #simple-map {
        bottom: 0;
        left: 0;
        position: absolute;
        right: 0;
        text-align: center;
        top: 0;
    }
</style>
