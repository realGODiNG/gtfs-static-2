<template>
    <div id="app">
        <input id="open-input" type="file" @change="loadDataset($event)" />
        <b-navbar id="main-menu" toggleable="lg" type="dark" variant="dark">
            <b-navbar-brand>GTFS Static</b-navbar-brand>
            <b-navbar-toggle target="main-menu-collapse"></b-navbar-toggle>
            <b-collapse id="main-menu-collapse" is-nav>
                <b-navbar-nav>
                    <b-nav-item-dropdown text="Dataset">
                        <b-dropdown-item @click="createDataset()">
                            New ...
                        </b-dropdown-item>
                        <b-dropdown-item id="open-button">
                            Open ...
                        </b-dropdown-item>
                        <b-dropdown-item @click="dataset.save()">
                            Save
                        </b-dropdown-item>
                    </b-nav-item-dropdown>   
                    <b-nav-item-dropdown text="Station">
                        <b-dropdown-item @click="createStation()">
                            New ...
                        </b-dropdown-item>
                        <b-dropdown-item @click="createTable('__stops')">
                            Select ...
                        </b-dropdown-item>
                    </b-nav-item-dropdown>
                    <b-nav-item-dropdown text="Trip">
                        <b-dropdown-item @click="createTrip()">
                            New ...
                        </b-dropdown-item>
                        <b-dropdown-item @click="createTable('__trips')">
                            Select ...
                        </b-dropdown-item>
                    </b-nav-item-dropdown>
                    <b-nav-item-dropdown text="File" v-if="dataset !== null">
                        <b-dropdown-item v-for="file in dataset.files" :key="file.identifier"
                            v-b-tooltip.hover="{ placement: 'right', title: file.description }"
                            @click="createTable(file.identifier)"
                        >
                            Open '{{ file.name }}'
                        </b-dropdown-item>
                    </b-nav-item-dropdown>
                    <b-nav-item id="create-record" @click="table.createRecord()" v-if="table !== null && table.callback === null">
                        Add Record
                    </b-nav-item>
                    <b-nav-item id="create-record" v-else disabled>
                        Add Record
                    </b-nav-item>
                </b-navbar-nav>
                <b-navbar-nav class="ml-auto">
                    <b-nav-item id="dataset-filename" disabled v-if="dataset !== null">
                        <span v-if="table === null">
                            Dataset: '{{ dataset.filename }}'
                        </span>
                        <span v-else>
                            File: '{{ table.file.name }}'
                        </span>
                    </b-nav-item>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>
        <div :key="table.key" v-if="table !== null">
            <b-table id="table"
                :current-page="table.currentPage"
                :fields="table.getFields()"
                :items="table.getRecords()"
                :per-page="table.perPage"
                :sort-compare="table.comparator"
                fixed hover small striped
            >
                <template v-slot:head()="data">
                    <span v-b-tooltip.hover="{ placement: 'bottom', title: data.label }" v-if="data.label.length != 0">
                        {{ table.formator(data.column) }}
                    </span>
                    <span v-else>
                        {{ table.formator(data.column) }}
                    </span>
                </template>
                <template v-slot:cell()="data">
                    <span class="centered" v-if="data.value.record === undefined">
                        <b-icon icon="pen"
                            v-b-tooltip.hover="{ placement: 'top', title: 'Edit record.' }"
                            @click="table.callback(data.item)"
                            v-if="table.callback !== null"
                        />
                        <b-icon icon="trash"
                            v-b-tooltip.hover="{ placement: 'top', title: 'Delete record.' }"
                            @click="table.deleteRecord(data.item)"
                            v-else
                        />
                    </span>
                    <span v-else-if="table.callback !== null">
                        <b-form-input :value="data.value.get()" size="sm" disabled />
                    </span>
                    <span v-else-if="data.value.isChild()">
                        <b-form-select :value="data.value.get()" size="sm" @change="data.value.set($event)">
                            <b-form-select-option :value="''" />
                            <option v-for="parent in data.value.getPossibleParents()" :key="parent.get()">
                                {{ parent.get() }}
                            </option>
                        </b-form-select>
                    </span>
                    <span v-else-if="data.value.isEnumeration()">
                        <b-form-select :value="data.value.get()" size="sm" @change="data.value.set($event)">
                            <option v-for="value in data.value.getEnumerationValues()" :key="value">
                                {{ value }}
                            </option>
                        </b-form-select>
                    </span>
                    <span v-else>
                        <b-form-input
                            :pattern="data.value.fieldType.structure.getInputPattern()"
                            :type="data.value.fieldType.structure.getInputType()"
                            :value="data.value.get()"
                            @change="data.value.set($event)"
                            size="sm"
                        />
                    </span>
                </template>
            </b-table>
            <b-pagination aria-controls="table"
                v-model="table.currentPage"
                :per-page="table.perPage"
                :total-rows="table.getRecords().length"
                align="center"
            />
        </div>
        <div :key="divers.key" v-if="divers !== null">
            <b-card v-for="mockup in divers.mockups" :key="mockup.title" :title="mockup.title">
                <b-table-simple class="mockup-table">
                    <b-tr v-for="row in mockup.table" :key="row.title">
                        <b-td v-for="(element, index) in row.data" :key="row.title + '-element' + index"
                            :colspan="element.colspan"
                            :rowspan="element.rowspan"
                        >
                            <span class="mockup-label">
                                {{ typeof element.label === 'string' ? element.label : '' }}
                            </span>
                            <span v-if="element.action !== null">
                                <br v-if="element.label === null" />
                                <b-icon :icon="element.action.icon"
                                    @click="element.action.callback()"
                                    v-if="element.action.icon !== null"
                                />
                                <b-button
                                    @click="element.action.callback()"
                                    size="sm" type="button" variant="dark"
                                    v-else-if="element.action.text !== null"
                                >
                                    {{ element.action.text }}
                                </b-button>
                                <span :key="divers.calendarKey" v-else-if="element.action.special === 'trips.calendar'">
                                    <v-date-picker :attributes="divers.calendar"
                                        :columns="$screens({ default: 1, lg: 4 })"
                                        :rows="$screens({ default: 1, lg: 1 })"
                                        v-model="pickerDate"
                                        is-expanded is-inline
                                    />
                                </span>
                                <span :key="divers.stopsKey" v-else-if="element.action.special === 'trips.stop_times'">
                                    <SimpleTable :fields="divers.stopFields" :items="divers.stopItems" :move="divers.stopMove" />
                                </span>
                                <span :key="divers.frequenciesKey" v-else-if="element.action.special === 'trips.frequencies'">
                                    <SimpleTable :fields="divers.frequencyFields" :items="divers.frequencyItems" :move="null" />
                                </span>
                                <span :key="divers.stationKey" v-else-if="element.action.special === 'stops.station'">
                                    <SimpleTree
                                        :fields="divers.stationFields"
                                        :handler="divers.stationHandler"
                                        :root="divers.tree"
                                    />
                                </span>
                                <span :key="divers.mapKey" v-else-if="element.action.special === 'stops.map'">
                                    <SimpleMap :data="divers.tree.flat()" :refreshParent="divers.stationRefresh" />
                                </span>
                                <span :key="divers.transfersKey" v-else-if="element.action.special === 'stops.transfers'">
                                    <SimpleTable :fields="divers.transferFields" :items="divers.transferItems" :move="null" />
                                </span>
                                <span :key="divers.pathwaysKey" v-else-if="element.action.special === 'stops.pathways'">
                                    <SimpleTable :fields="divers.pathwayFields" :items="divers.pathwayItems" :move="null" />
                                </span>
                            </span>
                            <span v-else-if="element.entry.isChild()">
                                <b-form-select class="mockup-input" :value="element.entry.get()" @change="divers.set(element.entry, $event)" size="sm">
                                    <b-form-select-option :value="''" />
                                    <option v-for="parent in element.entry.getPossibleParents()" :key="parent.get()">
                                        {{ parent.get() }}
                                    </option>
                                </b-form-select>
                            </span>
                            <span v-else-if="element.entry.isEnumeration()">
                                <b-form-select class="mockup-input" :value="element.entry.get()" @change="divers.set(element.entry, $event)" size="sm">
                                    <option v-for="value in element.entry.getEnumerationValues()" :key="value">
                                        {{ value }}
                                    </option>
                                </b-form-select>
                            </span>
                            <span v-else>
                                <b-form-input class="mockup-input"
                                    :pattern="element.entry.fieldType.structure.getInputPattern()"
                                    :type="element.entry.fieldType.structure.getInputType()"
                                    :value="element.entry.get()"
                                    @change="divers.set(element.entry, $event)"
                                    size="sm"
                                />
                            </span>
                        </b-td>
                    </b-tr>
                </b-table-simple>
            </b-card>
        </div>
        <Texter :wrapper="texterWrapper" @close="closeTexter()" v-if="texterWrapper !== null" />
    </div>
</template>

