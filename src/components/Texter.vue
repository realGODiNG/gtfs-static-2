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
            'wrapper': { callback: !Function, title: !String },
        },

        methods: {
            close() {
                this.wrapper.callback(this.value);
                this.$emit('close');
            }
        }
    };
</script>

<style scoped>
    .popup {
        background-color: rgba(0, 0, 0, 0.4);
        height: 100%;
        left: 0;
        overflow: auto;
        position: fixed;
        top: 0;
        width: 100%;
        z-index: 100;
    }
    .popup-content {
        background-color: white;
        border: 2px solid #888;
        left: 50%;
        position: absolute;
        top: 50%;
        width: fit-content;
        -ms-transform: translate(-50%, -50%);
        transform: translate(-50%, -50%);
    }
</style>
