import VueRouter from 'vue-router';
import Vue from 'vue';
import QueryPage from '../views/QueryPage.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'Query',
    component: QueryPage,
  },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

export default router;
