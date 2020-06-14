<template>
    <div id="simple-stop" class="popup">
        <div id="simple-stop-content" class="popup-content" role="dialog">
            <header id="simple-stop-header">
                <slot name="header">
                    <b-navbar toggleable="lg" type="dark" variant="dark">
                        <b-navbar-brand>
                            Select Stop
                        </b-navbar-brand>
                    </b-navbar>
                </slot>
            </header>
            <section id="simple-stop-body">
                <slot name="body">
                    <b-card :key="mainKey">
                        <SimpleTree :fields="fields" :handler="handler" :root="trees[0]" :trees="trees.slice(1)" v-if="trees.length != 0" />
                    </b-card>
                </slot>
            </section>
            <footer id="simple-stop-footer" class="centered">
                <slot name="footer">
                    <b-button class="m-1" size="sm" type="button" variant="dark" @click="handler('select', null)">
                        Clear
                    </b-button>
                    <b-button class="m-1" size="sm" type="button" variant="dark" @click="close()">
                        Cancel
                    </b-button>
                </slot>
            </footer>
        </div>
    </div>
</template>

<script>
    import SimpleTree from './SimpleTree'

    export default {
        name: 'SimpleStop',
        components: {
            SimpleTree
        },
        
        data() {
            return {
                /** @type {!Array.<!String>} */
                fields: [ 'stop_id', 'stop_name', 'location_type', 'platform_code' ],

                /** @type {!Number} */
                mainKey: 0
            }
        },
        props: {
            'entry': Object,
            'setter': Function,
            'trees': Array
        },

        methods: {
            close() {
                this.$emit('close');
            },

            /**
             * @param {!String} type
             * @param {?Object} object
             * @returns {?Object|undefined}
             */
            handler(type, object) {
                switch (type) {
                    case 'refresh':
                        this.mainKey += 1;
                        return;
                    case 'select':
                        this.setter(this.entry, object !== null ? object['stop_id'] : null);
                        return this.close();
                    default:
                        return;
                }
            }
        }
    };
</script>
