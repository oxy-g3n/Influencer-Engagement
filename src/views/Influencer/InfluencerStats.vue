<template>
    <div class="dashboard-container">
      <h2>Influencer Statistics Dashboard</h2>
      
      <div v-if="loading" class="loading">Loading data...</div>
      <div v-else>
        <!-- Stats Cards -->
        <div class="stats-cards">
          <div class="stat-card">
            <h3>Total Requests</h3>
            <p>{{ totalRequests }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Rejected</h3>
            <p>{{ totalRejected }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Accepted</h3>
            <p>{{ totalAccepted }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Completed</h3>
            <p>{{ totalCompleted }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Open</h3>
            <p>{{ totalOpen }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Withdrawn</h3>
            <p>{{ totalWithdrawn }}</p>
          </div>
        </div>
  
        <!-- Influencer Details -->
        <div class="table-container">
          <h3>Influencer Details</h3>
          <table class="requests-table" v-if="influencerData">
            <tbody>
              <tr>
                <th>Full Name</th>
                <td>{{ influencerData.full_name }}</td>
                <th>Username</th>
                <td>{{ influencerData.username }}</td>
              </tr>
              <tr>
                <th>Influencer Name</th>
                <td>{{ influencerData.influencer_name }}</td>
                <th>Email</th>
                <td>{{ influencerData.mail }}</td>
              </tr>
              <tr>
                <th>Category</th>
                <td>{{ influencerData.category }}</td>
                <th>Niche</th>
                <td>{{ influencerData.niche }}</td>
              </tr>
              <tr>
                <th>Reach</th>
                <td>{{ influencerData.reach }}</td>
                <th>Join Date</th>
                <td>{{ formatDate(influencerData.date_created) }}</td>
              </tr>
              <tr>
                <th>Status</th>
                <td>{{ influencerData.approval ? 'Approved' : 'Pending' }}</td>
                <th>Account Flag</th>
                <td>{{ influencerData.flag ? 'Flagged' : 'Normal' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
  
        <!-- Charts -->
        <div class="charts-container">
          <div class="chart">
            <h3>Campaign Request Distribution</h3>
            <canvas ref="campaignChartRef"></canvas>
          </div>
          <div class="chart">
            <h3>Request Status Distribution</h3>
            <canvas ref="statusChartRef"></canvas>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import Chart from 'chart.js/auto';
  import { ref, onMounted, computed } from 'vue';
  import VueJwtDecode from 'vue-jwt-decode';
  
  export default {
    name: 'InfluencerStats',
    setup(props) {
      const influencerData = ref(null);
      const adRequests = ref([]);
      const loading = ref(true);
      const campaignChartRef = ref(null);
      const statusChartRef = ref(null);
  
      // Computed properties for stats
      const totalRequests = computed(() => adRequests.value.length);
      
      const totalRejected = computed(() => 
        adRequests.value.filter(ad => 
          ad.status === 'rejected' || ad.status === 'modification_rejected'
        ).length
      );
      
      const totalAccepted = computed(() => 
        adRequests.value.filter(ad => 
          ad.status === 'accepted' || ad.status === 'modification_accepted'
        ).length
      );
      
      const totalCompleted = computed(() => 
        adRequests.value.filter(ad => ad.status === 'completed').length
      );
      
      const totalOpen = computed(() => 
        adRequests.value.filter(ad => ad.status === 'open').length
      );
      
      const totalWithdrawn = computed(() => 
        adRequests.value.filter(ad => ad.status === 'withdrawn').length
      );
  
      const fetchData = async () => {
        loading.value = true;
        try {
          const token = sessionStorage.getItem("influencer_Token");
          let decoded = VueJwtDecode.decode(token)
          const uid = decoded['user_id']
          const headers = {
            "Content-Type": "application/json",
            Authorization: token
          };
          // Fetch influencer details
          const influencerResponse = await axios.get(
            `http://127.0.0.1:5000/influencer/get_influencer/${uid}`,
            { headers }
          );
          influencerData.value = influencerResponse.data.influencer;
  
          // Fetch ad requests
          const adsResponse = await axios.get(
            `http://127.0.0.1:5000/ads/get_ads/${uid}?action=influencer_id`,
            { headers }
          );
          adRequests.value = adsResponse.data.ads;
  
          
        } catch (error) {
          console.error("Error fetching data:", error);
        } finally {
          loading.value = false;
        }
      };
  
      const createCharts = () => {
        createCampaignChart();
        createStatusChart();
      };
  
      const createCampaignChart = () => {
        if (!campaignChartRef.value) return;
  
        const campaignCounts = {};
        adRequests.value.forEach(request => {
          campaignCounts[request.campaign_id] = (campaignCounts[request.campaign_id] || 0) + 1;
        });
  
        const ctx = campaignChartRef.value.getContext('2d');
        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: Object.keys(campaignCounts).map(id => `Campaign ${id}`),
            datasets: [{
              label: 'Number of Requests',
              data: Object.values(campaignCounts),
              backgroundColor: 'rgba(100, 255, 218, 0.6)',
              borderColor: 'rgba(100, 255, 218, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                ticks: { color: 'white' },
                grid: { color: 'rgba(255, 255, 255, 0.1)' }
              },
              x: {
                ticks: { color: 'white' },
                grid: { color: 'rgba(255, 255, 255, 0.1)' }
              }
            },
            plugins: {
              legend: {
                labels: { color: 'white' }
              }
            }
          }
        });
      };
  
      const createStatusChart = () => {
        if (!statusChartRef.value) return;
  
        const statusCounts = {};
        adRequests.value.forEach(request => {
          statusCounts[request.status] = (statusCounts[request.status] || 0) + 1;
        });
  
        const ctx = statusChartRef.value.getContext('2d');
        new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: Object.keys(statusCounts),
            datasets: [{
              data: Object.values(statusCounts),
              backgroundColor: [
                'rgba(100, 255, 218, 0.6)',
                'rgba(255, 99, 132, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)'
              ]
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'right',
                labels: { color: 'white' }
              }
            }
          }
        });
      };
  
      const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      };
  
      onMounted(() => {
        fetchData().then(() => 
        createCharts()
    );
      });
  
      return {
        influencerData,
        loading,
        campaignChartRef,
        statusChartRef,
        totalRequests,
        totalRejected,
        totalAccepted,
        totalCompleted,
        totalOpen,
        totalWithdrawn,
        formatDate
      };
    }
  };
  </script>
  
  <style scoped>
  /* Reusing styles from the reference component */
  .dashboard-container {
    font-family: Arial, sans-serif;
    background-color: #1e2a3a;
    color: white;
    padding: 20px;
    min-height: 100vh;
  }
  
  h2 {
    color: white;
    margin-bottom: 30px;
    font-size: 2rem;
    font-weight: 600;
    text-align: center;
  }
  
  h3 {
    color: white;
    margin-bottom: 20px;
    font-size: 1.2rem;
    font-weight: 500;
  }
  
  .loading {
    text-align: center;
    padding: 20px;
    background-color: #2c3e50;
    border-radius: 8px;
    margin: 20px;
    font-size: 1.2rem;
    color: #64ffda;
    animation: pulse 1.5s infinite ease-in-out;
  }
  
  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }
  
  .stat-card {
    background-color: #2c3e50;
    border-radius: 8px;
    padding: 20px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
  }
  
  .stat-card h3 {
    font-size: 1rem;
    margin-bottom: 10px;
    color: #64ffda;
  }
  
  .stat-card p {
    font-size: 1.8rem;
    font-weight: bold;
    margin: 0;
    color: white;
  }
  
  .charts-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }
  
  .chart {
    background-color: #2c3e50;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    min-height: 300px;
  }
  
  .chart h3 {
    color: #64ffda;
    text-align: center;
    margin-bottom: 15px;
  }
  
  .table-container {
    background-color: #2c3e50;
    border-radius: 8px;
    padding: 20px;
    margin: 30px 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .requests-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    font-size: 0.9rem;
  }
  
  .requests-table th,
  .requests-table td {
    border: 1px solid #4a6278;
    padding: 12px 15px;
    text-align: left;
  }
  
  .requests-table th {
    background-color: #34495e;
    color: #64ffda;
    font-weight: 600;
    width: 25%;
  }
  
  .requests-table td {
    color: white;
  }
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
  
  @media (max-width: 768px) {
    .stats-cards {
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
  
    .charts-container {
      grid-template-columns: 1fr;
    }
  
    .requests-table th,
    .requests-table td {
      padding: 8px 10px;
      font-size: 0.8rem;
    }
  }
  </style>