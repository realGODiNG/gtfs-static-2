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
                        <b-icon class="m-1" icon="plus" @click="__addShadow(data.item.__file)" />
                    </fragment>
                    <fragment v-else-if="move !== null">
                        <b-icon class="m-1" icon="arrow-up" @click="move(data.index, 'up')" />
                        <b-icon class="m-1" icon="arrow-down" @click="move(data.index, 'down')" />
                        <b-icon class="m-1" icon="trash" @click="__delete(data.item)" />
                    </fragment>
                    <fragment v-else>
                        <b-icon class="m-1" icon="trash" @click="__delete(data.item)" />
                    </fragment>
                </span>
                <fragment v-else-if="data.value.hasPicker()">
                    <b-form-input type="text"
                        :placeholder="data.value.getDisplayText()"
                        :value="new String()"
                        @click="childStopEntry = data.value"
                        size="sm"
                    />
                </fragment>
                <fragment v-else-if="data.value.isChild()">
                    <b-form-select :value="data.value.get()" size="sm" @change="data.value.set($event)">
                        <b-form-select-option :value="''" />
                        <option v-for="parent in data.value.getPossibleParents()" :key="parent.get()">
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
                        @change="data.value.set($event)"
                        size="sm"
                    />
                </fragment>
            </template>
        </b-table>
        <SimpleStop :entry="childStopEntry"
            :setter="__set"
            :trees="gtfsStopTrees(childStopEntry)"
            @close="childStopEntry = null"
            v-if="childStopEntry !== null"
        />
    </div>
</template>

<script>
    import SimpleStop from './SimpleStop'

    export default {
        name: 'SimpleTable',
        components: {
            SimpleStop
        },

        data() {
            return {
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
            'refresh': Function,
            'gtfsStopTrees': Function
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
            }
        }
    };
</script>
