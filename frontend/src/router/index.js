import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '../views/Login.vue'

//influencer imports
import InfluencerDash from '@/views/Influencer/InfluencerDash.vue'
import RegisterInfluencer from '@/views/Influencer/RegisterInfluencer.vue'
import EditInfluencer from '@/views/Influencer/EditInfluencer.vue'
import InfluencerRequests from '@/views/Influencer/InfluencerRequests.vue'
import InfluencerStats from '@/views/Influencer/InfluencerStats.vue'
import SearchCampaigns from '@/views/Influencer/SearchCampaigns.vue'

//sponsor imports
import SponsorDash from '@/views/sponsor/SponsorDash.vue'
import RegisterSponsor from '@/views/sponsor/RegisterSponsor.vue'
import Campaigns from '@/views/sponsor/Campaigns.vue'
import EditSponsor from '@/views/sponsor/EditSponsor.vue'
import SearchInfluencers from '@/views/sponsor/SearchInfluencers.vue'
import SponsorStats from '@/views/sponsor/SponsorStats.vue'

//admin imports
import AdminDash from '@/views/admin/AdminDash.vue'
import AnF from '@/views/admin/AnF.vue'
import CampaignsFlagging from '@/views/admin/CampaignsFlagging.vue'
import Stats from '@/views/admin/Stats.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/InfluencerRegistration',
    name: 'Influencer Registration',
    component: RegisterInfluencer
  },
  {
    path: '/SponsorRegistration',
    name: 'Sponsor Registration',
    component: RegisterSponsor
  },
  //Sponsor Dashboard with navbar and child components
  {
    path: "/SponsorDash",
    name: "SponsorDash",
    component: SponsorDash,
    children:
    [
      {
        path: 'SponsorStats',
        name: 'SponsorStats',
        component: SponsorStats
      },
      {
        path: 'Campaigns',
        name: 'Campaigns',
        component: Campaigns
      },      
      {
        path: 'editProfile',
        name: 'editProfile',
        component: EditSponsor
      },
      {
        path: 'Search',
        name: 'Search',
        component: SearchInfluencers
      },
    ]
  },
//Influencer Dashboard with navbar and child components
{
  path: '/InfluencerDash',
  name: 'InfluencerDash',
  component: InfluencerDash,
  children: [
    {
      path: 'SearchCampaigns',
      name: 'SearchCampaigns',
      component: SearchCampaigns
    },
    {
      path: 'InfluencerStats',
      name: 'InfluencerStats',
      component: InfluencerStats
    },
    {
      path: 'Requests',
      name: 'Requests',
      component: InfluencerRequests
    },
    {
      path: 'editProf',
      name: 'editProf',
      component: EditInfluencer
    }
  ]
},
//Admin Dashboard with navbar and child components
  {
    path: "/AdminDash",
    name: "AdminDash",
    component: AdminDash,
    children:[
      {
        path: 'AnF',
        name: 'AnF',
        component: AnF
      },
      {
        path: 'CampaignsFlagging',
        name: 'CampaignsFlagging',
        component: CampaignsFlagging
      },
      {
        path: 'Stats',
        name: 'Stats',
        component: Stats
      },

    ]
  },
  

]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
