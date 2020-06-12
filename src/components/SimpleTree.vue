<template>
    <fragment id="simple-tree">
        <table class="simple-table" v-if="depth === undefined">
            <thead>
                <tr>
                    <th v-for="field in fields" :key="field">
                        {{ format(field) }}
                    </th>
                </tr>
            </thead>
            <tbody>
                <SimpleTree :depth="0" :fields="fields" :handler="handler" :isRendered="true" :root="root" />
            </tbody>
        </table>
        <fragment v-else>
            <tr v-if="isRendered">
                <td v-for="(field, index) in fields" :key="field">
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
                </td>
            </tr>
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
