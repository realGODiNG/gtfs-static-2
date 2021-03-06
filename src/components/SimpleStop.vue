<template>
    <div id="simple-stop" class="popup">
        <div id="simple-stop-content" class="popup-content" role="dialog">
            <header id="simple-stop-header">
                <slot name="header">
                    <b-navbar toggleable="lg" type="dark" variant="dark">
                        <b-navbar-brand>
                            Select '{{ entry.field.name }}'
                        </b-navbar-brand>
                        <b-navbar-nav class="ml-auto">
                            <b-nav-form>
                                <form @submit.prevent>
                                    <b-form-input class="m-1" v-model="filterWrapper" placeholder="Filter" size="sm" @keyup.enter="applyFilter()" />
                                </form>
                                <b-icon class="m-1" icon="trash" @click="applyFilter(true)" variant="light"
                                    v-b-tooltip.hover="{ placement: 'top', title: 'Clear filter.' }"
                                    v-if="filter.length != 0"
                                />
                                <b-icon class="m-1" icon="blank" v-else />
                                <b-icon class="m-1" icon="search" @click="applyFilter()" variant="light"
                                    v-b-tooltip.hover="{ placement: 'top', title: 'Apply filter.' }"
                                />
                            </b-nav-form>
                        </b-navbar-nav>
                        <b-navbar-nav class="ml-auto">
                            <b-nav-form>
                                <b-icon class="h3 m-1" icon="x-circle-fill" @click="close()" variant="danger" />
                            </b-nav-form>
                        </b-navbar-nav>
                    </b-navbar>
                </slot>
            </header>
            <section id="simple-stop-body">
                <slot name="body">
                    <b-card :key="mainKey" :style="{ 'min-width': '1000px' }">
                        <SimpleTree :fields="fields" :handler="handler"
                            :root="filteredTrees[0]"
                            :trees="filteredTrees.slice(1)"
                            v-if="filteredTrees.length != 0"
                        />
                    </b-card>
                </slot>
            </section>
            <footer id="simple-stop-footer" class="centered">
                <slot name="footer">
                    <b-card>
                        <b-button class="m-1" type="button" variant="dark" @click="handler('select', null)">
                            Clear
                        </b-button>
                        <b-button class="m-1" type="button" variant="dark" @click="close()">
                            Cancel
                        </b-button>
                    </b-card>
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
                mainKey: 0,

                /** @type {!String} */
                filterWrapper: '',

                /** @type {!String} */
                filter: ''
            }
        },
        props: {
            'entry': Object,
            'setter': Function,
            'trees': Array,
            'preFilter': String
        },

        mounted() {
            if (typeof this.preFilter === 'string') {
                this.filterWrapper = this.preFilter;
                this.applyFilter();
            }
        },

        methods: {
            /**
             * @param {!Boolean|undefined} reset
             */
            applyFilter(reset) {
                if (reset !== undefined ? reset : false) {
                    this.filterWrapper = '';
                }
                this.filter = this.filterWrapper;
                this.mainKey += 1;
            },

            /**
             * @param {!Boolean|undefined} needsUpdate
             */
            close(needsUpdate) {
                this.$emit('close', needsUpdate !== undefined ? needsUpdate : false);
            },

            /**
             * @param {!String} type
             * @param {?Object} object
             * @returns {?Object|undefined}
             */
            handler(type, object) {
                switch (type) {
                    case 'legal':
                        return !this.illegalStopIDs.includes(object['stop_id'].get());
                    case 'refresh':
                        this.mainKey += 1;
                        return;
                    case 'select':
                        this.setter(this.entry, object !== null ? object['stop_id'] : null);
                        return this.close(this.entry.field.getFullIdentifier() === 'stops.parent_station');
                    default:
                        return;
                }
            }
        },

        computed: {
            /**
             * @returns {!Array.<!Tree>}
             */
            filteredTrees() {
                if (this.filter.length == 0) {
                    return this.trees;
                }
                return this.trees.filter(tree => {
                    for (var index = 0; index < this.fields.length; index++) {
                        if (tree.includes(this.fields[index], this.filter)) {
                            return true;
                        }
                    }
                    return false;
                });
            },
            /**
             * @returns {!Array.<!String>}
             */
            illegalStopIDs() {
                if (this.entry.field.getFullIdentifier() !== 'stops.parent_station') {
                    return new Array();
                }
                const getStops = (stop, data) => {
                    if (stop === undefined) {
                        stop = this.entry.record;
                        data = new Array();
                    }
                    data.push(stop);
                    stop['stop_id'].children.forEach(child => {
                        if (child.field.file.identifier === 'stops') {
                            data = getStops(child.record, data);
                        }  
                    });
                    return data;
                };
                return getStops().map(stop => stop['stop_id'].get());
            }
        }
    };
</script>
