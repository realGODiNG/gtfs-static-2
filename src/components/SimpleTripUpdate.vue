<template>
    <div id="simple-trip-update" class="popup">
        <div id="simple-trip-update-content" class="popup-content" role="dialog">
            <header id="simple-trip-update-header">
                <slot name="header">
                    <b-navbar toggleable="lg" type="dark" variant="dark">
                        <b-navbar-brand>
                            Add 'Trip Update'
                        </b-navbar-brand>
                        <b-navbar-nav class="ml-auto">
                            <b-nav-form>
                                <b-icon class="h3 m-1" icon="x-circle-fill" @click="close(false)" variant="danger" />
                            </b-nav-form>
                        </b-navbar-nav>
                    </b-navbar>
                </slot>
            </header>
            <section id="simple-trip-update-body">
                <slot name="body">
                    <b-card>
                        <b-table-simple hover small striped>
                            <b-thead>
                                <b-tr>
                                    <b-th v-if="isFrequencyBased || isScheduleBased">
                                        Start Date
                                    </b-th>
                                    <b-th v-if="isFrequencyBased">
                                        Start Time
                                    </b-th>
                                    <b-th>
                                        Schedule Relationship
                                    </b-th>
                                </b-tr>
                            </b-thead>
                            <b-tbody>
                                <b-tr>
                                    <b-td v-if="isFrequencyBased || isScheduleBased">
                                        <b-form-input type="date" v-model="startDate" size="sm" />
                                    </b-td>
                                    <b-td v-if="isFrequencyBased">
                                        <b-form-select v-model="startTime" :options="stopTimes" size="sm" />
                                    </b-td>
                                    <b-td>
                                        <b-form-select v-model="schedule" :options="scheduleRelationship" size="sm" />
                                    </b-td>
                                </b-tr>
                            </b-tbody>
                        </b-table-simple>
                        <fragment v-if="schedule !== null && schedule !== 'CANCELED'">
                            <b-card v-for="(stopIdentifier, index) in stopIdentifiers" :key="index">
                                <b-form-checkbox class="m-1" v-model="stopTimeBooleans[index.toString()]" @change="toggleStopTimeUpdate(index)">
                                    {{ formator(stopIdentifier.property) + ': ' + stopIdentifier.value }}
                                </b-form-checkbox>
                                <b-table-simple hover small striped v-if="stopTimeBooleans[index.toString()]">
                                    <b-thead>
                                        <b-tr>
                                            <b-th>
                                                Schedule Relationship
                                            </b-th>
                                            <b-th>
                                                Arrival Delay
                                            </b-th>
                                            <b-th>
                                                Departure Delay
                                            </b-th>
                                        </b-tr>
                                    </b-thead>
                                    <b-tbody>
                                        <b-tr>
                                            <b-td>
                                                <b-form-select :options="innerScheduleRelationship" v-model="stopTimeUpdates[index.toString()].schedule" size="sm" />
                                            </b-td>
                                            <b-td>
                                                <b-form-input type="number" step="1" v-model="stopTimeUpdates[index.toString()].arrival_delay" size="sm" />
                                            </b-td>
                                            <b-td>
                                                <b-form-input type="number" step="1" v-model="stopTimeUpdates[index.toString()].departure_delay" size="sm" />
                                            </b-td>
                                        </b-tr>
                                    </b-tbody>
                                </b-table-simple>
                            </b-card>
                        </fragment>
                    </b-card>
                </slot>
            </section>
            <footer id="simple-trip-update-footer" class="centered">
                <slot name="footer">
                    <b-card>
                        <b-button class="m-1" type="button" @click="close(true)" variant="dark" :disabled="!isSaveable">
                            Save
                        </b-button>
                        <b-button class="m-1" type="button" @click="close(false)" variant="dark">
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
        name: 'SimpleTripUpdate',

        data() {
            return {
                /** @type {!String} */
                startDate: '',
                /** @type {!String} */
                startTime: '',
                /** @type {!String} */
                schedule: '',
                /** @type {!Object} */
                stopTimeBooleans: new Object(),
                /** @type {!Object} */
                stopTimeUpdates: new Object()
            }
        },
        props: {
            'realtime': Object,
            'trip': Object
        },

        methods: {
            /**
             * @param {!String} text
             * @returns {!String}
             */
            formator(text) {
                const words = text.split('_').map(word => word.length != 0 ? word[0].toUpperCase() + word.slice(1) : '');
                return words.join(' ').trim();
            },

            /**
             * @param {!Boolean} decision
             */
            close(decision) {
                if (this.schedule === 'CANCELED') {
                    this.stopTimeBooleans = new Object();
                    this.stopTimeUpdates = new Object();
                }
                if (decision) {
                    var stopTimeUpdates = new Array();
                    for (var index = 0; index < this.stops.length; index++) {
                        const __stopTimeUpdate = this.stopTimeUpdates[index.toString()];
                        if (__stopTimeUpdate !== undefined) {
                            stopTimeUpdates.push(new Object());
                            var stopTimeUpdate = stopTimeUpdates[stopTimeUpdates.length - 1];
                            if (__stopTimeUpdate.identifier.property === 'stop_sequence') {
                                stopTimeUpdate['stopSequence'] = Number.parseInt(__stopTimeUpdate.identifier.value);
                            } else if (__stopTimeUpdate.identifier.property === 'stop_id') {
                                stopTimeUpdate['stopId'] = __stopTimeUpdate.identifier.value;
                            }
                            if (__stopTimeUpdate.arrival_delay) {
                                stopTimeUpdate['arrival'] = { delay: Number.parseInt(__stopTimeUpdate.arrival_delay) };
                            }
                            if (__stopTimeUpdate.departure_delay) {
                                stopTimeUpdate['departure'] = { delay: Number.parseInt(__stopTimeUpdate.departure_delay) };
                            }
                            stopTimeUpdate['scheduleRelationship'] = this.innerScheduleRelationship.findIndex(schedule => {
                                return schedule === __stopTimeUpdate.schedule;
                            });
                        }
                    }
                    this.schedule = this.scheduleRelationship.findIndex(schedule => schedule === this.schedule);
                    this.realtime.addTripUpdate(this.trip, this.startDate, this.startTime, this.schedule, stopTimeUpdates);
                }
                this.startDate = '';
                this.startTime = '';
                this.schedule = '';
                this.stopTimeBooleans = new Object();
                this.stopTimeUpdates = new Object();
                this.$emit('close');
            },

            /**
             * @param {!Number} index
             */
            toggleStopTimeUpdate(index) {
                if (this.stopIdentifiers[index] !== undefined) {
                    this.stopTimeUpdates[index.toString()] = this.stopTimeUpdates[index.toString()] === undefined
                        ? { identifier: this.stopIdentifiers[index], arrival_delay: null, departure_delay: null, schedule: 'SCHEDULED' }
                        : undefined;
                }
            }
        },

        computed: {
            /**
             * @returns {!Boolean}
             */
            isFrequencyBased() {
                return this.realtime.isFrequencyBasedTrip(this.trip);
            },
            /**
             * @returns {!Boolean}
             */
            isScheduleBased() {
                return this.realtime.isScheduleBasedTrip(this.trip);
            },
            /**
             * @returns {!Boolean}
             */
            isSaveable() {
                return ((!this.isFrequencyBased && !this.isScheduleBased) || this.startDate.length != 0)
                    && (!this.isFrequencyBased || this.startTime.length != 0)
                    && this.schedule.length != 0;
            },

            /**
             * @returns {!Array.<!Record>}
             */
            stops() {
                if (this.trip.__file.identifier !== 'trips') {
                    return new Array();
                }
                return this.trip['trip_id'].children.flatMap(child => {
                    const stopID = child.record['stop_id'];
                    const stopSequence = child.record['stop_sequence'];
                    return child.field.file.identifier === 'stop_times' && (!stopSequence.isEmpty() || !stopID.isEmpty()) ? child.record : [];
                });
            },
            /**
             * @returns {!Array.<!{ property: !String, value: !String }>}
             */
            stopIdentifiers() {
                return this.stops.map(stop => {
                    const stopID = stop['stop_id'];
                    const stopSequence = stop['stop_sequence'];
                    return stopSequence.isEmpty()
                        ? { property: 'stop_id', value: stopID.get() }
                        : { property: 'stop_sequence', value: stopSequence.get() };
                });
            },
            /**
            * @returns {!Array.<!String>}
            */
            stopTimes() {
                if (this.trip.__file.identifier !== 'trips') {
                    return new Array();
                }
                var times = new Array();
                const isNotGreater = (a, b) => {
                    var [ a0, a1, a2 ] = a.split(':');
                    var [ b0, b1, b2 ] = b.split(':');
                    return (Number.parseInt(a0, 10) - Number.parseInt(b0, 10)) * 3600
                        + (Number.parseInt(a1, 10) - Number.parseInt(b1, 10)) * 60
                        <= Number.parseInt(b2, 10) - Number.parseInt(a2, 10);
                };
                const addSeconds = (time, secs) => {
                    var hours = Math.floor(secs / 3600);
                    var minutes = Math.floor((secs - hours * 3600) / 60);
                    var seconds = secs - minutes * 60 - hours * 3600;
                    var [ t0, t1, t2 ] = time.split(':');
                    seconds += Number.parseInt(t2, 10);
                    if (seconds >= 60) {
                        minutes++;
                        seconds -= 60;
                    }
                    minutes += Number.parseInt(t1, 10);
                    if (minutes >= 60) {
                        hours++;
                        minutes -= 60;
                    }
                    hours += Number.parseInt(t0, 10);
                    return '' + hours + ':' + (minutes <= 9 ? '0' + minutes : minutes) + ':' + (seconds <= 9 ? '0' + seconds : seconds);
                };
                var iteratorTime = '99:99:99';
                this.trip['trip_id'].children.forEach(child => {
                    if (child.field.file.identifier === 'stop_times' && !child.record['departure_time'].isEmpty()) {
                        const time = child.record['departure_time'].get();
                        if (isNotGreater(time, iteratorTime)) {
                            iteratorTime = time;
                        }
                    }
                });
                if (iteratorTime !== '99:99:99') {
                    times.push(iteratorTime);
                    this.trip['trip_id'].children.forEach(child => {
                        if (child.field.file.identifier === 'frequencies' && !child.record['end_time'].isEmpty() && !child.record['headway_secs'].isEmpty()) {
                            const endTime = child.record['end_time'].get();
                            const headwaySeconds = Number.parseInt(child.record['headway_secs'].get(), 10);
                            var time = addSeconds(iteratorTime, headwaySeconds);
                            while (isNotGreater(time, endTime)) {
                                times.push(time);
                                time = addSeconds(time, headwaySeconds);
                            }
                            iteratorTime = time;
                        }
                    });
                }
                return times.sort((a, b) => isNotGreater(a, b) ? (a !== b ? -1 : 0) : 1);
            },

            /**
             * @returns {!Array.<!String>}
             */
            scheduleRelationship() {
                return [ 'SCHEDULED', 'ADDED', 'UNSCHEDULED', 'CANCELED' ];
            },
            /**
             * @returns {!Array.<!String>}
             */
            innerScheduleRelationship() {
                return [ 'SCHEDULED', 'SKIPPED', 'NO_DATA' ];
            }
        }
    };
</script>
