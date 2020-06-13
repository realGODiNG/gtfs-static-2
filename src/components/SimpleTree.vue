<template>
    <fragment id="simple-tree">
        <b-table-simple class="simple-table" v-if="depth === undefined">
            <b-thead>
                <b-tr>
                    <b-th v-for="field in fields" :key="field">
                        {{ format(field) }}
                    </b-th>
                </b-tr>
            </b-thead>
            <b-tbody>
                <SimpleTree :depth="0" :fields="fields" :handler="handler" :isRendered="true" :root="root.data" />
                <b-tr v-if="__hasShadow()">
                    <b-td v-for="(entry, index) in __getShadowEntries()" :key="'shadow-' + index">
                        <span v-if="entry === undefined" />
                        <span class="form-inline" v-else>
                            <span v-if="entry.isChild()">
                                <b-form-select :value="entry.get()" size="sm" @change="entry.set($event)">
                                    <b-form-select-option :value="''" />
                                    <option v-for="parent in entry.getPossibleParents()" :key="parent.get()">
                                        {{ parent.get() }}
                                    </option>
                                </b-form-select>
                            </span>
                            <span v-else-if="entry.isEnumeration()">
                                <b-form-select :value="entry.get()" size="sm" @change="entry.set($event)">
                                    <option v-for="value in entry.getEnumerationValues()" :key="value">
                                        {{ value }}
                                    </option>
                                </b-form-select>
                            </span>
                            <span v-else>
                                <b-form-input
                                    :pattern="entry.fieldType.structure.getInputPattern()"
                                    :type="entry.fieldType.structure.getInputType()"
                                    :value="entry.get()"
                                    @change="entry.set($event)"
                                    size="sm"
                                />
                            </span>
                            <span class="centered" v-if="index == fields.length - 1">
                                &nbsp;
                                <b-icon icon="plus" @click="handler('add')" />
                            </span>
                        </span>
                    </b-td>
                </b-tr>
            </b-tbody>
        </b-table-simple>
        <fragment v-else>
            <b-tr v-if="isRendered">
                <b-td v-for="(field, index) in fields" :key="field">
                    <span v-if="index == 0">
                        <span v-if="depth > 0">
                            <b-icon icon="blank" v-for="(value, index) in new Array(depth)" :key="'useless-' + index" />     
                        </span>
                        <span v-if="root.children.length != 0">
                            <b-icon icon="dash" @click="toogle()" v-if="root.isOpened" />
                            <b-icon icon="plus" @click="toogle()" v-else />
                        </span>
                        <span v-else>
                            <b-icon icon="dot" />
                        </span>
                    </span>
                    <span v-if="root.record[field] === undefined">
                        <b-icon icon="trash" @click="handler('delete', root.record)" v-if="depth != 0" />
                        <b-icon icon="blank" v-else />
                    </span>
                    <span v-else>
                        {{ root.record[field].get() }}
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
            'root': Object
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
                return this.fields.length != 0 && this.fields[this.fields.length - 1] === '__action';
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
        }
    };
</script>
