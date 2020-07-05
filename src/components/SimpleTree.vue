<template>
    <fragment id="simple-tree">
        <b-table-simple hover small striped v-if="depth === undefined">
            <b-thead>
                <b-tr>
                    <b-th v-for="field in fields" :key="field">
                        {{ format(field) }}
                    </b-th>
                    <b-th v-if="!__hasShadow()">
                        Select
                    </b-th>
                </b-tr>
            </b-thead>
            <b-tbody>
                <SimpleTree :depth="0" :fields="fields" :handler="handler" :isRendered="true" :root="root.data" />
                <b-tr v-if="__hasShadow()">
                    <b-td v-for="(entry, index) in __getShadowEntries()" :key="'shadow-' + index">
                        <span v-if="entry !== undefined">
                            <fragment v-if="index == fields.length - 1">
                                <b-form-select :value="entry.get()" size="sm" @change="entry.set($event)">
                                    <!-- BAD PERFORMANCE: <option v-for="parent in root.flat().map(record => record['stop_id'])" :key="parent.get()"> -->
                                    <option v-for="stopID in stopIDs" :key="stopID">
                                        {{ stopID }}
                                    </option>
                                </b-form-select>
                            <span class="centered">
                                <b-icon class="m-1" icon="plus" @click="handler('add')"
                                    v-b-tooltip.hover="{ placement: 'top', title: 'Add record.' }"
                                />
                            </span>
                            </fragment>
                            <fragment v-else-if="entry.isChild()">
                                <b-form-select :value="entry.get()" size="sm" @change="entry.set($event)">
                                    <b-form-select-option :value="''" />
                                    <!-- BAD PERFORMANCE: <option v-for="parent in entry.getPossibleParents()" :key="parent.get()"> -->
                                    <option v-for="(parent, index) in entry.getPossibleParents()" :key="index">
                                        {{ parent.get() }}
                                    </option>
                                </b-form-select>
                            </fragment>
                            <fragment v-else-if="entry.isEnumeration()">
                                <b-form-select :value="entry.get()" size="sm" @change="entry.set($event)">
                                    <option v-for="value in entry.getEnumerationValues()" :key="value">
                                        {{ value }}
                                    </option>
                                </b-form-select>
                            </fragment>
                            <fragment v-else>
                                <b-form-input
                                    :pattern="entry.fieldType.structure.getInputPattern()"
                                    :type="entry.fieldType.structure.getInputType()"
                                    :value="entry.get()"
                                    @change="entry.set($event)"
                                    size="sm"
                                />
                            </fragment>
                        </span>
                    </b-td>
                </b-tr>
                <SimpleTree v-for="(tree, index) in trees" :key="'tree-' + index"
                    :depth="0" :fields="fields" :handler="handler" :isRendered="true" :root="tree.data"
                    v-else-if="trees !== undefined"
                />
            </b-tbody>
        </b-table-simple>
        <fragment v-else>
            <b-tr v-if="isRendered">
                <b-td v-for="(field, index) in fields" :key="field">
                    <fragment v-if="index == 0">
                        <fragment v-if="depth > 0">
                            <b-icon icon="blank" v-for="(value, index) in new Array(depth)" :key="'useless-' + index" />     
                        </fragment>
                        <fragment v-if="root.children.length != 0">
                            <b-icon icon="dash" @click="toogle()" v-if="root.isOpened"
                                v-b-tooltip.hover="{ placement: 'top', title: 'Close tree node.' }"
                            />
                            <b-icon icon="plus" @click="toogle()" v-else
                                v-b-tooltip.hover="{ placement: 'top', title: 'Open tree node.' }"
                            />
                        </fragment>
                        <fragment v-else>
                            <b-icon icon="dot" />
                        </fragment>
                    </fragment>
                    <span class="centered" v-if="root.record[field] === undefined">
                        <b-icon class="m-1" icon="check" @click="handler('select', root.record)"
                            v-b-tooltip.hover="{ placement: 'top', title: 'Select record.' }"
                        />
                        <b-icon class="m-1" icon="trash" @click="handler('delete', root.record)" v-if="depth != 0"
                            v-b-tooltip.hover="{ placement: 'top', title: 'Delete record.' }"
                        />
                        <b-icon class="m-1" icon="blank" v-else />
                    </span>
                    <fragment v-else-if="root.isSelected">
                        <b>
                            {{ root.record[field].get() }}
                        </b>
                    </fragment>
                    <fragment v-else>
                        {{ root.record[field].get() }}
                    </fragment>
                </b-td>
                <b-td v-if="!__hasShadow()">
                    <span class="centered">
                        <b-icon class="m-1" icon="check" @click="handler('select', root.record)" v-if="handler('legal', root.record)"
                            v-b-tooltip.hover="{ placement: 'top', title: 'Select record.' }"
                        />
                    </span>
                </b-td>
            </b-tr>
            <SimpleTree v-for="(child, index) in this.root.children" :key="index"
                :depth="depth + 1"
                :fields="fields"
                :handler="handler"
                :isRendered="isRendered && root.isOpened"
                :root="child"
            />
        </fragment>
    </fragment>
</template>

<script>
    export default {
        name: 'SimpleTree',

        props: {
            'depth': Number,
            'fields': Array,
            'handler': Function,
            'isRendered': Boolean,
            'root': Object,
            'trees': Array
        },

        methods: {
            /**
             * @returns {!Array.<?Entry>}
             */
            __getShadowEntries() {
                if (!this.__hasShadow()) {
                    return new Array();
                }
                const shadow = this.handler('shadow');
                const entries = this.fields.map(field => shadow[field]);
                entries[entries.length - 1] = shadow[this.root.field];
                return entries;
            },
            /**
             * @returns {!Boolean>}
             */
            __hasShadow() {
                return this.fields.length != 0 && this.fields[this.fields.length - 1] === '__actions';
            },

            /**
             * @param {!String} text
             * @returns {!String}
             */
            format(text) {
                return text.split('_').map(word => word.length != 0 ? word[0].toUpperCase() + word.slice(1) : '').join(' ').trim();
            },

            toogle() {
                this.root.isOpened = !this.root.isOpened;
                this.handler('refresh');
            }
        },

        computed: {
            /**
             * @returns {!Array.<!String>}
             */
            stopIDs() {
                return this.root.flat().map(record => record['stop_id'].get());
            }
        }
    };
</script>
