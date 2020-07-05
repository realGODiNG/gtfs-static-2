<template>
    <div id="simple-trip-update" class="popup" :key="mainKey">
        <div id="simple-trip-update-content" class="popup-content" role="dialog">
            <header id="simple-trip-update-header">
                <slot name="header">
                    <b-navbar toggleable="lg" type="dark" variant="dark">
                        <b-navbar-brand>
                            {{ (tripUpdate.entity === undefined ? 'Create' : 'Edit') + ' \'Trip Update\'' }}
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
                    <b-card title="Trip">
                        <b-table-simple fixed small>
                            <b-tr>
                                <b-td colspan="2">
                                    Trip ID *
                                    <b-form-input size="sm" type="text"
                                        :value="tripUpdate.tripUpdate.trip.tripId"
                                        @change="setTripId($event)"
                                    />
                                </b-td>
                                <b-td colspan="2">
                                    Route ID
                                    <b-form-input size="sm" type="text"
                                        :placeholder="getRouteDisplayText()"
                                        :value="new String()"
                                        @click="routeShadow['route_id'].set(tripUpdate.tripUpdate.trip.routeId); routeId = routeShadow['route_id']"
                                        :disabled="tripExists"
                                    />
                                </b-td>
                                <b-td colspan="2">
                                    Direction
                                    <b-form-select size="sm"
                                        :value="tripUpdate.tripUpdate.trip.directionId"
                                        @change="tripUpdate.tripUpdate.trip.directionId = $event"
                                        :disabled="tripExists"
                                    >
                                        <option v-for="value in realtime.dataset.get('trips').get('direction_id').types[0].enumeration.values" :key="value">
                                            {{ value }}
                                        </option>
                                    </b-form-select>
                                </b-td>
                            </b-tr>
                            <b-tr>
                                <b-td colspan="2">
                                    Start Date *
                                    <b-form-input type="date"  size="sm"
                                        :value="tripUpdate.tripUpdate.trip.startDate"
                                        @change="tripUpdate.tripUpdate.trip.startDate = $event; mainKey += 1"
                                    />
                                </b-td>
                                <b-td colspan="2">
                                    Start Time
                                    <b-form-input size="sm" type="text" v-model="tripUpdate.tripUpdate.trip.startTime"
                                        :pattern="'[0-3]?\\d:[0-5]\\d:[0-5]\\d|4[0-7]:[0-5]\\d:[0-5]\\d'"
                                    />
                                </b-td>
                                <b-td colspan="2">
                                    Schedule Relationship
                                    <b-form-select size="sm"
                                        :value="tripUpdate.tripUpdate.trip.scheduleRelationship"
                                        @change="setScheduleRelationship($event)"
                                    >
                                        <option v-for="value in tripExists ? [ 'SCHEDULED', 'UNSCHEDULED', 'CANCELED' ] : [ 'ADDED' ]" :key="value">
                                            {{ value }}
                                        </option>
                                    </b-form-select>
                                </b-td>
                            </b-tr>
                            <b-tr v-if="tripUpdate.tripUpdate.trip.scheduleRelationship !== 'CANCELED'">
                                <b-td colspan="1">
                                    <b-form-input type="number" step="1" v-model="seconds" size="sm" />
                                </b-td>
                                <b-td colspan="5">
                                    <b-button size="sm" type="button" @click="__addSeconds()" variant="dark" :disabled="seconds.length == 0">
                                        Add Seconds
                                    </b-button>
                                    <b-icon size="sm" icon="blank" />
                                    (Use this to modify 'Start Time' and 'Arrival / Departure Time' for all existing stops at once.)
                                </b-td>
                            </b-tr>
                        </b-table-simple>
                    </b-card>
                    <b-card title="Update">
                        <b-table-simple fixed small>
                            <b-tr>
                                <b-td>
                                    Id *
                                    <b-form-input type="text" v-model="tripUpdate.id" size="sm" />
                                </b-td>
                                <b-td>
                                    Timestamp (Date)
                                    <b-form-input type="date" v-model="tripUpdate.tripUpdate.timestamp[0]" size="sm" />
                                </b-td>
                                <b-td>
                                    Timestamp (Time)
                                    <b-form-input type="time" step="1" v-model="tripUpdate.tripUpdate.timestamp[1]" size="sm" />
                                </b-td>
                                <b-td>
                                    Delay
                                    <b-form-input type="number" step="1" v-model="tripUpdate.tripUpdate.delay" size="sm"
                                        v-if="tripUpdate.tripUpdate.trip.scheduleRelationship !== 'ADDED' && tripUpdate.tripUpdate.trip.scheduleRelationship !== 'CANCELED'"
                                    />  
                                    <b-form-input type="text" size="sm" disabled v-else />
                                </b-td>
                            </b-tr>
                        </b-table-simple>
                    </b-card>
                    <b-card title="Stops" v-if="tripUpdate.tripUpdate.trip.scheduleRelationship !== 'CANCELED'">
                        <b-table-simple fixed hover small striped :style="{ 'min-width': '1200px' }">
                            <b-thead>
                                <b-tr>
                                    <b-th colspan="2">
                                        Schedule Relationship
                                    </b-th>
                                    <b-th colspan="1">
                                        Stop Seq.
                                    </b-th>
                                    <b-th colspan="3">
                                        Stop Id
                                    </b-th>
                                    <b-th colspan="2">
                                        Arrival Time
                                    </b-th>
                                    <b-th colspan="2">
                                        Depature Time
                                    </b-th>
                                    <b-th colspan="1">
                                        Actions
                                    </b-th>
                                </b-tr>
                            </b-thead>
                            <b-tbody>
                                <b-tr v-for="(stopTimeUpdate, index) in getStopTimeUpdates()" :key="index">
                                    <b-td colspan="2">
                                        <b-form-select size="sm"
                                            :value="stopTimeUpdate.scheduleRelationship"
                                            @change="stopTimeUpdate.scheduleRelationship = $event"
                                        >
                                            <option v-for="value in realtime.innerScheduleRelationships" :key="value">
                                                {{ value }}
                                            </option>
                                        </b-form-select>
                                    </b-td>
                                    <b-td colspan="1">
                                        <b-form-input type="number" step="1" min="0" v-model="stopTimeUpdate.stopSequence" size="sm" />
                                    </b-td>
                                    <b-td colspan="3">
                                        <b-form-input type="text"
                                            :placeholder="getStopDisplayText(stopTimeUpdate)"
                                            :value="new String()"
                                            @click="stopShadow['stop_id'].set(stopTimeUpdate.stopId); stopId = stopShadow['stop_id']; currentStopTimeUpdate = stopTimeUpdate;"
                                            size="sm"
                                        />
                                    </b-td>
                                    <fragment v-if="stopTimeUpdate.scheduleRelationship !== 'NO_DATA'">
                                        <b-td colspan="2">
                                            <b-form-input size="sm" type="text" v-model="stopTimeUpdate.arrivalTime"
                                                :pattern="'[0-3]?\\d:[0-5]\\d:[0-5]\\d|4[0-7]:[0-5]\\d:[0-5]\\d'"
                                            />
                                        </b-td>
                                        <b-td colspan="2">
                                            <b-form-input size="sm" type="text" v-model="stopTimeUpdate.departureTime"
                                                :pattern="'[0-3]?\\d:[0-5]\\d:[0-5]\\d|4[0-7]:[0-5]\\d:[0-5]\\d'"
                                            />
                                        </b-td>
                                    </fragment>
                                    <fragment v-else>
                                        <b-td colspan="2">
                                            <b-form-input size="sm" type="text" disabled />
                                        </b-td>
                                        <b-td colspan="2">
                                            <b-form-input size="sm" type="text" disabled />
                                        </b-td>
                                    </fragment>
                                    <b-td colspan="1">
                                        <span class="centered">
                                            <b-icon class="m-1" icon="trash" @click="__delete(index)"
                                                v-if="index < tripUpdate.tripUpdate.stopTimeUpdate.length"
                                                v-b-tooltip.hover="{ placement: 'top', title: 'Delete stop time update.' }"
                                            />
                                            <b-icon class="m-1" icon="plus" @click="__add()"    
                                                v-b-tooltip.hover="{ placement: 'top', title: 'Add stop time update.' }"
                                                v-else
                                            />
                                        </span>
                                    </b-td>
                                </b-tr>
                                <b-tr>
                                    <b-td colspan="10" />
                                    <b-td colspan="1">
                                        <span class="centered">
                                            <b-button @click="sortStopTimeUpdates()" size="sm" type="button" variant="dark">
                                                Sort
                                            </b-button>
                                        </span>
                                    </b-td>
                                </b-tr>
                            </b-tbody>
                        </b-table-simple>
                    </b-card>
                </slot>
            </section>
            <footer id="simple-trip-update-footer" class="centered">
                <slot name="footer">
                    <b-card>
                        <b-button class="m-1" type="button" @click="close(true)" variant="dark"
                            :disabled="tripUpdate.id.length * tripUpdate.tripUpdate.trip['tripId'].length * tripUpdate.tripUpdate.trip['startDate'].length == 0"
                        >
                            {{ tripUpdate.entity === undefined ? 'Confirm' : 'Save' }}
                        </b-button>
                        <b-button class="m-1" type="button" @click="close(false)" variant="dark" v-if="tripUpdate.entity !== undefined">
                            Discard
                        </b-button>
                    </b-card>
                </slot>
            </footer>
        </div>
        <SimplePicker :entry="routeId"
            :setter="(entry, data) => tripUpdate.tripUpdate.trip['routeId'] = data !== null ? data.get() : ''"
            @close="routeId = null"
            v-if="routeId !== null"
        />
        <SimpleStop :entry="stopId"
            :setter="(entry, data) => currentStopTimeUpdate['stopId'] = data !== null ? data.get() : ''"
            :trees="gtfsStopTrees(stopId)"
            @close="stopId = null; currentStopTimeUpdate = null"
            v-if="stopId !== null && currentStopTimeUpdate !== null"
        />
    </div>