<script>
    import SimpleMap from './components/SimpleMap.vue'
    import SimpleTable from './components/SimpleTable.vue'
    import SimpleTree from './components/SimpleTree.vue'
    import Texter from './components/Texter.vue'

    import $ from 'jquery'
    import JSZip from 'jszip'
    import saveAs from 'file-saver'

    /**
     * @returns {!String}
     */
    function getXML() {
        return "<?xml version='1.0' encoding='UTF-8'?><gtfs_static><structures><structure><identifier>Color</identifier><name>Color</name><description>A color encoded as a six-digit hexadecimal number. Refer to https://htmlcolorcodes.com to generate a valid value (the leading \"#\" is not included). Example: FFFFFF for white, 000000 for black or 0039A6 for the A,C,E lines in NYMTA.</description></structure><structure><identifier>CurrencyCode</identifier><name>Currency Code</name><description>An ISO 4217 alphabetical currency code. For the list of current currency, refer to https://en.wikipedia.org/wiki/ISO_4217#Active_codes. Example: CAD for Canadian dollars, EUR for euros or JPY for Japanese yen.</description></structure><structure><identifier>Date</identifier><name>Date</name><description>Service day in the YYYYMMDD format. Since time within a service day can be above 24:00:00, a service day often contains information for the subsequent day(s). Example: 20180913 for September 13th, 2018.</description></structure><structure><identifier>Email</identifier><name>Email</name><description>An email address. Example: example@example.com</description></structure><structure><identifier>Enum</identifier><name>Enum</name><description>An option from a set of predefined constants defined in the \"Description\" column. Example: The route_type field contains a 0 for tram, a 1 for subway...</description></structure><structure><identifier>Id</identifier><name>Id</name><description>An ID field value is an internal ID, not intended to be shown to riders, and is a sequence of any UTF-8 characters. Using only printable ASCII characters is recommended. IDs defined in one.txt file are often referenced in another.txt file. Example: The stop_id field in stops.txt is a ID. The stop_id field in stop_times.txt is an ID referencing stops.stop_id.</description></structure><structure><identifier>LanguageCode</identifier><name>Language Code</name><description>An IETF BCP 47 language code. For an introduction to IETF BCP 47, refer to http://www.rfc-editor.org/rfc/bcp/bcp47.txt and http://www.w3.org/International/articles/language-tags/. Example: en for English, en-US for American English or de for German.</description></structure><structure><identifier>Latitude</identifier><name>Latitude</name><description>WGS84 latitude in decimal degrees. The value must be greater than or equal to -90.0 and less than or equal to 90.0. Example: 41.890169 for the Colosseum in Rome.</description></structure><structure><identifier>Longitude</identifier><name>Longitude</name><description>WGS84 longitude in decimal degrees. The value must be greater than or equal to -180.0 and less than or equal to 180.0. Example: 12.492269 for the Colosseum in Rome.</description></structure><structure><identifier>NonNegativeFloat</identifier><name>Non-negative Float</name><description>A floating point number greater than or equal to 0.</description></structure><structure><identifier>NonNegativeInteger</identifier><name>Non-negative Integer</name><description>A integer greater than or equal to 0.</description></structure><structure><identifier>PhoneNumber</identifier><name>Phone Number</name><description>A phone number.</description></structure><structure><identifier>Time</identifier><name>Time</name><description>Time in the HH:MM:SS format (H:MM:SS is also accepted). The time is measured from \"noon minus 12h\" of the service day (effectively midnight except for days on which daylight savings time changes occur. For more information, see the guidelines article). For times occurring after midnight, enter the time as a value greater than 24:00:00 in HH:MM:SS local time for the day on which the trip schedule begins. Example: 14:30:00 for 2:30PM or 25:35:00 for 1:35AM on the next day.</description></structure><structure><identifier>Text</identifier><name>Text</name><description>A string of UTF-8 characters, which is aimed to be displayed and which must therefore be human readable.</description></structure><structure><identifier>Timezone</identifier><name>Timezone</name><description>TZ timezone from the https://www.iana.org/time-zones. Timezone names never contain the space character but may contain an underscore. Refer to http://en.wikipedia.org/wiki/List_of_tz_zones for a list of valid values. Example: Asia/Tokyo, America/Los_Angeles or Africa/Cairo.</description></structure><structure><identifier>Url</identifier><name>Url</name><description>A fully qualified URL that includes http:// or https://, and any special characters in the URL must be correctly escaped. See the following http://www.w3.org/Addressing/URL/4_URI_Recommentations.html for a description of how to create fully qualified URL values.</description></structure><structure><identifier>PositiveInteger</identifier><name>Positive Integer</name><description/></structure><structure><identifier>NonNullInteger</identifier><name>Non-null Integer</name><description/></structure><structure><identifier>PositiveFloat</identifier><name>Positive Float</name><description/></structure><structure><identifier>Float</identifier><name>Float</name><description/></structure><structure><identifier>Translation</identifier><name>Translation</name><description/></structure></structures><enumerations><enumeration><name>Type</name><reference>stops.location_type.0</reference><map>0.Stop/Platform</map><map>1.Station</map><map>2.Entrance/Exit</map><map>3.Generic Node</map><map>4.Boarding Area</map><blank>0</blank></enumeration><enumeration><name>Information</name><reference>stops.wheelchair_boarding.0</reference><map>0.0</map><map>1.1</map><map>2.2</map><blank>0</blank></enumeration><enumeration><name>Type</name><reference>routes.route_type.0</reference><map>.</map><map>0.Tram</map><map>1.Subway</map><map>2.Rail</map><map>3.Bus</map><map>4.Ferry</map><map>5.Cable Tram</map><map>6.Aerial Lift</map><map>7.Funicular</map><map>11.Trolleybus</map><map>12.Monorail</map><blank/></enumeration><enumeration><name>Direction</name><reference>trips.direction_id.0</reference><map>.</map><map>0.One Direction</map><map>1.Opposite Direction</map><blank/></enumeration><enumeration><name>Accommodation</name><reference>trips.wheelchair_accessible.0</reference><reference>trips.bikes_allowed.0</reference><map>0.No Information</map><map>1.At least one Accommodation</map><map>2.No Accommodation</map><blank>0</blank></enumeration><enumeration><name>Method</name><reference>stop_times.pickup_type.0</reference><reference>stop_times.drop_off_type.0</reference><map>0.No Regularly sheduled</map><map>1.Not available</map><map>2.Must phone Agency</map><map>3.Must coordinate with Driver</map><blank>0</blank></enumeration><enumeration><name>Rule</name><reference>stop_times.timepoint.0</reference><map>0.Approximation</map><map>1.Exact Value</map><blank>1</blank></enumeration><enumeration><name>Boolean</name><reference>calendar.monday.0</reference><reference>calendar.tuesday.0</reference><reference>calendar.wednesday.0</reference><reference>calendar.thursday.0</reference><reference>calendar.friday.0</reference><reference>calendar.saturday.0</reference><reference>calendar.sunday.0</reference><reference>pathways.is_bidirectional.0</reference><reference>attributions.is_producer.0</reference><reference>attributions.is_operator.0</reference><reference>attributions.is_authority.0</reference><map>0.false</map><map>1.true</map><blank>0</blank></enumeration><enumeration><name>Type</name><reference>calendar_dates.exception_type.0</reference><map>.</map><map>1.Has been added</map><map>2.Has been removed</map><blank/></enumeration><enumeration><name>Method</name><reference>fare_attributes.payment_method.0</reference><map>.</map><map>0.On Board</map><map>1.Before Boarding</map><blank/></enumeration><enumeration><name>Number</name><reference>fare_attributes.transfers.0</reference><map>.Unlimited Transfers</map><map>0.No transfers</map><map>1.May transfer once</map><map>2.May transfer twice</map><blank>0</blank></enumeration><enumeration><name>Rule</name><reference>frequencies.exact_times.0</reference><map>0.Frequency-based</map><map>1.Schedule-based</map><blank>0</blank></enumeration><enumeration><name>Type</name><reference>transfers.transfer_type.0</reference><map>0.Recommendeds</map><map>1.Timed</map><map>2.Requires minimum Time</map><map>3.Impossible</map><blank>0</blank></enumeration><enumeration><name>Type</name><reference>pathways.pathway_mode.0</reference><map>.</map><map>1.Walkway</map><map>2.Stairs</map><map>3.Sidewalk/Travelator</map><map>4.Escalator</map><map>5.Elevator</map><map>6.Fare-/Payment-Gate</map><map>7.Exit Gate</map><blank/></enumeration><enumeration><name>Name</name><reference>translations.table_name.0</reference><map>.</map><map>agency.Agency</map><map>stops.Stops</map><map>routes.Routes</map><map>trips.Trips</map><map>stop_times.Stop Times</map><map>feed_info.Feed Info</map><map>pathways.Pathways</map><map>levels.Levels</map><blank/></enumeration><enumeration><name>Method</name><reference>routes.continuous_pickup.0</reference><reference>stop_times.continuous_pickup.0</reference><map>.</map><map>0.Continuous Stopping Pickup</map><map>1.No Continuous Stopping Pickup</map><map>2.Must phone Agency</map><map>3.Must coordinate with Driver</map><blank/></enumeration><enumeration><name>Method</name><reference>routes.continuous_drop_off.0</reference><reference>stop_times.continuous_drop_off.0</reference><map>.</map><map>0.Continuous Stopping Drop Off</map><map>1.No Continuous Stopping Drop Off</map><map>2.Must phone Agency</map><map>3.Must coordinate with Driver</map><blank/></enumeration></enumerations><files><file><filename>agency.txt</filename><name>Agency</name><required>required</required><description>Transit agencies with service represented in this dataset.</description><fields><field><identifier>agency_id</identifier><name>Agency Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>conditionally</required><description>Identifies a transit brandwhich is often synonymous with a transit agency. Note that in some cases, such as when a single agency operates multiple separate services, agencies and brands are distinct. This document uses the term \"agency\" in place of \"brand\". A dataset may contain data from multiple agencies. This field is required when the dataset contains data for multiple transit agencies, otherwise it is optional.</description></field><field><identifier>agency_name</identifier><name>Agency Name</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>required</required><description>Full name of the transit agency.</description></field><field><identifier>agency_url</identifier><name>Agency Url</name><structures><structure><identifier>Url</identifier><reference/></structure></structures><required>required</required><description>URL of the transit agency.</description></field><field><identifier>agency_timezone</identifier><name>Agency Timezone</name><structures><structure><identifier>Timezone</identifier><reference/></structure></structures><required>required</required><description>Timezone where the transit agency is located. If multiple agencies are specified in the dataset, each must have the same agency_timezone.</description></field><field><identifier>agency_lang</identifier><name>Agency Lang</name><structures><structure><identifier>LanguageCode</identifier><reference/></structure></structures><required>optional</required><description>Primary language used by this transit agency. This field helps GTFS consumers choose capitalization rules and other language-specific settings for the dataset.</description></field><field><identifier>agency_phone</identifier><name>Agency Phone</name><structures><structure><identifier>PhoneNumber</identifier><reference/></structure></structures><required>optional</required><description>A voice telephone number for the specified agency. This field is a string value that presents the telephone number as typical for the agency's service area. It can and should contain punctuation marks to group the digits of the number. Dialable text (for example, TriMet's \"503-238-RIDE\") is permitted, but the field must not contain any other descriptive text.</description></field><field><identifier>agency_fare_url</identifier><name>Agency Fare Url</name><structures><structure><identifier>Url</identifier><reference/></structure></structures><required>optional</required><description>URL of a web page that allows a rider to purchase tickets or other fare instruments for that agency online.</description></field><field><identifier>agency_email</identifier><name>Agency Email</name><structures><structure><identifier>Email</identifier><reference/></structure></structures><required>optional</required><description>Email address actively monitored by the agency’s customer service department. This email address should be a direct contact point where transit riders can reach a customer service representative at the agency.</description></field></fields></file><file><filename>stops.txt</filename><name>Stops</name><required>required</required><description>Stops where vehicles pick up or drop off riders. Also defines stations and station entrances.</description><fields><field><identifier>stop_id</identifier><name>Stop Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>required</required><description>Identifies a stop, station, or station entrance. The term \"station entrance\" refers to both station entrances and station exits. Stops, stations or station entrances are collectively referred to as locations. Multiple routes may use the same stop.</description></field><field><identifier>stop_code</identifier><name>Stop Code</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>optional</required><description>Short text or a number that identifies the location for riders. These codes are often used in phone-based transit information systems or printed on signage to make it easier for riders to get information for a particular location. The stop_code can be the same as stop_id if it is public facing. This field should be left empty for locations without a code presented to riders.</description></field><field><identifier>stop_name</identifier><name>Stop Name</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>conditionally</required><description>Name of the location. Use a name that people will understand in the local and tourist vernacular. When the location is a boarding area (location_type=4), the stop_name should contains the name of the boarding area as displayed by the agency. It could be just one letter (like on some European intercity railway stations), or text like “Wheelchair boarding area” (NYC’s Subway) or “Head of short trains” (Paris’ RER). Conditionally Required: * Required for locations which are stops (location_type=0), stations (location_type=1) or entrances/exits (location_type=2). * Optional for locations which are generic nodes (location_type=3) or boarding areas (location_type=4).</description></field><field><identifier>stop_desc</identifier><name>Stop Desc</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>optional</required><description>Description of the location that provides useful, quality information. Do not simply duplicate the name of the location.</description></field><field><identifier>stop_lat</identifier><name>Stop Lat</name><structures><structure><identifier>Latitude</identifier><reference/></structure></structures><required>conditionally</required><description>Latitude of the location. Conditionally Required: * Required for locations which are stops (location_type=0), stations (location_type=1) or entrances/exits (location_type=2). * Optional for locations which are generic nodes (location_type=3) or boarding areas (location_type=4).</description></field><field><identifier>stop_lon</identifier><name>Stop Lon</name><structures><structure><identifier>Longitude</identifier><reference/></structure></structures><required>conditionally</required><description>Longitude of the location. Conditionally Required: * Required for locations which are stops (location_type=0), stations (location_type=1) or entrances/exits (location_type=2). * Optional for locations which are generic nodes (location_type=3) or boarding areas (location_type=4).</description></field><field><identifier>zone_id</identifier><name>Zone Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>conditionally</required><description>Identifies the fare zone for a stop. This field is required if providing fare information using fare_rules.txt, otherwise it is optional. If this record represents a station or station entrance, the zone_id is ignored.</description></field><field><identifier>stop_url</identifier><name>Stop Url</name><structures><structure><identifier>Url</identifier><reference/></structure></structures><required>optional</required><description>URL of a web page about the location. This should be different from the agency.agency_url and the routes.route_url field values.</description></field><field><identifier>location_type</identifier><name>Location Type</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Type of the location: * 0 (or blank): Stop (or Platform). A location where passengers board or disembark from a transit vehicle. Is called a platform when defined within a parent_station. * 1: Station. A physical structure or area that contains one or more platform. * 2: Entrance/Exit. A location where passengers can enter or exit a station from the street. If an entrance/exit belongs to multiple stations, it can be linked by pathways to both, but the data provider must pick one of them as parent. * 3: Generic Node. A location within a station, not matching any other location_type, which can be used to link together pathways define in pathways.txt. * 4: Boarding Area. A specific location on a platform, where passengers can board and/or alight vehicles.</description></field><field><identifier>parent_station</identifier><name>Parent Station</name><structures><structure><identifier>Id</identifier><reference>stops.stop_id</reference></structure></structures><required>conditionally</required><description>Defines hierarchy between the different locations defined in stops.txt. It contains the ID of the parent location, as followed: * Stop/platform (location_type=0): the parent_station field contains the ID of a station. * Station (location_type=1): this field must be empty. * Entrance/exit (location_type=2) or generic node (location_type=3): the parent_station field contains the ID of a station (location_type=1) * Boarding Area (location_type=4): the parent_station field contains ID of a platform. Conditionally Required: * Required for locations which are entrances (location_type=2), generic nodes (location_type=3) or boarding areas (location_type=4). * Optional for stops/platforms (location_type=0). * Forbidden for stations (location_type=1).</description></field><field><identifier>stop_timezone</identifier><name>Stop Timezone</name><structures><structure><identifier>Timezone</identifier><reference/></structure></structures><required>optional</required><description>Timezone of the location. If the location has a parent station, it inherits the parent station’s timezone instead of applying its own. Stations and parentless stops with empty stop_timezone inherit the timezone specified by agency.agency_timezone. If stop_timezone values are provided, the times in stop_times.txt should be entered as the time since midnight in the timezone specified by agency.agency_timezone. This ensures that the time values in a trip always increase over the course of a trip, regardless of which timezones the trip crosses.</description></field><field><identifier>wheelchair_boarding</identifier><name>Wheelchair Boarding</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates whether wheelchair boardings are possible from the location. Valid options are: For parentless stops: 0 or empty - No accessibility information for the stop. 1 - Some vehicles at this stop can be boarded by a rider in a wheelchair. 2 - Wheelchair boarding is not possible at this stop. For child stops: 0 or empty - Stop will inherit its wheelchair_boarding behavior from the parent station, if specified in the parent. 1 - There exists some accessible path from outside the station to the specific stop/platform. 2 - There exists no accessible path from outside the station to the specific stop/platform. For station entrances/exits: 0 or empty - Station entrance will inherit its wheelchair_boarding behavior from the parent station, if specified for the parent. 1 - Station entrance is wheelchair accessible. 2 - No accessible path from station entrance to stops/platforms.</description></field><field><identifier>level_id</identifier><name>Level Id</name><structures><structure><identifier>Id</identifier><reference>levels.level_id</reference></structure></structures><required>optional</required><description>Level of the location. The same level can be used by multiple unlinked stations.</description></field><field><identifier>platform_code</identifier><name>Platform Code</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>optional</required><description>Platform identifier for a platform stop (a stop belonging to a station). This should be just the platform identifier (eg. \"G\" or \"3\"). Words like “platform” or \"track\" (or the feed’s language-specific equivalent) should not be included. This allows feed consumers to more easily internationalize and localize the platform identifier into other languages.</description></field></fields></file><file><filename>routes.txt</filename><name>Routes</name><required>required</required><description>Transit routes. A route is a group of trips that are displayed to riders as a single service.</description><fields><field><identifier>route_id</identifier><name>Route Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>required</required><description>Identifies a route.</description></field><field><identifier>agency_id</identifier><name>Agency Id</name><structures><structure><identifier>Id</identifier><reference>agency.agency_id</reference></structure></structures><required>conditionally</required><description>Agency for the specified route. This field is required when the dataset provides data for routes from more than one agency in agency.txt, otherwise it is optional.</description></field><field><identifier>route_short_name</identifier><name>Route Short Name</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>conditionally</required><description>Short name of a route. This will often be a short, abstract identifier like \"32\", \"100X\", or \"Green\" that riders use to identify a route, but which doesn't give any indication of what places the route serves. Either route_short_name or route_long_name must be specified, or potentially both if appropriate.</description></field><field><identifier>route_long_name</identifier><name>Route Long Name</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>conditionally</required><description>Full name of a route. This name is generally more descriptive than the route_short_name and often includes the route's destination or stop. Either route_short_name or route_long_name must be specified, or potentially both if appropriate.</description></field><field><identifier>route_desc</identifier><name>Route Desc</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>optional</required><description>Description of a route that provides useful, quality information. Do not simply duplicate the name of the route. Example: \"A\" trains operate between Inwood-207 St, Manhattan and Far Rockaway-Mott Avenue, Queens at all times. Also from about 6AM until about midnight, additional \"A\" trains operate between Inwood-207 St and Lefferts Boulevard (trains typically alternate between Lefferts Blvd and Far Rockaway).</description></field><field><identifier>route_type</identifier><name>Route Type</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Indicates the type of transportation used on a route. Valid options are: 0 - Tram, Streetcar, Light rail. Any light rail or street level system within a metropolitan area. 1 - Subway, Metro. Any underground rail system within a metropolitan area. 2 - Rail. Used for intercity or long-distance travel. 3 - Bus. Used for short- and long-distance bus routes. 4 - Ferry. Used for short- and long-distance boat service. 5 - Cable tram. Used for street-level rail cars where the cable runs beneath the vehicle, e.g., cable car in San Francisco. 6 - Aerial lift, suspended cable car (e.g., gondola lift, aerial tramway). Cable transport where cabins, cars, gondolas or open chairs are suspended by means of one or more cables. 7 - Funicular. Any rail system designed for steep inclines. 11 - Trolleybus. Electric buses that draw power from overhead wires using poles. 12 - Monorail. Railway in which the track consists of a single rail or a beam.</description></field><field><identifier>route_url</identifier><name>Route Url</name><structures><structure><identifier>Url</identifier><reference/></structure></structures><required>optional</required><description>URL of a web page about the particular route. Should be different from the agency.agency_url value.</description></field><field><identifier>route_color</identifier><name>Route Color</name><structures><structure><identifier>Color</identifier><reference/></structure></structures><required>optional</required><description>Route color designation that matches public facing material. Defaults to white (FFFFFF) when omitted or left empty. The color difference between route_color and route_text_color should provide sufficient contrast when viewed on a black and white screen.</description></field><field><identifier>route_text_color</identifier><name>Route Text Color</name><structures><structure><identifier>Color</identifier><reference/></structure></structures><required>optional</required><description>Legible color to use for text drawn against a background of route_color. Defaults to black (000000) when omitted or left empty. The color difference between route_color and route_text_color should provide sufficient contrast when viewed on a black and white screen.</description></field><field><identifier>route_sort_order</identifier><name>Route Sort Order</name><structures><structure><identifier>NonNegativeInteger</identifier><reference/></structure></structures><required>optional</required><description>Orders the routes in a way which is ideal for presentation to customers. Routes with smaller route_sort_order values should be displayed first.</description></field><field><identifier>continuous_pickup</identifier><name>Continuous Pickup</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates whether a rider can board the transit vehicle anywhere along the vehicle’s travel path. The path is described by shapes.txt on every trip of the route. Valid options are: 0 - Continuous stopping pickup. 1 or empty - No continuous stopping pickup. 2 - Must phone an agency to arrange continuous stopping pickup. 3 - Must coordinate with a driver to arrange continuous stopping pickup. The default continuous pickup behavior defined in routes.txt can be overridden in stop_times.txt.</description></field><field><identifier>continuous_drop_off</identifier><name>Continuous Drop Off</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates whether a rider can alight from the transit vehicle at any point along the vehicle’s travel path. The path is described by shapes.txt on every trip of the route. Valid options are: 0- Continuous stopping drop-off. 1 or empty - No continuous stopping drop-off. 2 - Must phone an agency to arrange continuous stopping drop-off. 3 - Must coordinate with a driver to arrange continuous stopping drop-off. The default continuous drop-off behavior defined in routes.txt can be overridden in stop_times.txt.</description></field></fields></file><file><filename>trips.txt</filename><name>Trips</name><required>required</required><description>Trips for each route. A trip is a sequence of two or more stops that occur during a specific time period.</description><fields><field><identifier>route_id</identifier><name>Route Id</name><structures><structure><identifier>Id</identifier><reference>routes.route_id</reference></structure></structures><required>required</required><description>Identifies a route.</description></field><field><identifier>service_id</identifier><name>Service Id</name><structures><structure><identifier>Id</identifier><reference>calendar.service_id</reference></structure><structure><identifier>Id</identifier><reference>calendar_dates.service_id</reference></structure></structures><required>required</required><description>Identifies a set of dates when service is available for one or more routes.</description></field><field><identifier>trip_id</identifier><name>Trip Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>required</required><description>Identifies a trip.</description></field><field><identifier>trip_headsign</identifier><name>Trip Headsign</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>optional</required><description>Text that appears on signage identifying the trip's destination to riders. Use this field to distinguish between different patterns of service on the same route. If the headsign changes during a trip, trip_headsign can be overridden by specifying values for the stop_times.stop_headsign.</description></field><field><identifier>trip_short_name</identifier><name>Trip Short Name</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>optional</required><description>Public facing text used to identify the trip to riders, for instance, to identify train numbers for commuter rail trips. If riders do not commonly rely on trip names, leave this field empty. A trip_short_name value, if provided, should uniquely identify a trip within a service day; it should not be used for destination names or limited/express designations.</description></field><field><identifier>direction_id</identifier><name>Direction Id</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates the direction of travel for a trip. This field is not used in routing; it provides a way to separate trips by direction when publishing time tables. Valid options are: 0 - Travel in one direction (e.g. outbound travel). 1 - Travel in the opposite direction (e.g. inbound travel). Example: The trip_headsign and direction_id fields could be used together to assign a name to travel in each direction for a set of trips. A trips.txt file could contain these records for use in time tables: trip_id,...,trip_headsign,direction_id 1234,...,Airport,0 1505,...,Downtown,1</description></field><field><identifier>block_id</identifier><name>Block Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>optional</required><description>Identifies the block to which the trip belongs. A block consists of a single trip or many sequential trips made using the same vehicle, defined by shared service days and block_id. A block_id can have trips with different service days, making distinct blocks. See the example below</description></field><field><identifier>shape_id</identifier><name>Shape Id</name><structures><structure><identifier>Id</identifier><reference>shapes.shape_id</reference></structure></structures><required>optional</required><description>Identifies a geospatial shape describing the vehicle travel path for a trip.</description></field><field><identifier>wheelchair_accessible</identifier><name>Wheelchair Accessible</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates wheelchair accessibility. Valid options are: 0 or empty - No accessibility information for the trip. 1 - Vehicle being used on this particular trip can accommodate at least one rider in a wheelchair. 2 - No riders in wheelchairs can be accommodated on this trip.</description></field><field><identifier>bikes_allowed</identifier><name>Bikes Allowed</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates whether bikes are allowed. Valid options are: 0 or empty - No bike information for the trip. 1 - Vehicle being used on this particular trip can accommodate at least one bicycle. 2 - No bicycles are allowed on this trip.</description></field></fields></file><file><filename>stop_times.txt</filename><name>Stop Times</name><required>required</required><description>Times that a vehicle arrives at and departs from stops for each trip.</description><fields><field><identifier>trip_id</identifier><name>Trip Id</name><structures><structure><identifier>Id</identifier><reference>trips.trip_id</reference></structure></structures><required>required</required><description>Identifies a trip.</description></field><field><identifier>arrival_time</identifier><name>Arrival Time</name><structures><structure><identifier>Time</identifier><reference/></structure></structures><required>conditionally</required><description>Arrival time at a specific stop for a specific trip on a route. If there are not separate times for arrival and departure at a stop, enter the same value for arrival_time and departure_time. For times occurring after midnight on the service day, enter the time as a value greater than 24:00:00 in HH:MM:SS local time for the day on which the trip schedule begins. Scheduled stops where the vehicle strictly adheres to the specified arrival and departure times are timepoints. If this stop is not a timepoint, it is recommended to provide an estimated or interpolated time. If this is not available, arrival_time can be left empty. Further, indicate that interpolated times are provided with timepoint = 0. If interpolated times are indicated with timepoint = 0, then time points must be indicated with timepoint = 1. Provide arrival times for all stops that are time points. An arrival time must be specified for the first and the last stop in a trip.</description></field><field><identifier>departure_time</identifier><name>Departure Time</name><structures><structure><identifier>Time</identifier><reference/></structure></structures><required>conditionally</required><description>Departure time from a specific stop for a specific trip on a route. For times occurring after midnight on the service day, enter the time as a value greater than 24:00:00 in HH:MM:SS local time for the day on which the trip schedule begins. If there are not separate times for arrival and departure at a stop, enter the same value for arrival_time and departure_time. See the arrival_time description for more details about using timepoints correctly. The departure_time field should specify time values whenever possible, including non-binding estimated or interpolated times between timepoints.</description></field><field><identifier>stop_id</identifier><name>Stop Id</name><structures><structure><identifier>Id</identifier><reference>stops.stop_id</reference></structure></structures><required>required</required><description>Identifies the serviced stop. All stops serviced during a trip must have a record in stop_times.txt. Referenced locations must be stops, not stations or station entrances. A stop may be serviced multiple times in the same trip, and multiple trips and routes may service the same stop.</description></field><field><identifier>stop_sequence</identifier><name>Stop Sequence</name><structures><structure><identifier>NonNegativeInteger</identifier><reference/></structure></structures><required>required</required><description>Order of stops for a particular trip. The values must increase along the trip but do not need to be consecutive. Example: The first location on the trip could have a stop_sequence = 1, the second location on the trip could have a stop_sequence = 23, the third location could have a stop_sequence = 40, and so on.</description></field><field><identifier>stop_headsign</identifier><name>Stop Headsign</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>optional</required><description>Text that appears on signage identifying the trip's destination to riders. This field overrides the default trips.trip_headsign when the headsign changes between stops. If the headsign is displayed for an entire trip, use trips.trip_headsign instead. A stop_headsign value specified for one stop_time does not apply to subsequent stop_time s in the same trip. If you want to override the trip_headsign for multiple stop_time s in the same trip, the stop_headsign value must be repeated in each stop_time row.</description></field><field><identifier>pickup_type</identifier><name>Pickup Type</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates pickup method. Valid options are: 0 or empty - Regularly scheduled pickup. 1 - No pickup available. 2 - Must phone agency to arrange pickup. 3 - Must coordinate with driver to arrange pickup.</description></field><field><identifier>drop_off_type</identifier><name>Drop Off Type</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates drop off method. Valid options are: 0 or empty - Regularly scheduled drop off. 1 - No drop off available. 2 - Must phone agency to arrange drop off. 3 - Must coordinate with driver to arrange drop off.</description></field><field><identifier>continuous_pickup</identifier><name>Continuous Pickup</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates whether a rider can board the transit vehicle anywhere along the vehicle’s travel path. The path is described by shapes.txt on every trip of the route. Valid options are: 0 - Continuous stopping pickup. 1 or empty - No continuous stopping pickup. 2 - Must phone an agency to arrange continuous stopping pickup. 3 - Must coordinate with a driver to arrange continuous stopping pickup. The default continuous pickup behavior defined in routes.txt can be overridden in stop_times.txt.</description></field><field><identifier>continuous_drop_off</identifier><name>Continuous Drop Off</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates whether a rider can alight from the transit vehicle at any point along the vehicle’s travel path. The path is described by shapes.txt on every trip of the route. Valid options are: 0- Continuous stopping drop-off. 1 or empty - No continuous stopping drop-off. 2 - Must phone an agency to arrange continuous stopping drop-off. 3 - Must coordinate with a driver to arrange continuous stopping drop-off. The default continuous drop-off behavior defined in routes.txt can be overridden in stop_times.txt.</description></field><field><identifier>shape_dist_traveled</identifier><name>Shape Dist Traveled</name><structures><structure><identifier>NonNegativeFloat</identifier><reference/></structure></structures><required>optional</required><description>Actual distance traveled along the associated shape, from the first stop to the stop specified in this record. This field specifies how much of the shape to draw between any two stops during a trip. Must be in the same units used in shapes.txt. Values used for shape_dist_traveled must increase along with stop_sequence; they cannot be used to show reverse travel along a route. Example: If a bus travels a distance of 5.25 kilometers from the start of the shape to the stop, shape_dist_traveled = 5.25.</description></field><field><identifier>timepoint</identifier><name>Timepoint</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates if arrival and departure times for a stop are strictly adhered to by the vehicle or if they are instead approximate and/or interpolated times. This field allows a GTFS producer to provide interpolated stop-times, while indicating that the times are approximate. Valid options are: 0 - Times are considered approximate. 1 or empty - Times are considered exact.</description></field></fields></file><file><filename>calendar.txt</filename><name>Calendar</name><required>conditionally</required><description>Service dates specified using a weekly schedule with start and end dates. This file is required unless all dates of service are defined in calendar_dates.txt.</description><fields><field><identifier>service_id</identifier><name>Service Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>required</required><description>Uniquely identifies a set of dates when service is available for one or more routes. Each service_id value can appear at most once in a calendar.txt file.</description></field><field><identifier>monday</identifier><name>Monday</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Indicates whether the service operates on all Mondays in the date range specified by the start_date and end_date fields. Note that exceptions for particular dates may be listed in calendar_dates.txt. Valid options are: 1 - Service is available for all Mondays in the date range. 0 - Service is not available for Mondays in the date range.</description></field><field><identifier>tuesday</identifier><name>Tuesday</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Functions in the same way as monday except applies to Tuesdays</description></field><field><identifier>wednesday</identifier><name>Wednesday</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Functions in the same way as monday except applies to Wednesdays</description></field><field><identifier>thursday</identifier><name>Thursday</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Functions in the same way as monday except applies to Thursdays</description></field><field><identifier>friday</identifier><name>Friday</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Functions in the same way as monday except applies to Fridays</description></field><field><identifier>saturday</identifier><name>Saturday</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Functions in the same way as monday except applies to Saturdays.</description></field><field><identifier>sunday</identifier><name>Sunday</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Functions in the same way as monday except applies to Sundays.</description></field><field><identifier>start_date</identifier><name>Start Date</name><structures><structure><identifier>Date</identifier><reference/></structure></structures><required>required</required><description>Start service day for the service interval.</description></field><field><identifier>end_date</identifier><name>End Date</name><structures><structure><identifier>Date</identifier><reference/></structure></structures><required>required</required><description>End service day for the service interval. This service day is included in the interval.</description></field></fields></file><file><filename>calendar_dates.txt</filename><name>Calendar Dates</name><required>conditionally</required><description>Exceptions for the services defined in the calendar.txt. If calendar.txt is omitted, then calendar_dates.txt is required and must contain all dates of service.</description><fields><field><identifier>service_id</identifier><name>Service Id</name><structures><structure><identifier>Id</identifier><reference>calendar.service_id</reference></structure><structure><identifier>Id</identifier><reference/></structure></structures><required>required</required><description>Identifies a set of dates when a service exception occurs for one or more routes. Each (service_id, date) pair can only appear once in calendar_dates.txt if using calendar.txt and calendar_dates.txt in conjunction. If a service_id value appears in both calendar.txt and calendar_dates.txt, the information in calendar_dates.txt modifies the service information specified in calendar.txt.</description></field><field><identifier>date</identifier><name>Date</name><structures><structure><identifier>Date</identifier><reference/></structure></structures><required>required</required><description>Date when service exception occurs.</description></field><field><identifier>exception_type</identifier><name>Exception Type</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Indicates whether service is available on the date specified in the date field. Valid options are: 1 - Service has been added for the specified date. 2 - Service has been removed for the specified date. Example: Suppose a route has one set of trips available on holidays and another set of trips available on all other days. One service_id could correspond to the regular service schedule and another service_id could correspond to the holiday schedule. For a particular holiday, the calendar_dates.txt file could be used to add the holiday to the holiday service_id and to remove the holiday from the regular service_id schedule.</description></field></fields></file><file><filename>fare_attributes.txt</filename><name>Fare Attributes</name><required>optional</required><description>Fare information for a transit agency's routes.</description><fields><field><identifier>fare_id</identifier><name>Fare Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>required</required><description>Identifies a fare class.</description></field><field><identifier>price</identifier><name>Price</name><structures><structure><identifier>NonNegativeFloat</identifier><reference/></structure></structures><required>required</required><description>Fare price, in the unit specified by currency_type.</description></field><field><identifier>currency_type</identifier><name>Currency Type</name><structures><structure><identifier>CurrencyCode</identifier><reference/></structure></structures><required>required</required><description>Currency used to pay the fare.</description></field><field><identifier>payment_method</identifier><name>Payment Method</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Indicates when the fare must be paid. Valid options are: 0 - Fare is paid on board. 1 - Fare must be paid before boarding.</description></field><field><identifier>transfers</identifier><name>Transfers</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Indicates the number of transfers permitted on this fare. The fact that this field can be left empty is an exception to the requirement that a Required field must not be empty. Valid options are: 0 - No transfers permitted on this fare. 1 - Riders may transfer once. 2 - Riders may transfer twice. empty - Unlimited transfers are permitted.</description></field><field><identifier>agency_id</identifier><name>Agency Id</name><structures><structure><identifier>Id</identifier><reference>agency.agency_id</reference></structure></structures><required>conditionally</required><description>Identifies the relevant agency for a fare. This field is required for datasets with multiple agencies defined in agency.txt, otherwise it is optional.</description></field><field><identifier>transfer_duration</identifier><name>Transfer Duration</name><structures><structure><identifier>NonNegativeInteger</identifier><reference/></structure></structures><required>optional</required><description>Length of time in seconds before a transfer expires. When transfers = 0 this field can be used to indicate how long a ticket is valid for or it can can be left empty.</description></field></fields></file><file><filename>fare_rules.txt</filename><name>Fare Rules</name><required>optional</required><description>Rules to apply fares for itineraries.</description><fields><field><identifier>fare_id</identifier><name>Fare Id</name><structures><structure><identifier>Id</identifier><reference>fare_attributes.fare_id</reference></structure></structures><required>required</required><description>Identifies a fare class.</description></field><field><identifier>route_id</identifier><name>Route Id</name><structures><structure><identifier>Id</identifier><reference>routes.route_id</reference></structure></structures><required>optional</required><description>Identifies a route associated with the fare class. If several routes with the same fare attributes exist, create a record in fare_rules.txt for each route. Example: If fare class \"b\" is valid on route \"TSW\" and \"TSE\", the fare_rules.txt file would contain these records for the fare class: fare_id,route_id b,TSW b,TSE</description></field><field><identifier>origin_id</identifier><name>Origin Id</name><structures><structure><identifier>Id</identifier><reference>stops.zone_id</reference></structure></structures><required>optional</required><description>Identifies an origin zone. If a fare class has multiple origin zones, create a record in fare_rules.txt for each origin_id. Example: If fare class \"b\" is valid for all travel originating from either zone \"2\" or zone \"8\", the fare_rules.txt file would contain these records for the fare class: fare_id,...,origin_id b,...,2 b,...,8</description></field><field><identifier>destination_id</identifier><name>Destination Id</name><structures><structure><identifier>Id</identifier><reference>stops.zone_id</reference></structure></structures><required>optional</required><description>Identifies a destination zone. If a fare class has multiple destination zones, create a record in fare_rules.txt for each destination_id. Example: The origin_id and destination_id fields could be used together to specify that fare class \"b\" is valid for travel between zones 3 and 4, and for travel between zones 3 and 5, the fare_rules.txt file would contain these records for the fare class: fare_id,...,origin_id,destination_id b,...,3,4 b,...,3,5</description></field><field><identifier>contains_id</identifier><name>Contains Id</name><structures><structure><identifier>Id</identifier><reference>stops.zone_id</reference></structure></structures><required>optional</required><description>Identifies the zones that a rider will enter while using a given fare class. Used in some systems to calculate correct fare class. Example: If fare class \"c\" is associated with all travel on the GRT route that passes through zones 5, 6, and 7 the fare_rules.txt would contain these records: fare_id,route_id,...,contains_id c,GRT,...,5 c,GRT,...,6 c,GRT,...,7 Because all contains_id zones must be matched for the fare to apply, an itinerary that passes through zones 5 and 6 but not zone 7 would not have fare class \"c\". For more detail, see https://code.google.com/p/googletransitdatafeed/wiki/FareExamples in the GoogleTransitDataFeed project wiki.</description></field></fields></file><file><filename>shapes.txt</filename><name>Shapes</name><required>optional</required><description>Rules for mapping vehicle travel paths, sometimes referred to as route alignments.</description><fields><field><identifier>shape_id</identifier><name>Shape Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>required</required><description>Identifies a shape.</description></field><field><identifier>shape_pt_lat</identifier><name>Shape Pt Lat</name><structures><structure><identifier>Latitude</identifier><reference/></structure></structures><required>required</required><description>Latitude of a shape point. Each record in shapes.txt represents a shape point used to define the shape.</description></field><field><identifier>shape_pt_lon</identifier><name>Shape Pt Lon</name><structures><structure><identifier>Longitude</identifier><reference/></structure></structures><required>required</required><description>Longitude of a shape point.</description></field><field><identifier>shape_pt_sequence</identifier><name>Shape Pt Sequence</name><structures><structure><identifier>NonNegativeInteger</identifier><reference/></structure></structures><required>required</required><description>Sequence in which the shape points connect to form the shape. Values must increase along the trip but do not need to be consecutive. Example: If the shape \"A_shp\" has three points in its definition, the shapes.txt file might contain these records to define the shape: shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence A_shp,37.61956,-122.48161,0 A_shp,37.64430,-122.41070,6 A_shp,37.65863,-122.30839,11</description></field><field><identifier>shape_dist_traveled</identifier><name>Shape Dist Traveled</name><structures><structure><identifier>NonNegativeFloat</identifier><reference/></structure></structures><required>optional</required><description>Actual distance traveled along the shape from the first shape point to the point specified in this record. Used by trip planners to show the correct portion of the shape on a map. Values must increase along with shape_pt_sequence; they cannot be used to show reverse travel along a route. Distance units must be consistent with those used in stop_times.txt. Example: If a bus travels along the three points defined above for A_shp, the additional shape_dist_traveled values (shown here in kilometers) would look like this: shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence,shape_dist_traveled A_shp,37.61956,-122.48161,0,0 A_shp,37.64430,-122.41070,6,6.8310 A_shp,37.65863,-122.30839,11,15.8765</description></field></fields></file><file><filename>frequencies.txt</filename><name>Frequencies</name><required>optional</required><description>Headway (time between trips) for headway-based service or a compressed representation of fixed-schedule service.</description><fields><field><identifier>trip_id</identifier><name>Trip Id</name><structures><structure><identifier>Id</identifier><reference>trips.trip_id</reference></structure></structures><required>required</required><description>Identifies a trip to which the specified headway of service applies.</description></field><field><identifier>start_time</identifier><name>Start Time</name><structures><structure><identifier>Time</identifier><reference/></structure></structures><required>required</required><description>Time at which the first vehicle departs from the first stop of the trip with the specified headway.</description></field><field><identifier>end_time</identifier><name>End Time</name><structures><structure><identifier>Time</identifier><reference/></structure></structures><required>required</required><description>Time at which service changes to a different headway (or ceases) at the first stop in the trip.</description></field><field><identifier>headway_secs</identifier><name>Headway Secs</name><structures><structure><identifier>NonNegativeInteger</identifier><reference/></structure></structures><required>required</required><description>Time, in seconds, between departures from the same stop (headway) for the trip, during the time interval specified by start_time and end_time. Multiple headways for the same trip are allowed, but may not overlap. New headways may start at the exact time the previous headway ends.</description></field><field><identifier>exact_times</identifier><name>Exact Times</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Indicates the type of service for a trip. See the file description for more information. Valid options are: 0 or empty - Frequency-based trips. 1 - Schedule-based trips with the exact same headway throughout the day. In this case the end_time value must be greater than the last desired trip start_time but less than the last desired trip start_time + headway_secs.</description></field></fields></file><file><filename>transfers.txt</filename><name>Transfers</name><required>optional</required><description>Rules for making connections at transfer points between routes.</description><fields><field><identifier>from_stop_id</identifier><name>From Stop Id</name><structures><structure><identifier>Id</identifier><reference>stops.stop_id</reference></structure></structures><required>required</required><description>Identifies a stop or station where a connection between routes begins. If this field refers to a station, the transfer rule applies to all its child stops.</description></field><field><identifier>to_stop_id</identifier><name>To Stop Id</name><structures><structure><identifier>Id</identifier><reference>stops.stop_id</reference></structure></structures><required>required</required><description>Identifies a stop or station where a connection between routes ends. If this field refers to a station, the transfer rule applies to all child stops.</description></field><field><identifier>transfer_type</identifier><name>Transfer Type</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Indicates the type of connection for the specified (from_stop_id, to_stop_id) pair. Valid options are: 0 or empty - Recommended transfer point between routes. 1 - Timed transfer point between two routes. The departing vehicle is expected to wait for the arriving one and leave sufficient time for a rider to transfer between routes. 2 - Transfer requires a minimum amount of time between arrival and departure to ensure a connection. The time required to transfer is specified by min_transfer_time. 3 - Transfers are not possible between routes at the location.</description></field><field><identifier>min_transfer_time</identifier><name>Min Transfer Time</name><structures><structure><identifier>NonNegativeInteger</identifier><reference/></structure></structures><required>optional</required><description>Amount of time, in seconds, that must be available to permit a transfer between routes at the specified stops. The min_transfer_time should be sufficient to permit a typical rider to move between the two stops, including buffer time to allow for schedule variance on each route.</description></field></fields></file><file><filename>pathways.txt</filename><name>Pathways</name><required>optional</required><description>Pathways linking together locations within stations.</description><fields><field><identifier>pathway_id</identifier><name>Pathway Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>required</required><description>The pathway_id field contains an ID that uniquely identifies the pathway. The pathway_id is used by systems as an internal identifier of this record (e.g., primary key in database), and therefore the pathway_id must be dataset unique. Different pathways can go from the same from_stop_id to the same to_stop_id. For example, this happens when two escalators are side by side in opposite direction, or when a stair is nearby and elevator and both go from the same place to the same place.</description></field><field><identifier>from_stop_id</identifier><name>From Stop Id</name><structures><structure><identifier>Id</identifier><reference>stops.stop_id</reference></structure></structures><required>required</required><description>Location at which the pathway begins. It contains a stop_id that identifies a platform, entrance/exit, generic node or boarding area from the stops.txt file.</description></field><field><identifier>to_stop_id</identifier><name>To Stop Id</name><structures><structure><identifier>Id</identifier><reference>stops.stop_id</reference></structure></structures><required>required</required><description>Location at which the pathway ends. It contains a stop_id that identifies a platform, entrance/exit, generic node or boarding area from the stops.txt file.</description></field><field><identifier>pathway_mode</identifier><name>Pathway Mode</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Type of pathway between the specified (from_stop_id, to_stop_id) pair. Valid values for this field are: * 1: walkway * 2: stairs * 3: moving sidewalk/travelator * 4: escalator * 5: elevator * 6: fare gate (or payment gate): A pathway that crosses into an area of the station where a proof of payment is required (usually via a physical payment gate). Fare gates may either separate paid areas of the station from unpaid ones, or separate different payment areas within the same station from each other. This information can be used to avoid routing passengers through stations using shortcuts that would require passengers to make unnecessary payments, like directing a passenger to walk through a subway platform to reach a busway. * 7: exit gate: Indicates a pathway exiting an area where proof-of-payment is required into an area where proof-of-payment is no longer required.</description></field><field><identifier>is_bidirectional</identifier><name>Is Bidirectional</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Indicates in which direction the pathway can be used: * 0: Unidirectional pathway, it can only be used from from_stop_id to to_stop_id. * 1: Bidirectional pathway, it can be used in the two directions. Fare gates (pathway_mode=6) and exit gates (pathway_mode=7) cannot be bidirectional.</description></field><field><identifier>length</identifier><name>Length</name><structures><structure><identifier>NonNegativeFloat</identifier><reference/></structure></structures><required>optional</required><description>Horizontal length in meters of the pathway from the origin location (defined in from_stop_id) to the destination location (defined in to_stop_id). This field is recommended for walkways (pathway_mode=1), fare gates (pathway_mode=6) and exit gates (pathway_mode=7).</description></field><field><identifier>traversal_time</identifier><name>Traversal Time</name><structures><structure><identifier>PositiveInteger</identifier><reference/></structure></structures><required>optional</required><description>Average time in seconds needed to walk through the pathway from the origin location (defined in from_stop_id) to the destination location (defined in to_stop_id). This field is recommended for moving sidewalks (pathway_mode=3), escalators (pathway_mode=4) and elevator (pathway_mode=5).</description></field><field><identifier>stair_count</identifier><name>Stair Count</name><structures><structure><identifier>NonNullInteger</identifier><reference/></structure></structures><required>optional</required><description>Number of stairs of the pathway. Best Practices: one could use the approximation of 1 floor = 15 stairs to generate approximative values. A positive stair_count implies that the rider walk up from from_stop_id to to_stop_id. And a negative stair_count implies that the rider walk down from from_stop_id to to_stop_id. This field is recommended for stairs (pathway_mode=2).</description></field><field><identifier>max_slope</identifier><name>Max Slope</name><structures><structure><identifier>Float</identifier><reference/></structure></structures><required>optional</required><description>Maximum slope ratio of the pathway. Valid values for this field are: * 0 or (empty): no slope. * A float: slope ratio of the pathway, positive for upwards, negative for downwards. This field should be used only with walkways (pathway_type=1) and moving sidewalks (pathway_type=3). Example: In the US, 0.083 (also written 8.3%) is the maximum slope ratio for hand-propelled wheelchair, which mean an increase of 0.083m (so 8.3cm) for each 1m.</description></field><field><identifier>min_width</identifier><name>Min Width</name><structures><structure><identifier>PositiveFloat</identifier><reference/></structure></structures><required>optional</required><description>Minimum width of the pathway in meters. This field is highly recommended if the minimum width is less than 1 meter.</description></field><field><identifier>signposted_as</identifier><name>Signposted As</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>optional</required><description>String of text from physical signage visible to transit riders. The string can be used to provide text directions to users, such as 'follow signs to '. The language text should appear in this field exactly how it is printed on the signs - it should not be translated.</description></field><field><identifier>reversed_signposted_as</identifier><name>Reversed Signposted As</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>optional</required><description>Same than the signposted_as field, but when the pathways is used backward, i.e. from the to_stop_id to the from_stop_id.</description></field></fields></file><file><filename>levels.txt</filename><name>Levels</name><required>optional</required><description>Levels within stations.</description><fields><field><identifier>level_id</identifier><name>Level Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>required</required><description>Id of the level that can be referenced from stops.txt.</description></field><field><identifier>level_index</identifier><name>Level Index</name><structures><structure><identifier>Float</identifier><reference/></structure></structures><required>required</required><description>Numeric index of the level that indicates relative position of this level in relation to other levels (levels with higher indices are assumed to be located above levels with lower indices). Ground level should have index 0, with levels above ground indicated by positive indices and levels below ground by negative indices.</description></field><field><identifier>level_name</identifier><name>Level Name</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>optional</required><description>Optional name of the level (that matches level lettering/numbering used inside the building or the station). Is useful for elevator routing (e.g. “take the elevator to level “Mezzanine” or “Platforms” or “-1”).</description></field></fields></file><file><filename>feed_info.txt</filename><name>Feed Info</name><required>conditionally</required><description>Dataset metadata, including publisher, version, and expiration information.</description><fields><field><identifier>feed_publisher_name</identifier><name>Feed Publisher Name</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>required</required><description>Full name of the organization that publishes the dataset. This might be the same as one of the agency.agency_name values.</description></field><field><identifier>feed_publisher_url</identifier><name>Feed Publisher Url</name><structures><structure><identifier>Url</identifier><reference/></structure></structures><required>required</required><description>URL of the dataset publishing organization's website. This may be the same as one of the agency.agency_url values.</description></field><field><identifier>feed_lang</identifier><name>Feed Lang</name><structures><structure><identifier>LanguageCode</identifier><reference/></structure></structures><required>required</required><description>Default language for the text in this dataset. This setting helps GTFS consumers choose capitalization rules and other language-specific settings for the dataset. To define another language, use the language field in translations.txt. Multilingual datasets might be the default language with the original text in multiple languages. In such cases, use the ISO 639-2 language code mul in the feed_lang field. Provide a translation for each of the languages used in the dataset in translations.txt. If all of the original text in the dataset is in the same language, don't use mul. For example, a dataset in Switzerland might set the original stops.stop_name field populated with stop names in different languages. Each stop name is written in accordance with the dominant language in that stop’s geographic location. Stop names include Genève for the French-speaking city of Geneva, Zürich for the German-speaking city of Zurich, and Biel/Bienne for the bilingual city of Biel/Bienne. Set feed_lang=mul and provide the following translations in translations.txt: * German: \"Genf,\" \"Zürich,\" and \"Biel\" * French: \"Genève,\" \"Zurich,\" and \"Bienne\" * Italian: \"Ginevra,\" \"Zurigo,\" and \"Bienna\" * English: \"Geneva,\" \"Zurich,\" and \"Biel/Bienne\"</description></field><field><identifier>default_lang</identifier><name>Default Lang</name><structures><structure><identifier>LanguageCode</identifier><reference/></structure></structures><required>optional</required><description>Defines the language used when the data consumer doesn’t know the language of the rider. It's often defined as en, English.</description></field><field><identifier>feed_start_date</identifier><name>Feed Start Date</name><structures><structure><identifier>Date</identifier><reference/></structure></structures><required>optional</required><description>The dataset provides complete and reliable schedule information for service in the period from the beginning of the feed_start_date day to the end of the feed_end_date day. Both days can be left empty if unavailable. The feed_end_date date must not precede the feed_start_date date if both are given. Dataset providers are encouraged to give schedule data outside this period to advise of likely future service, but dataset consumers should treat it mindful of its non-authoritative status. If feed_start_date or feed_end_date extend beyond the active calendar dates defined in calendar.txt and calendar_dates.txt, the dataset is making an explicit assertion that there is no service for dates within the feed_start_date to feed_end_date range but not included in the active calendar dates.</description></field><field><identifier>feed_end_date</identifier><name>Feed End Date</name><structures><structure><identifier>Date</identifier><reference/></structure></structures><required>optional</required><description>Refer to the feed_start_date row in this table.</description></field><field><identifier>feed_version</identifier><name>Feed Version</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>optional</required><description>String that indicates the current version of their GTFS dataset. GTFS-consuming applications can display this value to help dataset publishers determine whether the latest dataset has been incorporated.</description></field><field><identifier>feed_contact_email</identifier><name>Feed Contact Email</name><structures><structure><identifier>Email</identifier><reference/></structure></structures><required>optional</required><description>Email address for communication regarding the GTFS dataset and data publishing practices. feed_contact_email is a technical contact for GTFS-consuming applications. Provide customer service contact information through agency.txt.</description></field><field><identifier>feed_contact_url</identifier><name>Feed Contact Url</name><structures><structure><identifier>Url</identifier><reference/></structure></structures><required>optional</required><description>URL for contact information, a web-form, support desk, or other tools for communication regarding the GTFS dataset and data publishing practices. feed_contact_url is a technical contact for GTFS-consuming applications. Provide customer service contact information through agency.txt.</description></field></fields></file><file><filename>translations.txt</filename><name>Translations</name><required>optional</required><description>Translated information of a transit agency.</description><fields><field><identifier>table_name</identifier><name>Table Name</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>required</required><description>Defines the dataset table that contains the field to be translated. The following values are allowed: * agency * stops * routes * trips * stop_times * feed_info * pathways * levels Note: Don't include the.txt file extension after the table's name.</description></field><field><identifier>field_name</identifier><name>Field Name</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>required</required><description>Provides the name of the field to be translated. Fields with the type \"Text\" can be translated, while fields with the types \"URL,\" \"Email,\" and \"Phone number\" can be included here to provide those resources in the correct language. Note: Fields with other types are ignored and will not be translated.</description></field><field><identifier>language</identifier><name>Language</name><structures><structure><identifier>LanguageCode</identifier><reference/></structure></structures><required>required</required><description>Provides the language of translation. If this language is the same as the one from feed_lang in feed_info.txt, the original value of the field is the default value used in languages without specific translations. For example, in Switzerland, a city in a bilingual canton is officially called \"Biel/Bienne,\" but it would simply be called \"Bienne\" in French and \"Biel\" in German.</description></field><field><identifier>translation</identifier><name>Translation</name><structures><structure><identifier>Text</identifier><reference/></structure><structure><identifier>Url</identifier><reference/></structure><structure><identifier>Email</identifier><reference/></structure><structure><identifier>PhoneNumber</identifier><reference/></structure></structures><required>required</required><description>Provides the translated value for the specified field_name.</description></field><field><identifier>record_id</identifier><name>Record Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>conditionally</required><description>Defines the record that corresponds to the field to be translated. The value in record_id needs to be a main ID from a dataset table, as defined in the following table: (table has been removed) The following conditions determine how this field can be used: * Forbidden if table_name equals feed_info. * Forbidden if field_value is defined. * Required if field_value is empty.</description></field><field><identifier>record_sub_id</identifier><name>Record Sub Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>conditionally</required><description>Helps to translate the record that contains the field when the table referenced in record_id doesn’t have a unique ID. The value in record_sub_id is the secondary ID of a dataset table, as defined in the following table: (table has been removed) The following conditions determine how this field can be used: * Forbidden if table_name equals feed_info. * Forbidden if field_value is defined. * Required if table_name equals stop_times and record_id is defined.</description></field><field><identifier>field_value</identifier><name>Field Value</name><structures><structure><identifier>Text</identifier><reference/></structure><structure><identifier>Url</identifier><reference/></structure><structure><identifier>Email</identifier><reference/></structure><structure><identifier>PhoneNumber</identifier><reference/></structure></structures><required>conditionally</required><description>Instead of using record_id and record_sub_id to define which record needs to be translated, field_value can be used to define the value for translation. When used, the translation is applied when the field identified by table_name and field_name contains the exact same value defined in field_value. The field must exactly match the value defined in field_value. If only a subset of the value matches field_value, the translation isn't applied. If two translation rules match the same record, one with field_value and the other one with record_id, then the rule with record_id is the one that needs to be used. The following conditions determine how this field can be used: * Forbidden if table_name equals feed_info. * Forbidden if record_id is defined. * Required if record_id is empty.</description></field></fields></file><file><filename>attributions.txt</filename><name>Attributions</name><required>optional</required><description>Specifies the attributions that are applied to the dataset.</description><fields><field><identifier>attribution_id</identifier><name>Attribution Id</name><structures><structure><identifier>Id</identifier><reference/></structure></structures><required>optional</required><description>Identifies an attribution for the dataset, or a subset of it. This field is useful for translations.</description></field><field><identifier>agency_id</identifier><name>Agency Id</name><structures><structure><identifier>Id</identifier><reference>agency.agency_id</reference></structure></structures><required>optional</required><description>The agency to which the attribution applies. If one agency_id, route_id, or trip_id attribution is defined, the other fields must be empty. If none are specified, the attribution applies to the whole dataset.</description></field><field><identifier>route_id</identifier><name>Route Id</name><structures><structure><identifier>Id</identifier><reference>routes.route_id</reference></structure></structures><required>optional</required><description>This field functions in the same way as agency_id, except the attribution applies to a route. Multiple attributions can apply to the same route.</description></field><field><identifier>trip_id</identifier><name>Trip Id</name><structures><structure><identifier>Id</identifier><reference>trips.trip_id</reference></structure></structures><required>optional</required><description>This field functions in the same way as agency_id, except the attribution applies to a trip. Multiple attributions can apply to the same trip.</description></field><field><identifier>organization_name</identifier><name>Organization Name</name><structures><structure><identifier>Text</identifier><reference/></structure></structures><required>required</required><description>The name of the organization that the dataset is attributed to.</description></field><field><identifier>is_producer</identifier><name>Is Producer</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>The role of the organization is producer. Allowed values include the following: * 0 or empty: Organization doesn’t have this role. * 1: Organization does have this role. At least one of the fields, either is_producer, is_operator, or is_authority, must be set at 1.</description></field><field><identifier>is_operator</identifier><name>Is Operator</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Functions in the same way as is_producer, except the role of the organization is operator.</description></field><field><identifier>is_authority</identifier><name>Is Authority</name><structures><structure><identifier>Enum</identifier><reference/></structure></structures><required>optional</required><description>Functions in the same way as is_producer, except the role of the organization is authority.</description></field><field><identifier>attribution_url</identifier><name>Attribution Url</name><structures><structure><identifier>Url</identifier><reference/></structure></structures><required>optional</required><description>The URL of the organization.</description></field><field><identifier>attribution_email</identifier><name>Attribution Email</name><structures><structure><identifier>Email</identifier><reference/></structure></structures><required>optional</required><description>The email of the organization.</description></field><field><identifier>attribution_phone</identifier><name>Attribution Phone</name><structures><structure><identifier>PhoneNumber</identifier><reference/></structure></structures><required>optional</required><description>The phone number of the organization.</description></field></fields></file></files></gtfs_static>";
    }
    
    /**
     * @param {!Entry|!Date} date
     * @returns {!Date|!String}
     */
    function gtfsDate(date) {
        if (date instanceof Entry) {
            const [ year, month, day ] = date.get().split('-');
            return new Date(parseInt(year, 10), parseInt(month, 10) - 1, parseInt(day, 10));
        }
        const nextDay = new Date(date);
        nextDay.setDate(nextDay.getDate() + 1);
        return nextDay.toISOString().slice(0, 10);
    }
    /**
     * @param {!String} line
     * @returns {!Array.<!String>}
     */
    function gtfsLineSplit(line) {
        const split = line.split('\r').join('').split('\t').join('').split('""').join('\r').split(",");
        var index = 0;
        while (index < split.length - 1) {
            if ((split[index].match(/"/g) || []).length == 1) {
                split[index] += ';' + split.splice(index + 1, 1);
            } else {
                index += 1;
            }
        }
        split.forEach((value, index) => split[index] = value.split('"').join('').split('\r').join('"').trim());
        return split;
    }
    /**
     * @param {!Record} stop
     * @returns {?{ contains: !Function, data: { record: !Record, children: !Array.<!Object>, isOpened: !Boolean }, field: !String, flat: !Function }}
     */
    function gtfsStopTree(stop) {
        if (stop.__file.identifier !== 'stops') {
            return null;
        }
        const getTreeData = parent => {
            const nodes = parent['stop_id'].children.filter(child => child.field.file.identifier === 'stops').map(entry => getTreeData(entry.record));
            return { record: parent, children: nodes, isOpened: nodes.length != 0 };
        };
        const __data = getTreeData(stop);
        const __contains = (stopID, node) => {
            if (node === undefined) {
                node = __data;
            }
            if (node.record['stop_id'].get() === stopID) {
                return true;
            }
            for (var index = 0; index < node.children.length; index++) {
                if (__contains(stopID, node.children[index])) {
                    return true;
                }
            }
            return false;
        };
        const __flat = (node, data) => {
            if (node === undefined) {
                node = __data;
                data = new Array();
            }
            data.push(node.record);
            node.children.forEach(child => data = __flat(child, data));
            return data;
        };
        console.log(__flat());
        return { contains: __contains, data: __data, field: 'parent_station', flat: __flat };
    }

    /**
     * @param {!String} text
     * @returns {!String}
     */
    function shorterText(text) {
        const size = 450;
        return text.length <= size ? text : text.substr(0, size - 3) + '...';
    }

    class Dataset {
        /**
         * @param {!Doucment} xmlDataset
         */
        constructor(xmlDataset) {
            /** @type {!String} */
            this.filename = 'untitled';

            /** @type {!Array.<!Structure>} */
            this.structures = new Array();
            xmlDataset.getElementsByTagName('structures')[0].getElementsByTagName('structure').forEach(xmlStructure => {
                this.structures.push(new Structure(xmlStructure, this));
            });

            /** @type {!Array.<!Enumeration>} */
            this.enumerations = new Array();
            xmlDataset.getElementsByTagName('enumerations')[0].getElementsByTagName('enumeration').forEach(xmlEnumeration => {
                this.enumerations.push(new Enumeration(xmlEnumeration, this));
            });

            /** @type {!Array.<!File>} */
            this.files = new Array();
            xmlDataset.getElementsByTagName('files')[0].getElementsByTagName('file').forEach(xmlFile => {
                this.files.push(new File(xmlFile, this));
            });
            this.files.forEach(file => file.fields.forEach(field => field.afterDatasetConstructed()));
        }

        /**
         * @param {!String} fileIdentifier
         * @returns {?File}
         */
        get(fileIdentifier) {
            const file = this.files.find(file => file.identifier === fileIdentifier);
            return file instanceof File ? file : null;
        }

        /**
         * @param {!Object} event
         */
        load(event) {
            const that = this;
            const zipFile = event.target.files[0];
            JSZip.loadAsync(zipFile).then(function(zip) {
                that.filename = zipFile.name.slice(0, -4);
                that.files.forEach(file => file.onDatasetReset());
                var counter = 0; zip.forEach(() => counter += 1);
                zip.forEach((relativePath, zipEntry) => {
                    zipEntry.async('text').then(function(content) {
                        const file = that.get(zipEntry.name.slice(0, -4));
                        if (file instanceof File) {
                            const lines = content.split('\n');
                            const fields = gtfsLineSplit(lines[0]).map(fieldIdentifier => file.get(fieldIdentifier));
                            lines.slice(1).forEach(line => {
                                const entries = gtfsLineSplit(line);
                                const record = file.createRecord();
                                fields.forEach((field, index) => {
                                    if (field instanceof Field && typeof entries[index] === 'string') {
                                        record[field.identifier].data = field.types[0].enumeration instanceof Enumeration
                                            ? field.types[0].enumeration.toHTML(entries[index])
                                            : field.types[0].structure.toHTML(entries[index]);
                                    }
                                });
                            });
                        }
                        if (--counter == 0) {
                            that.files.forEach(file => file.records.forEach(record => record.__afterDatasetLoaded()));
                            
                        }
                    }, function(reason) {
                        console.log(reason);
                    });
                });
            }, function(reason) {
                console.log(reason);
            });
        }
        /**
         * @param {!String|undefined} filename
         */
        reset(filename) {
            this.filename = typeof filename === 'string' && filename.length != 0 ? filename : 'untitled';
            this.files.forEach(file => file.onDatasetReset());
        }
        save() {
            const filename = this.filename + '.zip';
            const zipFile = new JSZip();
            this.files.forEach(file => zipFile.file(file.identifier + '.txt', file.toString()));
            zipFile.generateAsync({ type: 'blob' }).then(function(blob) {
                saveAs(blob, filename);
            }, function(reason) {
                console.log(reason);
            });
        }
    }

    class Structure {
        /**
         * comment: no specialized handling for 'CurrencyCode', 'LanguageCode' & 'Timezone'
         * @param {!Node} xmlStructure
         * @param {!Dataset} dataset
         */
        constructor(xmlStructure, dataset) {
            /** @type {!Dataset} */
            this.dataset = dataset;

            /** @type {!String} */
            this.identifier = xmlStructure.getElementsByTagName('identifier')[0].innerHTML;

            /** @type {!String} */
            this.name = xmlStructure.getElementsByTagName('name')[0].innerHTML;

            /** @type {!String} */
            this.description = shorterText(xmlStructure.getElementsByTagName('description')[0].innerHTML);
        }

        /**
         * @returns {!String}
         */
        getInputPattern() {
            switch (this.identifier) {
                case 'Email':
                    return '.+@.+[.].+';
                case 'Latitude': // range: [-90, 90]
                    return '[-]?[1-8]\\d|[-]?[1-8]\\d[.]\\d*|[-]?90|[-]?90[.][0]*|[-]?\\d|[-]?\\d[.]\\d*';
                case 'Longitude': // range: [-180, 180]
                   return '[-]?\\d\\d|[-]?\\d\\d[.]\\d*|[-]?1[0-7]\\d|[-]?1[0-7]\\d[.]\\d*|[-]?180|[-]?180[.][0]*|[-]?\\d|[-]?\\d[.]\\d*';
                case 'NonNegativeFloat':
                    return '[1-9]+\\d*[.]?\\d*|0[.]\\d*|0[.]?';
                case 'NonNegativeInteger':
                    return '[1-9]+\\d*|0';
                case 'Time': // max: 23:59:59 on next day
                    return '[0-3]?\\d:[0-5]\\d:[0-5]\\d|4[0-7]:[0-5]\\d:[0-5]\\d';
                case 'Url':
                    return 'https?://.+[.].+';
                case 'PositiveInteger':
                    return '[1-9]+\\d*';
                case 'NonNullInteger':
                    return '[-]?[1-9]+\\d*';
                case 'PositiveFloat':
                    return '[1-9]+\\d*[.]?\\d*|0[.]\\d*[1-9]+\\d*';
                case 'Float':
                    return '[-]?[1-9]+\\d*[.]?\\d*|[-]?0[.]\\d*|[-]?0';
                default:
                    return '.*';
            }
        }
        /**
         * @returns {!String}
         */
        getInputType() {
            switch (this.identifier) {
                case 'Color':
                    return 'color';
                case 'Date':
                    return 'date';
                case 'Email':
                    return 'email';
                case 'Url':
                    return 'url';
                default:
                    return 'text';
            }
        }

        /**
         * @param {!String} data
         * @returns {!String}
         */
        fromHTML(data) {
            switch (this.identifier) {
                case 'Color':
                    return data.substr(1);
                default:
                    return data;
            }
        }
        /**
         * @param {!String} data
         * @returns {!String}
         */
        toHTML(data) {
            switch (this.identifier) {
                case 'Color':
                    return data.length == 6 ? '#' + data : data;
                case 'Date':
                    return data.length == 8 ? data.substr(0, 4) + '-' + data.substr(4, 2) + '-' + data.substr(6) : data;
                default:
                    return data;
            }
        }
    }

    class Enumeration {
        /**
         * @param {!Node} xmlEnumeration
         * @param {!Dataset} dataset
         */
        constructor(xmlEnumeration, dataset) {
            /** @type {!Dataset} */
            this.dataset = dataset;

            /** @type {!String} */
            this.name = xmlEnumeration.getElementsByTagName('name')[0].innerHTML;

            /**
             * @typedef {Object} FieldTypeInformation
             * @property {!String} iFile
             * @property {!String} iField
             * @property {!Number} iFieldType
             */
            /** @type {!Array.<!FieldTypeInformation>} */
            this.children = new Array();
            xmlEnumeration.getElementsByTagName('reference').forEach(child => {
                const [ fileIdentifier, fieldIdentifier, fieldTypeIndex ] = child.innerHTML.split('.');
                this.children.push({ iFile: fileIdentifier, iField: fieldIdentifier, iFieldType: parseInt(fieldTypeIndex, 10) });
            });

            /** @type {!Array.<!String>} */
            this.raws = new Array();
            /** @type {!Array.<!String>} */
            this.values = new Array();
            xmlEnumeration.getElementsByTagName('map').forEach(xmlMap => {
                const [ raw, value ] = xmlMap.innerHTML.split('.');
                this.raws.push(raw);
                this.values.push(value);
            });

            /** @type {?Number} */
            this.iBlank = xmlEnumeration.getElementsByTagName('blank')[0].innerHTML;
            this.iBlank = this.iBlank.length != 0 ? parseInt(this.iBlank, 10) : null;
        }

        /**
         * @param {!Field} field
         * @param {!Number} fieldTypeIndex
         * @returns {!Boolean}
         */
        handles(field, fieldTypeIndex) {
            const child = this.children.find(child => child.iFile === field.file.identifier && child.iField === field.identifier && child.iFieldType == fieldTypeIndex);
            return child !== undefined; 
        }

        /**
         * @param {!String} data
         * @returns {!String}
         */
        fromHTML(data) {
            const index = this.values.findIndex(value => value === data);
            return index != -1 ? this.raws[index] : '';
        }
        /**
         * @param {!String} data
         * @returns {!String}
         */
        toHTML(data) {
            if (data.length == 0 && typeof this.iBlank === 'number') {
                return this.values[this.iBlank];
            }
            const index = this.raws.findIndex(raw => raw === data);
            return index != -1 ? this.values[index] : '';
        }
    }

    class File {
        /**
         * @param {!Node} xmlFile
         * @param {!Dataset} dataset
         */
        constructor(xmlFile, dataset) {
            /** @type {!Dataset} */
            this.dataset = dataset;

            /** @type {!String} */
            this.identifier = xmlFile.getElementsByTagName('filename')[0].innerHTML.slice(0, -4);

            /** @type {!String} */
            this.name = xmlFile.getElementsByTagName('name')[0].innerHTML;

            /** @type {!String} */
            this.description = shorterText(xmlFile.getElementsByTagName('description')[0].innerHTML);
            
            /** @type {!Boolean} */
            this.isRequired = xmlFile.getElementsByTagName('required')[0].innerHTML === 'required';

            /** @type {!Array.<!Field>} */
            this.fields = new Array();
            xmlFile.getElementsByTagName('field').forEach(xmlField => {
                this.fields.push(new Field(xmlField, this));
            });

            /** @type {!Array.<!Record>} */
            this.records = new Array();

            /** @type {!Record} */
            this.shadowRecord = new Record(this, true);
        }

        onDatasetReset() {
            this.records.length = 0;
            this.shadowRecord.__delete();
        }

        /**
         * @param {!String} fieldIdentifier
         * @returns {?Field}
         */
        get(fieldIdentifier) {
            const field = this.fields.find(field => field.identifier === fieldIdentifier);
            return field instanceof Field ? field : null;
        }
        /**
         * @param {!{ property: !String, value: !String }} data
         * @returns {?Array.<!Record>}
         */
        filter(data) {
            return this.get(data.property) instanceof Field ? this.records.filter(record => record[data.property].get() === data.value) : null;
        }

        /**
         * @returns {!Record}
         */
        addShadowRecord() {
            const record = this.createRecord(this.shadowRecord.__toArray());
            this.shadowRecord.__delete();
            return record;
        }
        /**
         * @param {!Array.<!{ property: !String, value: !String }>|undefined} data
         * @returns {!Record}
         */
        createRecord(data) {
            const record = new Record(this);
            this.records.push(record);
            if (data instanceof Array) {
                data.forEach(element => {
                    const entry = record[element.property];
                    if (entry instanceof Entry) {
                        entry.set(element.value);
                    }
                });
            }
            return record;
        }

        /**
         * @returns {!String}
         */
        toString() {
            var result = this.fields.reduce((str, field) => str + field.identifier + ',', '').slice(0, -1);
            this.records.forEach(record => {
                const line = this.fields.reduce((str, field) => {
                    const entry = record[field.identifier];
                    const value = entry.isEnumeration()
                        ? entry.fieldType.enumeration.fromHTML(entry.get())
                        : entry.fieldType.structure.fromHTML(entry.get());
                    return str + value + ',';
                }, '');
                result += '\n' + line.slice(0, -1);
            });
            return result;
        }
    }

    class Field {
        /**
         * @param {!Node} xmlField
         * @param {!File} file
         */
        constructor(xmlField, file) {
            /** @type {!File} */
            this.file = file;

            /** @type {!String} */
            this.identifier = xmlField.getElementsByTagName('identifier')[0].innerHTML;

            /** @type {!String} */
            this.name = xmlField.getElementsByTagName('name')[0].innerHTML;

            /** @type {!String} */
            this.description = shorterText(xmlField.getElementsByTagName('description')[0].innerHTML);

            /** @type {!Boolean} */
            this.isRequired = xmlField.getElementsByTagName('required')[0].innerHTML === 'required';

            /** @type {!Array.<!FieldType>} */
            this.types = new Array();
            xmlField.getElementsByTagName('structures')[0].getElementsByTagName('structure').forEach((xmlType, index) => {
                const structureIdentifier = xmlType.getElementsByTagName('identifier')[0].innerHTML;
                const structure = file.dataset.structures.find(structure => structure.identifier === structureIdentifier);
                const enumeration = file.dataset.enumerations.find(enumeration => enumeration.handles(this, index));
                this.types.push(new FieldType(this, structure, enumeration, xmlType.getElementsByTagName('reference')[0].innerHTML));
            });

            /** @type {!Array.<!Field>} */
            this.children = new Array();
        }

        afterDatasetConstructed() {
            this.types.forEach(type => {
                if (typeof type.parent === 'string') {
                    const [ fileIdentifier, fieldIdentifier ] = type.parent.split('.');
                    type.parent = this.file.dataset.get(fileIdentifier).get(fieldIdentifier);
                    type.parent.children.push(this);
                    type.name += ' (\'' + type.parent.getFullIdentifier() + '\')';
                } else if (type.isEnumeration()) {
                    type.name += ' (\'' + type.enumeration.name + '\')';
                }
            });
        }

        /**
         * @returns {!String}
         */
        getFullIdentifier() {
            return this.file.identifier + '.' + this.identifier;
        }
        /**
         * @returns {!Array.<!Entry>}
         */
        getEntries() {
            return this.file.records.flatMap(record => {
                const entry = record[this.identifier];
                return !entry.isEmpty() ? entry : [];
            });
        }
    }

    class FieldType {
        /**
         * @param {!Field} field
         * @param {!Structure} structure
         * @param {!Enumeration|undefined} enumeration
         * @param {!String} parent
         */
        constructor(field, structure, enumeration, parent) {
            /** @type {!Field} */
            this.field = field;

            /** @type {!String} */
            this.name = structure.name;

            /** @type {!Structure} */
            this.structure = structure;

            /** @type {?Enumeration} */
            this.enumeration = enumeration instanceof Enumeration ? enumeration : null;

            /** @type {?Field} - Can be a string until dataset is constructed. */
            this.parent = parent.length != 0 ? parent : null;
        }

        /**
         * @returns {!Boolean}
         */
        isChild() {
            return this.parent instanceof Field;
        }
        /**
         * @returns {!Boolean}
         */
        isEnumeration() {
            return this.enumeration instanceof Enumeration;
        }
        /**
         * @returns {!Boolean}
         */
        isParent() {
            return this.field.children.length != 0;
        }
    }

    class Record {
        /**
         * @param {!File} file
         * @param {!Boolean|undefined} isShadow
         */
        constructor(file, isShadow) {
            /** @type {!File} */
            this.__file = file;

            /** @type {!Boolean} */
            this.__isShadow = isShadow !== undefined ? isShadow : false;

            /** @type {!Number} */
            this.__index = file.records.length;
            
            file.fields.forEach(field => {
                Object.defineProperty(this, field.identifier, { enumerable: true, value: new Entry(this, field), writable: true });
                const entry = this[field.identifier];
                if (entry.isEnumeration() && entry.fieldType.enumeration.iBlank !== null) {
                    entry.set(entry.fieldType.enumeration.toHTML(''));
                }
            });
        }

        __afterDatasetLoaded() {
            this.__file.fields.forEach(field => this[field.identifier].afterDatasetLoaded());
        }

        /**
         * @param {?Record} other
         * @returns {!Boolean}
         */
        __isEqual(other) {
            return other instanceof Record && this.__file.identifier === other.__file.identifier && this.__index == other.__index;
        }
        /**
         * @returns {!Boolean}
         */
        __isParent() {
            for (const property in this) {
                const entry = this[property];
                if (entry instanceof Entry && entry.isParent()) {
                    return true;
                }
            }
            return false;
        }

        __delete() {
            this.__file.fields.forEach(field => this[field.identifier].clear());
            if (!this.__isShadow) {
                this.__file.records.splice(this.__index, 1);
                while (this.__index < this.__file.records.length) {
                    this.__file.records[this.__index++].__index -= 1;
                }
            }
        }

        /**
         * @returns {!Array.<!{ property: !String, value: !String }>}
         */
        __toArray() {
            const data = new Array();
            for (const __property in this) {
                const entry = this[__property];
                if (entry instanceof Entry && !entry.isEmpty()) {
                    data.push({ property: __property, value: entry.get() });
                }
            }
            return data;
        }
    }

    class Entry {
        /**
         * @param {!Record} record
         * @param {!Field} field
         */
        constructor(record, field) {
            /** @type {!Record} */
            this.record = record;

            /** @type {!Field} */
            this.field = field;

            /** @type {!FieldType} */
            this.fieldType = field.types[0];

            /** @type {?Entry|!String} */
            this.data = !this.record.__isShadow && this.isChild() ? null : '';

            /** @type {!Array.<!Entry>} */
            this.children = new Array();
        }

        afterDatasetLoaded() {
            if (this.isChild() && typeof this.data === 'string') {
                const data = this.data;
                this.data = null;
                if (data.length != 0) {
                    var record = this.fieldType.parent.file.records.find(record => {
                        const entry = record[this.fieldType.parent.identifier];
                        entry.afterDatasetLoaded();
                        return entry.get() === data;
                    });
                    switch (this.field.getFullIdentifier()) {
                        case 'trips.service_id':
                            if (record instanceof Record) {
                                this.set(record[this.fieldType.parent.identifier]);
                            } else {
                                this.setFieldType(this.field.types[1]);
                                record = this.fieldType.parent.file.records.find(record => {
                                    const entry = record[this.fieldType.parent.identifier];
                                    entry.afterDatasetLoaded();
                                    return entry.get() === data;
                                });
                                if (record instanceof Record) {
                                    this.set(record[this.fieldType.parent.identifier]);
                                } else {
                                    this.setFieldType(this.field.types[0]);
                                }
                            }
                            break;
                        case 'calendar_dates.service_id':
                            if (record instanceof Record) {
                                this.set(record[this.fieldType.parent.identifier]);
                            } else {
                                this.setFieldType('Id');
                                this.data = data;
                            }
                            break;
                        default:
                            if (record instanceof Record) {
                                this.set(record[this.fieldType.parent.identifier]);
                            }
                            break;
                    }
                }
            }
        }

        /**
         * @param {?Entry} other
         * @returns {!Boolean}
         */
        isEqual(other) {
            return other instanceof Entry && this.record.__isEqual(other.record) && this.field.identifier === other.field.identifier;
        }
        /**
         * @returns {!Boolean}
         */
        isChild() {
            return this.fieldType.isChild();
        }
        /**
         * @returns {!Boolean}
         */
        isEmpty() {
            return !this.record.__isShadow && this.isChild() ? this.data === null : this.data.length == 0;
        }
        /**
         * @returns {!Boolean}
         */
        isEnumeration() {
            return this.fieldType.isEnumeration();
        }
        /**
         * @returns {!Boolean}
         */
        isParent() {
            return this.fieldType.isParent() && !this.isEmpty();
        }
        
        /**
         * @returns {!String}
         */
        get() {
            return !this.record.__isShadow && this.isChild() ? this.data !== null ? this.data.get() : '' : this.data;
        }
        /**
         * @returns {?Array.<!Entry>}
         */
        getPossibleParents() {
            return this.isChild() ? this.fieldType.parent.getEntries() : null;
        }
        /**
         * @returns {?Array.<!String>}
         */
        getEnumerationValues() {
            return this.isEnumeration() ? this.fieldType.enumeration.values : null;
        }

        /**
         * @param {?Entry|!String} data
         * @returns {!Boolean}
         */
        set(data) {
            if (!this.record.__isShadow && this.isChild() && typeof data === 'string') {
                const record = this.fieldType.parent.file.records.find(record => record[this.fieldType.parent.identifier].get() === data);
                data = record instanceof Record ? record[this.fieldType.parent.identifier] : null;
            }
            if (!this.record.__isShadow && this.isChild()) {
                if (data === null || data.isEmpty()) {
                    return this.clear();
                }
                if (data.isEqual(this.data)) {
                    return false;
                }
                if (this.data instanceof Entry) {
                    this.data.children.splice(this.data.children.findIndex(entry => entry.isEqual(this)), 1);
                }
                data.children.push(this);
            } else {
                if (data.length == 0) {
                    return this.clear();
                }
                if (this.data === data) {
                    return false;
                }
                /*
                 * comment: definitely useful, but to complex for user maybe
                 * if (this.fieldType.structure.identifier === 'Id' && this.field.getEntries().find(entry => entry.get() === data) instanceof Entry) {
                 *     return false;
                 * }
                 */
            }
            this.data = data;
            return true;
        }
        /**
         * @param {?FieldType|!String} data
         * @returns {!Boolean}
         */
        setFieldType(data) {
            if (typeof data === 'string') {
                const fieldType = this.field.types.find(fieldType => fieldType.name === data);
                data = fieldType !== undefined ? fieldType : null;
            }
            if (data === null || this.fieldType.name === data.name) {
                return false;
            }
            this.data.clear();
            this.fieldType = data;
            this.data = this.isChild() ? null : '';
            return true;
        }

        /**
         * @returns {!Boolean}
         */
        clear() {
            if (this.isEnumeration() && this.fieldType.enumeration.iBlank !== null) {
                return this.set(this.fieldType.enumeration.toHTML(''));
            }
            if (this.isEmpty()) {
                return false;
            }
            if (this.record.__isShadow) {
                this.data = '';
            } else {
                if (this.isChild()) {
                    this.data.children.splice(this.data.children.findIndex(entry => entry.isEqual(this)), 1);
                }
                this.children.forEach(entry => entry.clear());
                this.children.length = 0;
                this.data = this.isChild() ? null : '';
            }
            return true;
        }
    }

    class Table {
        /**
         * @param {!Dataset} dataset
         * @param {!String} fileIdentifier
         * @param {?Array.<!String>} fieldIdentifiers
         * @param {?Function} callback
         * @param {!Function|undefined} filter
         */
        constructor(dataset, fileIdentifier, fieldIdentifiers, callback, filter) {
            /** @type {!Dataset} */
            this.dataset = dataset;

            /** @type {?File} */
            this.file = dataset.get(fileIdentifier);

            /** @type {!Array.<?Field>} */
            this.fields = fieldIdentifiers === null ? this.file.fields : fieldIdentifiers.map(fieldIdentifier => this.file.get(fieldIdentifier));

            /** @type {!Function} */
            this.callback = callback;

            /** @type {?Function} */
            this.filter = filter !== undefined ? filter : null;

            /** @type {!Number} */
            this.currentPage = 1;

            /** @type {!Number} */
            this.perPage = 10;

            /** @type {!Number} */
            this.key = 0;
        }

        /**
         * @returns {!Array.<!{ key: !String, label: !String, sortable: !Boolean }>}
         */
        getFields() {
            return this.fields.flatMap(field => {
                return field instanceof Field ? { key: field.identifier, label: field.description, sortable: true } : [];
            }).concat([ { key: '__actions', label: '', sortable: false } ]);
        }
        /**
         * @returns {!Array.<!Record>}
         */
        getRecords() {
            return this.filter !== null ? this.file.records.filter(record => this.filter(record)) : this.file.records;
        }

        createRecord () {
            this.file.createRecord();
            this.key += 1;
        }
        /**
         * @param {!Record} record
         */
        deleteRecord(record) {
            record.__delete();
            this.key += 1;
        }

        /**
         * @param {!Record} a
         * @param {!Record} b
         * @param {!String} fieldIdentifier
         * @returns {!Number}
         */
        comparator(a, b, fieldIdentifier) {
            a = a[fieldIdentifier];
            b = b[fieldIdentifier];
            return a instanceof Entry && b instanceof Entry ? a.get() < b.get() ? -1 : b.get() < a.get() ? 1 : 0 : 0;
        }
        /**
         * @param {!String} text
         * @returns {!String}
         */
        formator(text) {
            const words = text.split('_').map(word => word.length != 0 ? word[0].toUpperCase() + word.slice(1) : '');
            return words.join(' ').trim();
        }
    }

    class Station {
        /**
         * @param {!Record} station
         * @param {!Object} vue
         */
        constructor(station, vue) {
            /** @type {!Object} */
            this.vue = vue;

            /** @type {!Dataset} */
            this.dataset = station.__file.dataset;

            /** @type {!Record} */
            this.record = station;

            /** @type {!Object} */
            this.tree = new Object();

            /** @type {!Array.<!{ title: !String, table: !Array.<!Object> }>} */
            this.mockups = [
                { title: 'Station', table: new Array() },
                { title: 'Stop', table: new Array() },
                { title: 'Transfers', table: new Array() },
                { title: 'Pathways', table: new Array() }
            ];

            /** @type {!Number} */
            this.key = 0;

             /** @type {!Array.<!String>} */
            this.stationFields = [ 'stop_id', 'stop_name', 'location_type', 'platform_code', '__action' ];

            /** @type {!Function} */
            this.stationHandler = (type, object) => {
                const shadow = this.dataset.get('stops').shadowRecord;
                switch (type) {
                    case 'add':
                        shadow.__file.addShadowRecord();
                        shadow['parent_station'].set(this.record['stop_id'].get());
                        this.update('tree');
                        this.stationKey += 1;
                        return;
                    case 'delete':
                        object.__delete();
                        this.update('tree');
                        this.stationKey += 1;
                        return;
                    case 'refresh':
                        this.stationKey += 1;
                        return;
                    case 'shadow':
                        return shadow;
                    default:
                        return;
                }
            };

            /** @type {!Number} */
            this.stationKey = 1000;

            this.stationRefresh = () => {
                this.update('full');
                this.key += 1;
            }

            /** @type {!Number} */
            this.mapKey = 2000;

            /** @type {!Function} */
            this.transferFields = () => [ 'from_stop_id', 'to_stop_id', 'transfer_type', 'min_transfer_time', '__action' ];

            /** @type {!Function} */
            this.transferItems = () => {
                const __filter = record => this.tree.contains(record['from_stop_id'].get()) || this.tree.contains(record['to_stop_id'].get());
                const items = this.dataset.get('transfers').records.filter(__filter);
                const shadow = this.dataset.get('transfers').shadowRecord;
                shadow.__delete();
                shadow['from_stop_id'].set(this.record['stop_id'].get());
                return items.concat([ shadow ]);
            };

            /** @type {!Number} */
            this.transfersKey = 3000;

            /** @type {!Function} */
            this.pathwayFields = () => [ 'from_stop_id', 'to_stop_id', 'pathway_mode', 'is_bidirectional', 'length', 'traversal_time', 'stair_count', '__action' ];

            /** @type {!Function} */
            this.pathwayItems = () => {
                const __filter = record => this.tree.contains(record['from_stop_id'].get()) || this.tree.contains(record['to_stop_id'].get());
                const items = this.dataset.get('pathways').records.filter(__filter);
                const shadow = this.dataset.get('pathways').shadowRecord;
                shadow.__delete();
                shadow['from_stop_id'].set(this.record['stop_id'].get());
                return items.concat([ shadow ]);
            };

            /** @type {!Number} */
            this.pathwaysKey = 4000;

            this.afterConstructed();
        }

        afterConstructed() {
            this.mockups.find(mockup => mockup.title === 'Station').table.push({
                key: 'station-row-1',
                data: [
                    { action: { icon: null, text: null, special: 'stops.station' }, colspan: 1, rowspan: 1 },
                    { action: { icon: null, text: null, special: 'stops.map' }, colspan: 1, rowspan: 1 }
                ]
            });

            this.mockups.find(mockup => mockup.title === 'Stop').table.push({
                key: 'stop-row-1',
                data: [
                    { action: null, colspan: 1, entry: this.record['stop_id'], label: 'Stop ID', rowspan: 1 },
                    { action: null, colspan: 2, entry: this.record['stop_name'], label: 'Stop Name', rowspan: 1 },
                    { action: null, colspan: 1, entry: this.record['stop_lat'], label: 'Latitude', rowspan: 1 },
                    { action: null, colspan: 1, entry: this.record['stop_lon'], label: 'Longitude', rowspan: 1 }
                ]
            });
            this.mockups.find(mockup => mockup.title === 'Stop').table.push({
                key: 'stop-row-2',
                data: [
                    { action: null, colspan: 1, entry: this.record['location_type'], label: 'Type', rowspan: 1 },
                    { action: null, colspan: 2, entry: this.record['parent_station'], label: 'Parent Station', rowspan: 1 },
                    { action: null, colspan: 2, entry: this.record['stop_desc'], label: 'Description', rowspan: 2 }
                ]
            });
            this.mockups.find(mockup => mockup.title === 'Stop').table.push({
                key: 'stop-row-3',
                data: [
                    { action: null, colspan: 1, entry: this.record['stop_code'], label: 'Stop Code', rowspan: 1 },
                    { action: null, colspan: 2, entry: this.record['level_id'], label: 'Level ID', rowspan: 1 }
                ]
            });
            this.mockups.find(mockup => mockup.title === 'Stop').table.push({
                key: 'stop-row-4',
                data: [
                    { action: null, colspan: 1, entry: this.record['platform_code'], label: 'Platform Code', rowspan: 1 },
                    { action: null, colspan: 1, entry: this.record['stop_timezone'], label: 'Timezone', rowspan: 1 },
                    { action: null, colspan: 1, entry: this.record['wheelchair_boarding'], label: 'Wheelchair Boarding', rowspan: 1 },
                    { action: null, colspan: 2, entry: this.record['stop_url'], label: 'URL', rowspan: 1 }
                ]
            });

            this.mockups.find(mockup => mockup.title === 'Transfers').table.push({
                key: 'transfers-row-1',
                data: [
                    { action: { icon: null, text: null, special: 'stops.transfers' }, colspan: 1, rowspan: 1 }
                ]
            });

            this.mockups.find(mockup => mockup.title === 'Pathways').table.push({
                key: 'pathways-row-1',
                data: [
                    { action: { icon: null, text: null, special: 'stops.pathways' }, colspan: 1, rowspan: 1 }
                ]
            });

            this.dataset.get('stops').shadowRecord.__delete();
            this.dataset.get('stops').shadowRecord['parent_station'].set(this.record['stop_id'].get());
            this.update('full');
        }

        /**
         * @param {!String} updateKey
         */
        update(updateKey) {
            switch (updateKey) {
                case 'full':
                    // fallsthrough
                case 'tree':
                    this.tree = gtfsStopTree(this.record);
                    if (updateKey !== 'full') {
                        break;
                    }
                    // fallsthrough
                default:
                    break;
            }
        }

        /**
         * @param {!Entry} entry
         * @param {!String} data
         */
        set(entry, data) {
            if (entry.set(data) && !entry.record.__isShadow) {
                switch (entry.field.getFullIdentifier()) {
                    default:
                        break;
                }
            }
        }
    }

    class Trip {
        /**
         * @param {!Record} trip
         * @param {!Object} vue
         */
        constructor(trip, vue) {
            /** @type {!Object} */
            this.vue = vue;

            /** @type {!Dataset} */
            this.dataset = trip.__file.dataset;

            /** @type {!Record} */
            this.record = trip;

            /** @type {!Array.<!{ title: !String, table: !Array.<!Object> }>} */
            this.mockups = [
                { title: 'Trip', table: new Array() },
                { title: 'Route', table: new Array() },
                { title: 'Service Days', table: new Array() },
                { title: 'Stops', table: new Array() },
                { title: 'Frequencies', table: new Array() }
            ];

            /** @type {!Number} */
            this.key = 0;

            /** @type {!Array.<!{ key: !String, highlight: !String, dates: ?Object }>} */
            this.calendar = [
                { key: 'range', highlight: 'blue', dates: null },
                { key: 'removed', highlight: 'red', dates: null },
                { key: 'added', highlight: 'green', dates: null }
            ];

            /** @type {!Number} */
            this.calendarKey = 1000;

            /** @type {!Function} */
            this.stopFields = () => [ 'stop_id', 'arrival_time', 'departure_time', 'pickup_type', 'drop_off_type', 'stop_headsign', '__action' ];

            /** @type {!Function} */
            this.stopItems = () => {
                const __sort = (a, b) => a['stop_sequence'].get() < b['stop_sequence'].get() ? 0 : 1;
                const items = this.record['trip_id'].children.filter(child => child.field.file.identifier === 'stop_times').map(entry => entry.record);
                const shadow = this.dataset.get('stop_times').shadowRecord;
                const tripID = this.record['trip_id'].get();
                const stop_sequence = this.dataset.get('stop_times').records.reduce((maximum, record) => {
                    const value = parseInt(record['stop_sequence'].get(), 10);
                    return record['trip_id'].get() === tripID && maximum < value ? value : maximum;
                }, 0);
                shadow.__delete();
                shadow['trip_id'].set(tripID);
                shadow['stop_sequence'].set((stop_sequence + 1).toString());
                return items.sort(__sort).concat([ shadow ]);
            };

            /** @type {!Function} */
            this.stopMove = (index, direction) => {
                const stop_times = this.stopItems();
                if (direction === 'up' ? 0 < index : index + 1 < stop_times.length ) {
                    const other = stop_times[direction === 'up' ? index - 1 : index + 1];
                    const stop_sequence = stop_times[index]['stop_sequence'].get();
                    stop_times[index]['stop_sequence'].set(other['stop_sequence'].get());
                    other['stop_sequence'].set(stop_sequence);
                    this.stopsKey += 1;
                }
            }
            
            /** @type {!Number} */
            this.stopsKey = 2000;

            /** @type {!Function} */
            this.frequencyFields = () => [ 'start_time', 'end_time', 'headway_secs', 'exact_times', '__action' ];

            /** @type {!Function} */
            this.frequencyItems = () => {
                const items = this.record['trip_id'].children.filter(child => child.field.file.identifier === 'frequencies').map(entry => entry.record);
                const shadow = this.dataset.get('frequencies').shadowRecord;
                shadow.__delete();
                shadow['trip_id'].set(this.record['trip_id'].get());
                return items.concat([ shadow ]);
            };

            /** @type {!Number} */
            this.frequenciesKey = 3000;

            this.afterConstructed();
        }

        afterConstructed() {
            this.mockups.find(mockup => mockup.title === 'Trip').table.push({
                key: 'trip-row-1',
                data: [
                    { action: null, colspan: 1, entry: this.record['trip_id'], label: 'Trip ID', rowspan: 1 },
                    { action: null, colspan: 1, entry: this.record['trip_short_name'], label: 'Short Name', rowspan: 1 },
                    { action: null, colspan: 2, entry: this.record['trip_headsign'], label: 'Headsign', rowspan: 1 }
                ]
            });
            this.mockups.find(mockup => mockup.title === 'Trip').table.push({
                key: 'trip-row-2',
                data: [
                    { action: null, colspan: 1, entry: this.record['block_id'], label: 'Block ID', rowspan: 1 },
                    { action: null, colspan: 1, entry: this.record['direction_id'], label: 'Direction', rowspan: 1 },
                    { action: null, colspan: 1, entry: this.record['wheelchair_accessible'], label: 'Wheelchair Accessible', rowspan: 1 },
                    { action: null, colspan: 1, entry: this.record['bikes_allowed'], label: 'Bikes Allowed', rowspan: 1 }
                ]
            });

            const createRoute = {
                callback: () => this.vue.texterWrapper = {
                    callback: routeID => {
                        const route = this.dataset.get('routes').createRecord([{ property: 'route_id', value: routeID }]);
                        this.set(this.record['route_id'], route['route_id']);
                    },
                    title: 'Route ID'
                },
                icon: null,
                text: 'New'
            };
            this.mockups.find(mockup => mockup.title === 'Route').table.push({
                key: 'route-row-1',
                data: [
                    { action: null, colspan: 1, entry: this.record['route_id'], label: 'Route ID', rowspan: 1 },
                    { action: createRoute, colspan: 2, entry: null, label: null, rowspan: 1 }
                ]
            });

            const createService = {
                callback: () => this.vue.texterWrapper = {
                    callback: serviceID => {
                        const service = this.dataset.get('calendar').createRecord([{ property: 'service_id', value: serviceID }]);
                        this.set(this.record['service_id'], service['service_id']);
                    },
                    title: 'Service ID'
                },
                icon: null,
                text: 'New'
            };
            this.mockups.find(mockup => mockup.title === 'Service Days').table.push({
                key: 'service-days-row-1',
                data: [
                    { action: null, colspan: 2, entry: this.record['service_id'], label: 'Service ID', rowspan: 1 },
                    { action: createService, colspan: 7, entry: null, label: null, rowspan: 1 }
                ]
            });

            this.mockups.find(mockup => mockup.title === 'Stops').table.push({
                key: 'stops-row-1',
                data: [
                    { action: { icon: null, text: null, special: 'trips.stop_times' }, colspan: 1, rowspan: 1 }
                ]
            });

            this.mockups.find(mockup => mockup.title === 'Frequencies').table.push({
                key: 'frequencies-row-1',
                data: [
                    { action: { icon: null, text: null, special: 'trips.frequencies' }, colspan: 1, rowspan: 1 }
                ]
            });

            this.update('full');
        }

        /**
         * @param {!String} updateKey
         */
        update(updateKey) {
            const routeTable = this.mockups.find(mockup => mockup.title === 'Route').table;
            const route = !this.record['route_id'].isEmpty() ? this.record['route_id'].data.record : null;

            const serviceDaysTable = this.mockups.find(mockup => mockup.title === 'Service Days').table;
            const service = !this.record['service_id'].isEmpty() ? this.record['service_id'].data.record : null;
            const startDate = service instanceof Record ? service['start_date'] : null;
            const endDate = service instanceof Record ? service['end_date'] : null;

            switch (updateKey) {
                case 'full':
                    routeTable.length = 1;
                    if (route instanceof Record) {
                        routeTable.push({
                            key: 'route-row-2',
                            data: [
                                { action: null, colspan: 1, entry: route['agency_id'], label: 'Agency ID', rowspan: 1 },
                                { action: null, colspan: 1, entry: route['route_short_name'], label: 'Short Name', rowspan: 1 },
                                { action: null, colspan: 1, entry: route['route_long_name'], label: 'Long Name', rowspan: 1 }
                            ]
                        });
                        routeTable.push({
                            key: 'route-row-3',
                            data: [
                                { action: null, colspan: 1, entry: route['route_type'], label: 'Type', rowspan: 1 },
                                { action: null, colspan: 1, entry: route['route_sort_order'], label: 'Sort Order', rowspan: 1 },
                                { action: null, colspan: 1, entry: route['route_desc'], label: 'Description', rowspan: 2 }
                            ]
                        });
                        routeTable.push({
                            key: 'route-row-4',
                            data: [
                                { action: null, colspan: 1, entry: route['route_color'], label: 'Color', rowspan: 1 },
                                { action: null, colspan: 1, entry: route['route_text_color'], label: 'Text Color', rowspan: 1 }
                            ]
                        });
                        routeTable.push({
                            key: 'route-row-5',
                            data: [
                                { action: null, colspan: 1, entry: route['continuous_pickup'], label: 'Continuous Pickup', rowspan: 1 },
                                { action: null, colspan: 1, entry: route['continuous_drop_off'], label: 'Continuous Drop Off', rowspan: 1 },
                                { action: null, colspan: 1, entry: route['route_url'], label: 'URL', rowspan: 1 }
                            ]
                        });
                    }

                    serviceDaysTable.length = 1;
                    if (service instanceof Record) {
                        serviceDaysTable.push({
                            key: 'service-days-row-2',
                            data: [
                                { action: null, colspan: 1, entry: service['start_date'], label: 'Start Date', rowspan: 1 },
                                { action: null, colspan: 1, entry: service['end_date'], label: 'End Date', rowspan: 1 },
                                { action: null, colspan: 1, entry: service['monday'], label: 'Monday', rowspan: 1 },
                                { action: null, colspan: 1, entry: service['tuesday'], label: 'Tuesday', rowspan: 1 },
                                { action: null, colspan: 1, entry: service['wednesday'], label: 'Wednesday', rowspan: 1 },
                                { action: null, colspan: 1, entry: service['thursday'], label: 'Thursday', rowspan: 1 },
                                { action: null, colspan: 1, entry: service['friday'], label: 'Friday', rowspan: 1 },
                                { action: null, colspan: 1, entry: service['saturday'], label: 'Saturday', rowspan: 1 },
                                { action: null, colspan: 1, entry: service['sunday'], label: 'Sunday', rowspan: 1 }
                            ]
                        });
                    }
                    // fallsthrough
                case 'calendar':
                    if (serviceDaysTable.length < 3 && service instanceof Record && !startDate.isEmpty() && !endDate.isEmpty()) {
                        serviceDaysTable.push({
                            key: 'service-days-row-3',
                            data: [
                                { action: { icon: null, text: null, special: 'trips.calendar' }, colspan: 9, rowspan: 1 }
                            ]
                        });
                    }
                    if (service instanceof Record && !startDate.isEmpty() && !endDate.isEmpty()) {
                        const added = this.dataset.get('calendar_dates').get('exception_type').types[0].enumeration.toHTML('1');
                        const removed = this.dataset.get('calendar_dates').get('exception_type').types[0].enumeration.toHTML('2');
                        this.calendar.find(element => element.key === 'range').dates = {
                            start: gtfsDate(startDate),
                            end: gtfsDate(endDate),
                            weekdays: [ 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday' ].flatMap((property, index) => {
                                return service[property].get() === 'true' ? index + 1 : [];
                            })
                        };
                        this.calendar.find(element => element.key === 'added').dates = service['service_id'].children.flatMap(date => {
                            if (date.field.file.identifier !== 'calendar_dates' || date.record['date'].isEmpty()) {
                                return [];
                            }
                            return date.record['exception_type'].get() === added ? gtfsDate(date.record['date']) : [];
                        });
                        this.calendar.find(element => element.key === 'removed').dates = service['service_id'].children.flatMap(date => {
                            if (date.field.file.identifier !== 'calendar_dates' || date.record['date'].isEmpty()) {
                                return [];
                            }
                            return date.record['exception_type'].get() === removed ? gtfsDate(date.record['date']) : [];
                        });      
                    }
                    if (updateKey !== 'full') {
                        break;
                    }
                    // fallsthrough
                default:
                    break;
            }
        }

        handleDate() {
            if (this.mockups.find(mockup => mockup.title === 'Service Days').table.find(row => row.key === 'service-days-row-3')) {
                const calenderDates = this.dataset.get('calendar_dates');
                const serviceID = this.record['service_id'].get();
                const pickedData = gtfsDate(this.vue.pickerDate);
                const record = calenderDates.records.find(record => record['service_id'].get() === serviceID && record['date'].get() === pickedData);
                if (record instanceof Record) {
                    record.__delete();
                } else {
                    const range = this.calendar.find(element => element.key === 'range').dates;
                    const pickedDay = this.vue.pickerDate.getDay() + 1;
                    const inRange = range.start <= this.vue.pickerDate
                        && this.vue.pickerDate <= range.end
                        && range.weekdays.find(day => day == pickedDay) !== undefined;
                    calenderDates.createRecord([
                        { property: 'service_id', value: serviceID },
                        { property: 'date', value: pickedData },
                        { property: 'exception_type', value: calenderDates.get('exception_type').types[0].enumeration.toHTML(inRange ? '2' : '1') }
                    ]);
                }
                this.vue.pickerDate = null;
                this.update('calendar');
                this.calendarKey += 1;
            }
        }
        /**
         * @param {!Entry} entry
         * @param {!String} data
         */
        set(entry, data) {
            if (entry.set(data) && !entry.record.__isShadow) {
                switch (entry.field.getFullIdentifier()) {
                    case 'trips.route_id':
                        // fallsthrough
                    case 'trips.service_id':
                        this.update('full');
                        this.key += 1;
                        break;
                    case 'calendar.start_date':
                        // fallsthrough
                    case 'calendar.end_date':
                        // fallsthrough
                    case 'calendar.monday':
                        // fallsthrough
                    case 'calendar.tuesday':
                        // fallsthrough
                    case 'calendar.wednesday':
                        // fallsthrough
                    case 'calendar.thursday':
                        // fallsthrough
                    case 'calendar.friday':
                        // fallsthrough
                    case 'calendar.saturday':
                        // fallsthrough
                    case 'calendar.sunday':
                        this.update('calendar');
                        this.calendarKey += 1;
                        break;
                    default:
                        break;
                }
            }
        }
    }

    export default {
        name: 'App',
        components: {
            SimpleMap,
            SimpleTable,
            SimpleTree,
            Texter
        },

        data() {
            return {
                /** @type {?{ callback: !Function, title: !String }} */
                texterWrapper: null,

                /** @type {!Dataset} */
                dataset: null,

                /** @type {?Table} */
                table: null,

                /** @type {?Station} */
                station: null,

                /** @type {?Trip} */
                trip: null,

                /** @type {?Object} */
                divers: null,

                /** @type {?Date} */
                pickerDate: null
            };
        },
        mounted() {
            $("#open-button").click(() => $("#open-input").click());

            if (process.env.NODE_ENV === 'production') {
                this.dataset = new Dataset(new DOMParser().parseFromString(getXML(), 'text/xml'));
            } else {
                var httpRequest = new XMLHttpRequest();
                httpRequest.onreadystatechange = () => {
                    if (httpRequest.readyState == 4 && httpRequest.status == 200) {
                        this.dataset = new Dataset(new DOMParser().parseFromString(httpRequest.responseText, 'application/xml'));
                    }
                };
                httpRequest.open('GET', 'http://localhost:8080/gtfs-static.xml', true);
                httpRequest.send();
            }
        },

        watch: {
            pickerDate(value) {
                if (value instanceof Date && this.trip instanceof Trip) {
                    this.trip.handleDate(value);
                }
            }
        },

        methods: {
            createDataset() {
                this.table = null;
                this.divers = null;
                this.station = null;
                this.trip = null;
                this.texterWrapper = { title: 'Filename', callback: filename => this.dataset.reset(filename) };
            },
            /**
             * @param {!Object} event
             */
            loadDataset(event) {
                this.table = null;
                this.divers = null;
                this.station = null;
                this.trip = null;
                this.dataset.load(event);
            },

            /**
             * @param {!String} fileIdentifier
             */
            createTable(fileIdentifier) {
                this.divers = null;
                this.station = null;
                this.trip = null;
                const station = this.dataset.get('stops').get('location_type').types[0].enumeration.toHTML('1');
                switch(fileIdentifier) {
                    case '__stops':
                        this.table = new Table(
                            this.dataset,
                             'stops',
                            [ 'stop_id', 'stop_code', 'stop_name', 'stop_desc', 'stop_lat', 'stop_lon' ],
                            this.selectStation,
                            record => !record['stop_id'].isEmpty() && record['location_type'].get() === station
                        );
                        break;
                    case '__trips':
                        this.table = new Table(
                            this.dataset,
                            'trips',
                            [ 'route_id', 'service_id', 'trip_id', 'trip_headsign', 'trip_short_name' ],
                            this.selectTrip,
                            record => !record['trip_id'].isEmpty()
                        );
                        break;
                    default:
                        this.table = new Table(this.dataset, fileIdentifier, null, null);
                        break;
                }
            },
            createStation() {
                const station = this.dataset.get('stops').get('location_type').types[0].enumeration.toHTML('1');
                this.texterWrapper = {
                    callback: stopID => this.selectStation(this.dataset.get('stops').createRecord([
                        { property: 'stop_id', value: stopID },
                        { property: 'location_type', value: station }
                    ])),
                    title: 'Stop ID'
                };
            },
            createTrip() {
                this.texterWrapper = {
                    callback: tripID => this.selectTrip(this.dataset.get('trips').createRecord([ { property: 'trip_id', value: tripID } ])),
                    title: 'Trip ID'
                };
            },

            /**
             * @param {!Record} station
             */
            selectStation(station) {
                this.table = null;
                this.trip = null;
                this.station = station.__file.identifier === 'stops' ? new Station(station, this) : null;
                this.divers = this.station;
            },
            /**
             * @param {!Record} trip
             */
            selectTrip(trip) {
                this.table = null;
                this.station = null;
                this.trip = trip.__file.identifier === 'trips' ? new Trip(trip, this) : null;
                this.divers = this.trip;
            },

            closeTexter() {
                this.texterWrapper = null;
            }
        }
    }
</script>

<style>
    #open-input {
        display: none;
    }
</style>
