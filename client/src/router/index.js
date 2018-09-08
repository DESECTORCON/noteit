import Vue from 'vue';
import Router from 'vue-router';
import Ping from '@/components/Ping';
import Books from '@/components/pub_notes';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/pubnotes',
      name: 'pubnotes',
      component: Books,
    },
    {
      path: '/ping',
      name: 'Ping',
      component: Ping,
    },
  ],
  mode: 'hash',
});
