<template>
    <div id="simple-picker" class="popup">
        <div id="simple-picker-content" class="popup-content" role="dialog">
            <header id="simple-picker-header">
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
                                <b-icon class="m-1" icon="trash" @click="applyFilter(true)" :variant="filter.length != 0 ? 'light' : 'dark'" />
                                <b-icon class="m-1" icon="search" @click="applyFilter()" variant="light" />
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
            <section id="simple-picker-body">
                <slot name="body">
                    <b-card :key="mainKey" :style="{ 'min-width': '800px' }">
                        <b-table :fields="getFields()" :items="getRecords()" hover small striped
                            v-if="entry.fieldType.parent.getFullIdentifier() === 'levels.level_id'"
                        >
                            <template v-slot:head()="data">
                                {{ formator(data.column) }}
                            </template>
                            <template v-slot:cell()="data">
                                <span class="centered" v-if="data.value.record === undefined">
                                    <fragment v-if="data.item.__isShadow">
                                        <b-icon class="m-1" icon="plus" @click="data.item.__file.addShadowRecord()"/>
                                    </fragment>
                                    <fragment v-else>
                                        <b-icon class="m-1" icon="check" @click="handler('select', data.item)" />
                                        <b-icon class="m-1" icon="trash" @click="data.item.__delete()" />
                                    </fragment>
                                </span>
                                <b-form-input size="sm"
                                    :pattern="data.value.fieldType.structure.getInputPattern()"
                                    :type="data.value.fieldType.structure.getInputType()"
                                    :value="data.value.get()"
                                    @change="data.value.set($event)"
                                    v-bind:class="[!data.value.record.__isShadow && data.value.record.__isEqual(entry.data !== null ? entry.data.record : null) ? 'selected' : '']"
                                    v-else
                                />
                            </template>
                        </b-table>
                        <b-table :fields="getFields()" :items="getRecords()" hover small striped v-else>
                            <template v-slot:head()="data">
                                {{ formator(data.column) }}
                            </template>
                            <template v-slot:cell()="data">
                                <span class="centered" v-if="data.value.record === undefined">
                                    <b-icon class="m-1" icon="check" @click="handler('select', data.item)" />
                                </span>
                                <fragment v-else-if="entry.record.__isShadow ? data.value.record[entry.field.identifier].get() === entry.data : data.value.record.__isEqual(entry.data !== null ? entry.data.record : null)">
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
    export default {
        name: 'SimplePicker',
        
        data() {
            return {
                /** @type {!Number} */
                mainKey: 0,

                /** @type {!String} */
                filterWrapper: '',

                /** @type {!String} */
                filter: '',

                /** @type {?Record} */
                currentRecord: null
            }
        },
        props: {
            'entry': Object,
            'setter': Function
        },

        mounted() {
            if (this.entry.fieldType.parent.getFullIdentifier() === 'levels.level_id') {
                this.entry.fieldType.parent.file.shadowRecord.__delete();
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
                        return [ 'level_id', 'level_index', 'level_name', '__actions' ];
                    default:
                        return new Array();
                }
            },
            /** @returns {!Array.<!Record>} */
            getRecords() {
                var records = this.entry.fieldType.parent !== null ? this.entry.fieldType.parent.file.records : new Array();
                if (this.filter.length != 0) {
                    const fields = this.getFields().slice(0, -1);
                    records = records.filter(record => {
                        for (var index = 0; index < fields.length; index++) {
                            if (record[fields[index]].get().includes(this.filter)) {
                                return true;
                            }
                        }
                        return false;
                    });
                }
                return this.entry.fieldType.parent.getFullIdentifier() === 'levels.level_id'
                    ? records.concat([ this.entry.fieldType.parent.file.shadowRecord ])
                    : records;
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

<style scoped>
    .selected {
        font-weight: bold;
    }
</style>
