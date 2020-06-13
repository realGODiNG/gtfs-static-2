<template>
    <div id="simple-map" :key="mainKey">
        Ooops! I should be a map!
        <br />
        (but I have a full api...)
    </div>
</template>

<script>
    /**
     * @typedef {Object} Position
     * @property {!Number} lat
     * @property {!Number} lon
     */

    export default {
        name: 'SimpleMap',

        data() {
            return {
                /** @type {!Number} */
                mainKey: 0,
                
                /** @type {!Number} */
                markedIndex: 0
            };
        },
        props: {
            'data': Array,
            'refreshParent': Function
        },

        methods: {  
            /**
             * @param {!Number} index
             * @param {!String} property
             * @returns {?String}
             */
            getProperty(index, property) {
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
                        return entry.isEnumeration()
                            ? entry.fieldType.enumeration.fromHTML(entry.get())
                            : entry.fieldType.structure.fromHTML(entry.get());
                    default:
                        return null;
                }
            },

            /**
             * @param {!Number} index
             * @returns {?Position}
             */
            getPosition(index) {
                return this.data[index] !== undefined
                    ? { lat: parseFloat(this.data[index]['stop_lat'].get()), lon: parseFloat(this.data[index]['stop_lon'].get()) }
                    : null;
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
                this.mainKey += 1;
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
