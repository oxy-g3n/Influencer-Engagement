<!-- src/views/DashboardLayout.vue -->
<template>
    <div class="dashboard-layout">
      <sponsorNav />
      <div class="container mt-4">
        <router-view></router-view> <!-- Dynamic content will be loaded here -->
      </div>
    </div>
  </template>
  
  <script>
  import sponsorNav from '@/components/sponsorNav.vue';
  
  export default {
    name: 'SponsorDash',
    components: {
      sponsorNav
    },
    created() {
      this.$router.push('/SponsorDash/Campaigns');
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
  