<template>
    <div class="dashboard-container">
      <h2>Sponsor Statistics Dashboard</h2>
      
      <div v-if="loading" class="loading">Loading data...</div>
      <div v-else>
        <!-- Campaign Stats Cards -->
        <div class="stats-cards">
          <div class="stat-card">
            <h3>Total Campaigns</h3>
            <p>{{ totalCampaigns }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Budget</h3>
            <p>${{ formatNumber(totalBudget) }}</p>
          </div>
          <div class="stat-card">
            <h3>Public Campaigns</h3>
            <p>{{ publicCampaigns }}</p>
          </div>
          <div class="stat-card">
            <h3>Private Campaigns</h3>
            <p>{{ privateCampaigns }}</p>
          </div>
        </div>
  
        <!-- Request Stats Cards -->
        <div class="stats-cards">
          <div class="stat-card">
            <h3>Total Requests</h3>
            <p>{{ totalRequests }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Accepted</h3>
            <p>{{ totalAccepted }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Rejected</h3>
            <p>{{ totalRejected }}</p>
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
  
        <!-- Sponsor Details -->
        <div class="table-container">
          <h3>Sponsor Details</h3>
          <table class="requests-table" v-if="sponsorData">
            <tbody>
              <tr>
                <th>Company Name</th>
                <td>{{ sponsorData.company_name }}</td>
                <th>Industry</th>
                <td>{{ sponsorData.industry }}</td>
              </tr>
              <tr>
                <th>Full Name</th>
                <td>{{ sponsorData.full_name }}</td>
                <th>Username</th>
                <td>{{ sponsorData.username }}</td>
              </tr>
              <tr>
                <th>Email</th>
                <td>{{ sponsorData.mail }}</td>
                <th>Join Date</th>
                <td>{{ formatDate(sponsorData.date_created) }}</td>
              </tr>
              <tr>
                <th>Status</th>
                <td>{{ sponsorData.approval ? 'Approved' : 'Pending' }}</td>
                <th>Account Flag</th>
                <td>{{ sponsorData.flag ? 'Flagged' : 'Normal' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
  
        <!-- Charts -->
        <div class="charts-container">
          <div class="chart">
            <h3>Campaign Request Distribution</h3>
            <canvas ref="requestChartRef"></canvas>
          </div>
          <div class="chart">
            <h3>Campaign Budget Distribution</h3>
            <canvas ref="budgetChartRef"></canvas>
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
    name: 'SponsorStats',
    setup() {
      const sponsorData = ref(null);
      const campaigns = ref([]);
      const adRequests = ref([]);
      const loading = ref(true);
      const requestChartRef = ref(null);
      const budgetChartRef = ref(null);
  
      // Computed properties for campaign stats
      const totalCampaigns = computed(() => campaigns.value.length);
      
      const totalBudget = computed(() => 
        campaigns.value.reduce((sum, campaign) => sum + campaign.budget, 0)
      );
      
      const publicCampaigns = computed(() => 
        campaigns.value.filter(campaign => campaign.visibility == '1').length
      );
      
      const privateCampaigns = computed(() => 
        campaigns.value.filter(campaign => campaign.visibility == '0').length
      );
  
      // Computed properties for request stats
      const totalRequests = computed(() => adRequests.value.length);
      
      const totalAccepted = computed(() => 
        adRequests.value.filter(ad => 
          ad.status === 'accepted' || ad.status === 'modification_accepted'
        ).length
      );
      
      const totalRejected = computed(() => 
        adRequests.value.filter(ad => 
          ad.status === 'rejected' || ad.status === 'modification_rejected'
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
          const token = sessionStorage.getItem("sponsor_Token");
          let decoded = VueJwtDecode.decode(token);
          const uid = decoded['user_id'];
          const headers = {
            "Content-Type": "application/json",
            Authorization: token
          };
  
          // Fetch sponsor details
          const sponsorResponse = await axios.get(
            `http://127.0.0.1:5000/sponsor/get_sponsor/${uid}`,
            { headers }
          );
          sponsorData.value = sponsorResponse.data.sponsor;
  
          // Fetch campaigns
          const campaignsResponse = await axios.get(
            `http://127.0.0.1:5000/campaigns/get_campaigns/${uid}?action=sponsor_id`,
            { headers }
          );
          campaigns.value = campaignsResponse.data.campaigns;
  
          // Fetch ad requests
          const adsResponse = await axios.get(
            `http://127.0.0.1:5000/ads/get_ads/${uid}?action=sponsor_id`,
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
        createRequestsChart();
        createBudgetChart();
      };
  
      const createRequestsChart = () => {
        if (!requestChartRef.value) return;
  
        const requestCounts = {};
        adRequests.value.forEach(request => {
          requestCounts[request.campaign_id] = (requestCounts[request.campaign_id] || 0) + 1;
        });
  
        const ctx = requestChartRef.value.getContext('2d');
        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: Object.keys(requestCounts).map(id => {
              const campaign = campaigns.value.find(c => c.campaign_id === parseInt(id));
              return campaign ? campaign.campaign_name : `Campaign ${id}`;
            }),
            datasets: [{
              label: 'Number of Requests',
              data: Object.values(requestCounts),
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
  
      const createBudgetChart = () => {
        if (!budgetChartRef.value) return;
  
        const ctx = budgetChartRef.value.getContext('2d');
        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: campaigns.value.map(campaign => campaign.campaign_name),
            datasets: [{
              label: 'Campaign Budget',
              data: campaigns.value.map(campaign => campaign.budget),
              backgroundColor: 'rgba(255, 159, 64, 0.6)',
              borderColor: 'rgba(255, 159, 64, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  color: 'white',
                  callback: value => `$${formatNumber(value)}`
                },
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
              },
              tooltip: {
                callbacks: {
                  label: context => `Budget: $${formatNumber(context.raw)}`
                }
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
  
      const formatNumber = (number) => {
        return number.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        });
      };
  
      onMounted(() => {
        fetchData().then(() => createCharts());
      });
  
      return {
        sponsorData,
        loading,
        totalCampaigns,
        totalBudget,
        publicCampaigns,
        privateCampaigns,
        totalRequests,
        totalAccepted,
        totalRejected,
        totalCompleted,
        totalOpen,
        totalWithdrawn,
        requestChartRef,
        budgetChartRef,
        formatDate,
        formatNumber
      };
    }
  };
  </script>

<style scoped>
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