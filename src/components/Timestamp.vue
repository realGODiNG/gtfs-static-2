<template>
    <div id="texter" class="popup">
        <div id="texter-content" class="popup-content" role="dialog">
            <header id="texter-header">
                <slot name="header">
                    <b-navbar toggleable="lg" type="dark" variant="dark">
                        <b-navbar-brand>
                            Edit Timestamp
                        </b-navbar-brand>
                        <b-navbar-nav class="ml-auto">
                            <b-nav-form>
                                <b-icon class="h3 m-1" icon="x-circle-fill" @click="close(false)" variant="danger" />
                            </b-nav-form>
                        </b-navbar-nav>
                    </b-navbar>
                </slot>
            </header>
            <section id="texter-body">
                <slot name="body">
                    <b-card>
                        Date *
                        <b-form-input size="sm" type="date" v-model="cTimestamp[0]" />
                        <br />
                        Time *
                        <b-form-input size="sm" type="time" step="1" v-model="cTimestamp[1]" />
                    </b-card>
                </slot>
            </section>
            <footer id="texter-footer" class="centered">
                <slot name="footer">
                    <b-card>
                        <b-button class="m-1" type="button" variant="dark" @click="close(true)" :disabled='cTimestamp[0].length * cTimestamp[1].length == 0'>
                            Save
                        </b-button>
                        <b-button class="m-1" type="button" variant="dark" @click="close(false)">
                            Discard
                        </b-button>
                    </b-card>
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
                /** @type {!Array.<!String>} */
                cTimestamp: this.converter(this.timestamp),
            }
        },
        props: {
            'converter': Function,
            'timestamp': Number
        },

        methods: {
            /**
             * @param {!Boolean} decision
             */
            close(decision) {
                this.$emit('close', decision ? this.converter(this.cTimestamp): null);
            }
        }
    };
</script>
