<template>
    <fragment id="simple-tree" :key="mainKey">
        <tr v-if="isRendered">
            <td>
                <span v-if="root.children.length != 0">
                    <b-icon icon="plus" @click="toogle()" v-if="root.isOpened" />
                    <b-icon icon="dash" @click="toogle()" v-else />
                </span>
                <span v-else>
                    <b-icon icon="blank" />
                </span>
                <span v-if="depth != 0">
                    <b-icon icon="blank" v-for="(value, index) in new Array(depth - 1)" :key="index" />
                    <b-icon icon="dot" />
                </span>
                {{ root.record['stop_id'].get() }}
            </td>
            <td>
                {{ root.record['stop_name'].get() }}
            </td>
            <td>
                {{ root.record['location_type'].get() }}
            </td>
            <td>
                {{ root.record['platform_code'].get() }}
            </td>
            <td>
                <b-icon icon="trash" @click="deleter(root.record)" v-if="depth != 0" />
                <b-icon icon="blank" v-else />
            </td>
        </tr>
        <SimpleTree v-for="child in root.children" :key="child.record['stop_id'].get()"
            :deleter="deleter"
            :depth="depth + 1"
            :isRendered="root.isOpened"
            :root="child"
        />
    </fragment>
</template>

<script>
    export default {
        name: 'SimpleTree',

        data() {
            return {
                /** @type {!Number} */
                mainKey: 0
            };
        },
        props: {
            'deleter': Function,
            'depth': Number,
            'isRendered': Boolean,
            'root': Object
        },

        methods: {
            toogle() {
                this.root.isOpened = !this.root.isOpened;
                this.mainKey += 1;
            }
        }
    };
</script>
