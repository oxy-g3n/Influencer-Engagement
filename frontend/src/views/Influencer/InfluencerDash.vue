<!-- src/views/DashboardLayout.vue -->
<template>
    <div class="dashboard-layout">
      <influencerNav />
      <div class="container mt-4">
        <router-view></router-view> <!-- Dynamic content will be loaded here -->
      </div>
    </div>
  </template>
  
  <script>
  import influencerNav from '@/components/influencerNav.vue';
  
  export default {
    name: 'InfluencerDash',
    components: {
      influencerNav
    },
    created() {
      this.$router.push('/InfluencerDash/Requests');
    }
  }
  </script>
  
  <style scoped>
  .dashboard-layout {
    background-color: #7f8c8d; /* Dark blue background */
    color: white; /* Optional: Adjust text color for better contrast */
    min-height: 100vh; /* Ensure it covers the full viewport height */
    display: flex;
    flex-direction: column;
  }
  
  .container {
    padding-top: 20px;
  }
  </style>
  