</template>

<script>
    import SimplePicker from './SimplePicker.vue'
    import SimpleStop from './SimpleStop.vue'

    export default {
        name: 'SimpleTripUpdate',
        components: {
            SimplePicker,
            SimpleStop
        },

        data() {
            return {
                /** @type {!Number} */
                mainKey: 0,

                /** @type {!Array.<!Record>} */
                trips: this.realtime.dataset.get('trips').records,

                /** @type {!Boolean} */
                tripExists: null,

                /** @type {!Record} */
                routeShadow: this.realtime.dataset.createShadow('trips'),

                /** @type {?Entry} */
                routeId: null,

                /** @type {!Record} */
                stopShadow: this.realtime.dataset.createShadow('stops'),

                /** @type {?Entry} */
                stopId: null,

                /** @type {?Object} */
                currentStopTimeUpdate: null,

                /** @type {!Object} */
                shadowStopTimeUpdate: { stopSequence: '', stopId: '', arrivalTime: '', departureTime: '', scheduleRelationship: 'SCHEDULED' },

                /** @type {!String} */
                seconds: ''
            };
        },
        mounted() {
            this.setTripId(this.tripUpdate.tripUpdate.trip.tripId);
        },
        props: {
            'realtime': Object,
            'tripUpdate': Object,
            'gtfsStopTrees': Function
        },

        methods: {
            __add() {
                this.tripUpdate.tripUpdate.stopTimeUpdate.push({
                    stopSequence: this.shadowStopTimeUpdate['stopSequence'],
                    stopId: this.shadowStopTimeUpdate['stopId'],
                    arrivalTime: this.shadowStopTimeUpdate['arrivalTime'],
                    departureTime: this.shadowStopTimeUpdate['departureTime'],
                    scheduleRelationship: this.shadowStopTimeUpdate['scheduleRelationship']
                });
                this.shadowStopTimeUpdate = { stopSequence: '', stopId: '', arrivalTime: '', departureTime: '', scheduleRelationship: 'SCHEDULED' };
            },
            __addSeconds() {
                const convert = time => {
                    if (typeof time === 'string') {
                        const [ hours, minutes, seconds ] = time.split(':');
                        return Number.parseInt(hours, 10) * 3600 + Number.parseInt(minutes, 10) * 60 + Number.parseInt(seconds, 10);
                    } else {
                        var seconds = time;
                        const hours = Math.floor(seconds / 3600);
                        seconds -= hours * 3600;
                        const minutes = Math.floor(seconds / 60);
                        seconds -= minutes * 60;
                        return hours.toString() + ':' + ('0' + minutes).substr(-2) + ':' + ('0' + seconds).substr(-2);
                    }
                };
                const isValid = time => {
                    const regex = time.match('[0-3]?\\d:[0-5]\\d:[0-5]\\d|4[0-7]:[0-5]\\d:[0-5]\\d');
                    return regex !== null && regex[0] === time;
                };
                const __seconds = Number.parseInt(this.seconds, 10);
                if (!isNaN(__seconds)) {
                    if (isValid(this.tripUpdate.tripUpdate.trip['startTime'])) {
                        this.tripUpdate.tripUpdate.trip['startTime'] = convert(convert(this.tripUpdate.tripUpdate.trip['startTime']) + __seconds);
                    }
                    this.tripUpdate.tripUpdate.stopTimeUpdate.forEach(stopTimeUpdate => {
                        if (isValid(stopTimeUpdate['arrivalTime'])) {
                            stopTimeUpdate['arrivalTime'] = convert(convert(stopTimeUpdate['arrivalTime']) + __seconds);
                        }
                        if (isValid(stopTimeUpdate['departureTime'])) {
                            stopTimeUpdate['departureTime'] = convert(convert(stopTimeUpdate['departureTime']) + __seconds);
                        }
                    });
                    this.seconds = '';
                    this.mainKey += 1;
                }
            },
            /**
             * @param {!Number} index
             */
            __delete(index) {
                if (this.tripUpdate.tripUpdate.stopTimeUpdate[index] !== undefined) {
                    this.tripUpdate.tripUpdate.stopTimeUpdate.splice(index, 1);
                }
            },

            /**
             * @param {!Boolean} decision
             */
            close(decision) {
                if (decision) {
                    this.realtime.addTripUpdate(this.tripUpdate);
                }
                this.$emit('close');
            },

            /**
             * @returns {!String}
             */
            getRouteDisplayText() {
                const routeID = this.tripUpdate.tripUpdate.trip['routeId'];
                const route = routeID.length != 0
                    ? this.realtime.dataset.get('routes').records.find(route => route['route_id'].get() === routeID)
                    : undefined;
                return route !== undefined ? route['route_id'].getDisplayText() : '';
            },
            /**
             * @param {!Object} stopTimeUpdate
             * @returns {!String}
             */
            getStopDisplayText(stopTimeUpdate) {
                const stopID = stopTimeUpdate['stopId'];
                const stop = stopID.length != 0
                    ? this.realtime.dataset.get('stops').records.find(stop => stop['stop_id'].get() === stopID)
                    : undefined;
                return stop !== undefined ? stop['stop_id'].getDisplayText() : '';
            },
            /** 
             * @returns {!Array.<!Object>}
            */
            getStopTimeUpdates() {
                return this.tripUpdate.tripUpdate.stopTimeUpdate.concat([ this.shadowStopTimeUpdate ]);
            },

            /**
             * @param {!String} scheduleRelationship
             */
            setScheduleRelationship(scheduleRelationship) {
                if (this.tripUpdate.tripUpdate.trip.scheduleRelationship !== scheduleRelationship) {
                    this.tripUpdate.tripUpdate.trip.scheduleRelationship = scheduleRelationship;
                    this.mainKey += 1;
                }
            },
            /**
             * @param {!String} tripID
             */
            setTripId(tripID) {
                const trip = this.trips.find(trip => trip['trip_id'].get() === tripID);
                this.tripExists = trip !== undefined;
                this.tripUpdate.tripUpdate.trip.tripId = tripID;
                if (this.tripExists) {
                    this.tripUpdate.tripUpdate.trip.routeId = trip['route_id'].get();
                    this.tripUpdate.tripUpdate.trip.directionId = trip['direction_id'].get();
                    if (this.tripUpdate.tripUpdate.trip.scheduleRelationship === 'ADDED') {
                        this.tripUpdate.tripUpdate.trip.scheduleRelationship = 'SCHEDULED';
                    }
                } else if (this.tripUpdate.tripUpdate.trip.scheduleRelationship !== 'ADDED') {
                    this.tripUpdate.tripUpdate.trip.scheduleRelationship = 'ADDED';
                }
                this.mainKey += 1;
            },

            sortStopTimeUpdates() {
                this.tripUpdate.tripUpdate.stopTimeUpdate.sort((a, b) => {
                    return Number.parseInt(a['stopSequence'], 10) - Number.parseInt(b['stopSequence'], 10);
                });
            }
        }
    };
</script>
