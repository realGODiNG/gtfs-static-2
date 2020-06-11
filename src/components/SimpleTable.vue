<template>
    <div id="simple-table">
        <b-table id="table" :fields="fields()" :items="items()" :key="mainKey">
            <template v-slot:cell()="data">
                <span class="centered" v-if="data.value.record === undefined">
                    <span v-if="move !== null">
                        <b-icon icon="arrow-up" @click="move(data.index, 'up')" />
                        &nbsp;
                        <b-icon icon="arrow-down" @click="move(data.index, 'down')" />
                        &nbsp;
                        <b-icon icon="trash" @click="__delete(data.item)" />
                    </span>
                    <span v-else>
                        <b-icon icon="trash" @click="__delete(data.item)" />
                    </span>
                </span>
                <span v-else-if="data.value.isChild()">
                    <b-form-select :value="data.value.get()" size="sm" @change="data.value.set($event)">
                        <b-form-select-option :value="''" />
                        <option v-for="parent in data.value.getPossibleParents()" :key="parent.get()">
                            {{ parent.get() }}
                        </option>
                    </b-form-select>
                </span>
                <span v-else-if="data.value.isEnumeration()">
                    <b-form-select :value="data.value.get()" size="sm" @change="data.value.set($event)">
                        <option v-for="value in data.value.getEnumerationValues()" :key="value">
                            {{ value }}
                        </option>
                    </b-form-select>
                </span>
                <span v-else>
                    <b-form-input
                        :pattern="data.value.fieldType.structure.getInputPattern()"
                        :type="data.value.fieldType.structure.getInputType()"
                        :value="data.value.get()"
                        @change="data.value.set($event)"
                        size="sm"
                    />
                </span>
            </template>
        </b-table>
    </div>
</template>

<script>
    export default {
        name: 'SimpleTable',

        data() {
            return {
                /** @type {!Number} */
                mainKey: 0
            };
        },
        props: {
            'fields': Function,
            'items': Function,
            'move': Function
        },

        methods: {
            /**
             * @param {!Record} record
             */
            __delete(record) {
                record.__delete();
                this.mainKey += 1;
            }
        }
    };
</script>
