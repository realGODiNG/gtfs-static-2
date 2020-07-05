<template>
    <div id="simple-table">
        <b-table id="table"
            :fields="fields()"
            :items="items()"
            :key="mainKey"
            hover small striped
        >
            <template v-slot:cell()="data">
                <span class="centered" v-if="data.value.record === undefined">
                    <fragment v-if="data.item.__isShadow">
                        <fragment v-if="isFilled(data.item)">
                            <b-icon class="m-1" icon="plus" @click="__addShadow(data.item.__file)"
                                v-b-tooltip.hover="{ placement: 'top', title: 'Add record.' }"
                            />
                            <b-icon class="m-1" icon="shuffle" @click="__addShadowBidirectional(data.item.__file)"
                                v-b-tooltip.hover="{ placement: 'top', title: 'Add record bidirectionally.' }"
                                v-if="data.item.__file.identifier === 'transfers'"
                            />
                        </fragment>
                    </fragment>
                    <fragment v-else-if="move !== null">
                        <b-icon class="m-1" icon="arrow-up" @click="move(data.index, 'up')"
                            v-b-tooltip.hover="{ placement: 'top', title: 'Move record up.' }"
                        />
                        <b-icon class="m-1" icon="arrow-down" @click="move(data.index, 'down')"
                            v-b-tooltip.hover="{ placement: 'top', title: 'Move record down.' }"
                        />
                        <b-icon class="m-1" icon="trash" @click="__delete(data.item)"
                            v-b-tooltip.hover="{ placement: 'top', title: 'Delete record.' }"
                        />
                    </fragment>
                    <fragment v-else>
                        <b-icon class="m-1" icon="trash" @click="__delete(data.item)"
                            v-b-tooltip.hover="{ placement: 'top', title: 'Delete record.' }"
                        />
                    </fragment>
                </span>
                <fragment v-else-if="data.value.hasPicker()">
                    <b-form-input type="text"
                        :placeholder="data.value.getDisplayText()"
                        :value="new String()"
                        @click="childStopEntry = data.value"
                        size="sm"
                        v-if="needsStopPicker(data.value)"
                    />
                    <b-form-input type="text"
                        :placeholder="data.value.getDisplayText()"
                        :value="new String()"
                        @click="childEntry = data.value;"
                        size="sm"
                        v-else
                    />
                </fragment>
                <fragment v-else-if="data.value.isChild()">
                    <b-form-select :value="data.value.get()" size="sm" @change="data.value.set($event)">
                        <b-form-select-option :value="''" />
                        <!-- BAD PERFORMANCE: <option v-for="parent in data.value.getPossibleParents()" :key="parent.get()"> -->
                        <option v-for="(parent, index) in data.value.getPossibleParents()" :key="index">
                            {{ parent.get() }}
                        </option>
                    </b-form-select>
                </fragment>
                <fragment v-else-if="data.value.isEnumeration()">
                    <b-form-select :value="data.value.get()" size="sm" @change="data.value.set($event)">
                        <option v-for="value in data.value.getEnumerationValues()" :key="value">
                            {{ value }}
                        </option>
                    </b-form-select>
                </fragment>
                <fragment v-else>
                    <b-form-input
                        :pattern="data.value.fieldType.structure.getInputPattern()"
                        :type="data.value.fieldType.structure.getInputType()"
                        :value="data.value.get()"
                        @change="__innerSet(data.value, $event)"
                        size="sm"
                    />
                </fragment>
            </template>
        </b-table>
        <SimplePicker :entry="childEntry"
            :setter="__set"
            @close="childEntry = null"
            v-if="childEntry !== null"
        />
        <SimpleStop :entry="childStopEntry"
            :setter="__set"
            :trees="gtfsStopTrees(childStopEntry)"
            :preFilter="childStopEntry.record.__isShadow ? stopPreFilter : undefined"
            @close="childStopEntry = null"
            v-if="childStopEntry !== null"
        />
    </div>
</template>

<script>
    import SimplePicker from './SimplePicker'
    import SimpleStop from './SimpleStop'

    export default {
        name: 'SimpleTable',
        components: {
            SimplePicker,
            SimpleStop
        },

        data() {
            return {
                /** @type {?Entry} */
                childEntry: null,

                /** @type {?Entry} */
                childStopEntry: null,

                /** @type {!Number} */
                mainKey: 0,
            };
        },
        props: {
            'fields': Function,
            'items': Function,
            'move': Function,
            'needsStopPicker': Function,
            'refresh': Function,
            'gtfsStopTrees': Function,
            'stopPreFilter': String
        },

        methods: {
            /**
             * @param {!File} file
             */
            __addShadow(file) {
                file.addShadowRecord();
                if (this.refresh !== undefined) {
                    this.refresh();
                }
                this.mainKey += 1;
            },
            /**
             * @param {!File} file
             */
            __addShadowBidirectional(file) {
                if (file.identifier === 'transfers') {
                    file.createRecord(file.shadowRecord.__toArray());
                    const fromStopId = file.shadowRecord['from_stop_id'].get();
                    file.shadowRecord['from_stop_id'].set(file.shadowRecord['to_stop_id'].get());
                    file.shadowRecord['to_stop_id'].set(fromStopId);
                    this.__addShadow(file);
                }
            },
            /**
             * @param {!Record} record
             */
            __delete(record) {
                record.__delete();
                if (this.refresh !== undefined) {
                    this.refresh();
                }
                this.mainKey += 1;
            },
            /**
             * @param {!Entry} entry
             * @param {!String|!Entry} data
             */
            __set(entry, data) {
                entry.set(data);
                this.mainKey += 1;
            },
            /**
             * @param {!Entry} entry
             * @param {!String} data
             */
            __innerSet(entry, data) {
                var regex = null;
                switch (entry.fieldType.structure.identifier) {
                    case 'Time':
                        regex = data.match('[0-3]?\\d:[0-5]\\d|4[0-7]:[0-5]\\d');
                        if (regex !== null && regex[0] === data) {
                            entry.set(data + ':00');
                            this.mainKey += 1;
                        } else {
                            entry.set(data);
                        }
                        break;
                    default:
                        entry.set(data);
                        break;
                }
            },

            /**
             * @param {!Record} record
             * @returns {!Boolean}
             */
            isFilled(record) {
                switch (record.__file.identifier) {
                    case 'transfers':
                        // fallsthrough
                    case 'pathways':
                        return !record['from_stop_id'].isEmpty() || !record['to_stop_id'].isEmpty();
                    default:
                        return true;
                }
            }
        }
    };
</script>
