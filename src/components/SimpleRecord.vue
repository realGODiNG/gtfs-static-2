<template>
    <div id="simple-record" class="popup">
        <div id="simple-record-content" class="popup-content" role="dialog">
            <header id="simple-record-header">
                <slot name="header">
                    <b-navbar toggleable="lg" type="dark" variant="dark">
                        <b-navbar-brand>
                            Edit 'Record'
                        </b-navbar-brand>
                        <b-navbar-nav class="ml-auto">
                            <b-nav-item disabled>
                                File: '{{ record.__file.name }}'
                            </b-nav-item>
                        </b-navbar-nav>
                        <b-navbar-nav class="ml-auto">
                            <b-nav-form>
                                <b-icon class="h3 m-1" icon="x-circle-fill" @click="close()" variant="danger" />
                            </b-nav-form>
                        </b-navbar-nav>
                    </b-navbar>
                </slot>
            </header>
            <section id="simple-record-body">
                <slot name="body">
                    <b-card>
                        <b-table-simple hover small striped :key="mainKey">
                            <b-thead>
                                <b-tr>
                                    <b-th>
                                        Property
                                    </b-th>
                                    <b-th>
                                        Value
                                    </b-th>
                                    <b-th>
                                        Type
                                    </b-th>
                                </b-tr>
                            </b-thead>
                            <b-tbody>
                                <b-tr v-for="field in record.__file.fields" :key="field.identifier">
                                    <b-td>
                                        <span v-b-tooltip.hover="{ placement: 'left', title: field.description }">
                                            {{ field.name }}:
                                        </span>
                                    </b-td>
                                    <b-td>
                                        <fragment v-if="record[field.identifier].isChild()">
                                            <b-form-select :value="record[field.identifier].get()" size="sm" @change="record[field.identifier].set($event)">
                                                <b-form-select-option :value="''" />
                                                <!-- BAD PERFORMANCE: <option v-for="parent in record[field.identifier].getPossibleParents()" :key="parent.get()"> -->
                                                <option v-for="(parent, index) in record[field.identifier].getPossibleParents()" :key="index">
                                                    {{ parent.get() }}
                                                </option>
                                            </b-form-select>
                                        </fragment>
                                        <fragment v-else-if="record[field.identifier].isEnumeration()">
                                            <b-form-select :value="record[field.identifier].get()" size="sm" @change="record[field.identifier].set($event)">
                                                <option v-for="value in record[field.identifier].getEnumerationValues()" :key="value">
                                                    {{ value }}
                                                </option>
                                            </b-form-select>
                                        </fragment>
                                        <fragment v-else>
                                            <b-form-input
                                                :pattern="record[field.identifier].fieldType.structure.getInputPattern()"
                                                :type="record[field.identifier].fieldType.structure.getInputType()"
                                                :value="record[field.identifier].get()"
                                                @change="record[field.identifier].set($event)"
                                                size="sm"
                                            />
                                        </fragment>
                                    </b-td>
                                    <b-td>
                                        <b-form-select :value="record[field.identifier].fieldType.name" size="sm"
                                            @change="mainKey += record[field.identifier].setFieldType($event)"
                                            :disabled="record[field.identifier].field.types.length == 1"
                                        >
                                            <option v-for="fieldType in record[field.identifier].field.types" :key="fieldType.name">
                                                {{ fieldType.name }}
                                            </option>
                                        </b-form-select>
                                    </b-td>
                                </b-tr>
                            </b-tbody>
                        </b-table-simple>
                    </b-card>
                </slot>
            </section>
            <footer id="simple-record-footer" class="centered">
                <slot name="footer">
                    <b-card>
                        <b-button class="m-1" type="button" variant="dark" @click="close()">
                            Close
                        </b-button>
                    </b-card>
                </slot>
            </footer>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'SimpleRecord',

        data() {
            return {
                /** @type {!Number} */
                mainKey: 0
            };
        },
        props: {
            'record': Object
        },

        methods: {
            close() {
                this.$emit('close');
            }
        }
    };
</script>
