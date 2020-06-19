<template>
    <div id="simple-picker" class="popup">
        <div id="simple-picker-content" class="popup-content" role="dialog">
            <header id="simple-picker-header">
                <slot name="header">
                    <b-navbar toggleable="lg" type="dark" variant="dark">
                        <b-navbar-brand>
                            Select '{{ this.entry.field.name }}'
                        </b-navbar-brand>
                        <b-navbar-nav class="ml-auto">
                            <b-nav-form>
                                <b-form-input class="m-1" v-model="filterWrapper" placeholder="Filter" size="sm" />
                                <b-icon class="m-1" icon="trash" @click="applyFilter(true)" :variant="filter.length != 0 ? 'light' : 'dark'" />
                                <b-button class="m-1" @click="applyFilter()" variant="light" size="sm">
                                    Apply
                                </b-button>
                            </b-nav-form>
                        </b-navbar-nav>
                    </b-navbar>
                </slot>
            </header>
            <section id="simple-picker-body">
                <slot name="body">
                    <b-card :key="mainKey">
                        <b-table :fields="getFields()" :items="getRecords()" hover small striped >
                            <template v-slot:head()="data">
                                {{ formator(data.column) }}
                            </template>
                            <template v-slot:cell()="data">
                                <span class="centered" v-if="data.value.record === undefined">
                                    <b-icon class="m-1" icon="check" @click="handler('select', data.item)" />
                                </span>
                                <fragment v-else-if="data.value.record.__isEqual(entry.data !== null ? entry.data.record : null)">
                                    <b>
                                        {{ data.value.get() }}
                                    </b>
                                </fragment>
                                <fragment v-else>
                                    {{ data.value.get() }}
                                </fragment>
                            </template>
                        </b-table>
                    </b-card>
                </slot>
            </section>
            <footer id="simple-picker-footer" class="centered">
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
    export default {
        name: 'SimplePicker',
        
        data() {
            return {
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
            'setter': Function
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
             * @param {!String} text
             * @returns {!String}
             */
            formator(text) {
                const words = text.split('_').map(word => word.length != 0 ? word[0].toUpperCase() + word.slice(1) : '');
                return words.join(' ').trim();
            },

            /**
             * @param {!Boolean|undefined} needsUpdate
             */
            close(needsUpdate) {
                this.$emit('close', needsUpdate !== undefined ? needsUpdate : false);
            },

            /** @returns {!Array.<!String>} */
            getFields() {
                switch (this.entry.field.getFullIdentifier()) {
                    case 'trips.route_id':
                        return [ 'route_id', 'route_short_name', 'route_long_name', '__select' ];
                    case 'stops.level_id':
                        return [ 'level_id', 'level_index', 'level_name', '__select' ];
                    default:
                        return new Array();
                }
            },
            /** @returns {!Array.<!Record>} */
            getRecords() {
                const records = this.entry.fieldType.parent !== null ? this.entry.fieldType.parent.file.records : new Array();
                if (this.filter.length == 0) {
                    return records;
                }
                const fields = this.getFields().slice(0, -1);
                return records.filter(record => {
                    for (var index = 0; index < fields.length; index++) {
                        if (record[fields[index]].get().includes(this.filter)) {
                            return true;
                        }
                    }
                    return false;
                });
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
                        this.setter(this.entry, object !== null ? object[this.getFields()[0]] : null);
                        return this.close(this.entry.field.getFullIdentifier() === 'trips.route_id');
                    default:
                        return;
                }
            }
        }
    };
</script>