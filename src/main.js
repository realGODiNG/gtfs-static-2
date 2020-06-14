import Vue from 'vue'
import { BootstrapVue, BootstrapVueIcons } from 'bootstrap-vue'
import { Plugin } from 'vue-fragment'
import VueResizeText from 'vue-resize-text'
import VueInputAutowidth from 'vue-input-autowidth'
import VCalendar from 'v-calendar'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import App from './App.vue'

Vue.use(BootstrapVue);
Vue.use(BootstrapVueIcons);
Vue.use(Plugin);
Vue.use(VueResizeText);
Vue.use(VueInputAutowidth);
Vue.use(VCalendar);

Vue.config.productionTip = false;

new Vue({ render: h => h(App) }).$mount('#app');
