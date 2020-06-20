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
                                <b-form-input class="m-1" v-model="filterWrapper" placeholder="Filter" size="sm" />
                                <b-icon class="m-1" icon="trash" @click="applyFilter(true)" :variant="filter.length != 0 ? 'light' : 'dark'" />
                                <b-icon class="m-1" icon="search" @click="applyFilter()" variant="light" />
                            </b-nav-form>
                        </b-navbar-nav>
                    </b-navbar>
                </slot>
            </header>
            <section id="simple-stop-body">
                <slot name="body">
                    <b-card :key="mainKey">
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
            'trees': Array
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
            }
        }
    };
</script>
