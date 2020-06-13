<template>
    <div id="texter" class="popup">
        <div id="texter-content" class="popup-content" role="dialog">
            <header id="texter-header">
                <slot name="header">
                    <b-navbar toggleable="lg" type="dark" variant="dark">
                        <b-navbar-brand>
                            {{ wrapper.title }}
                        </b-navbar-brand>
                    </b-navbar>
                </slot>
            </header>
            <section id="texter-body">
                <slot name="body">
                    <b-card>
                        <b-form-input size="sm" type="text" v-model="value" />
                    </b-card>
                </slot>
            </section>
            <footer id="texter-footer" class="centered">
                <slot name="footer">
                    <b-button class="m-1" size="sm" type="button" variant="dark" @click="close()" :disabled='value.length == 0'>
                        Confirm
                    </b-button>
                </slot>
            </footer>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'Texter',

        data() {
            return {
                /** @type {!String} */
                value: ''
            }
        },
        props: {
            'wrapper': { callback: !Function, title: !String }
        },

        methods: {
            close() {
                this.wrapper.callback(this.value);
                this.$emit('close');
            }
        }
    };
</script>
