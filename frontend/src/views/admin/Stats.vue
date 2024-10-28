<template>
    <div class="dashboard-container">
      <h2>Influencer Marketing Dashboard</h2>
      
      <div v-if="loading" class="loading">Loading data...</div>
      <div v-else>
        <!-- Stats Cards -->
        <div class="stats-cards">
          <div class="stat-card">
            <h3>Total Influencers</h3>
            <p>{{ influencers.length }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Sponsors</h3>
            <p>{{ sponsors.length }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Campaigns</h3>
            <p>{{ campaigns.length }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Ad Requests</h3>
            <p>{{ ads.length }}</p>
          </div>
          <div class="stat-card">
            <h3>Flagged Users</h3>
            <p>{{ flaggedUsers }}</p>
          </div>
          <div class="stat-card">
            <h3>Flagged Campaigns</h3>
            <p>{{ flaggedCampaigns }}</p>
          </div>
        </div>
  
        <!-- Charts -->
        <div class="charts-container">
          <div class="chart">
            <h3>User Approval Status</h3>
            <canvas ref="approvalChartRef"></canvas>
          </div>
          <div class="chart">
            <h3>User Registration Timeline</h3>
            <canvas ref="userCreationChartRef"></canvas>
          </div>
        </div>
  
        <div class="charts-container">
          <div class="chart">
            <h3>Campaigns per Sponsor</h3>
            <canvas ref="campaignsPerSponsorRef"></canvas>
          </div>
          <div class="chart">
            <h3>Ad Request Status Distribution</h3>
            <canvas ref="adStatusChartRef"></canvas>
          </div>
        </div>
  
        <!-- Ad Requests Table -->
        <div class="table-container">
          <h3>All Ad Requests</h3>
          <table class="requests-table">
            <thead>
              <tr>
                <th @click="sortTable('adRequest_id')">Request ID <span :class="getSortClass('adRequest_id')"></span></th>
                <th @click="sortTable('campaign_id')">Campaign ID <span :class="getSortClass('campaign_id')"></span></th>
                <th @click="sortTable('sponsor_id')">Sponsor ID <span :class="getSortClass('sponsor_id')"></span></th>
                <th @click="sortTable('influencer_id')">Influencer ID <span :class="getSortClass('influencer_id')"></span></th>
                <th @click="sortTable('payout')">Payout <span :class="getSortClass('payout')"></span></th>
                <th @click="sortTable('status')">Status <span :class="getSortClass('status')"></span></th>
                <th @click="sortTable('new_payout')">New Payout <span :class="getSortClass('new_payout')"></span></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ad in sortedAds" :key="ad.adRequest_id">
                <td>{{ ad.adRequest_id }}</td>
                <td>{{ ad.campaign_id }}</td>
                <td>{{ ad.sponsor_id }}</td>
                <td>{{ ad.influencer_id }}</td>
                <td>${{ ad.payout }}</td>
                <td>{{ ad.status }}</td>
                <td>${{ ad.new_payout || 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { Colors } from 'chart.js';
  import Chart from 'chart.js/auto';
  import { ref, onMounted, computed } from 'vue';
  
  export default {
    setup() {
      const influencers = ref([]);
      const sponsors = ref([]);
      const campaigns = ref([]);
      const ads = ref([]);
      const loading = ref(true);
      const sortKey = ref('');
      const sortAsc = ref(true);
      const approvalChartRef = ref(null);
      const userCreationChartRef = ref(null);
      const campaignsPerSponsorRef = ref(null);
      const adStatusChartRef = ref(null);
  
      const fetchAllData = async () => {
        loading.value = true;
        try {
          await Promise.all([
            fetchInfluencers(),
            fetchSponsors(),
            fetchCampaigns(),
            fetchAds(),
          ]);
          
        } catch (error) {
          console.error("Error fetching data:", error);
          alert("Failed to fetch data. Please try again.");
        } finally {
          loading.value = false;
        }
      };
  
      const fetchInfluencers = async () => {
        const token = sessionStorage.getItem("admin_Token");
        const response = await axios.get(
          "http://127.0.0.1:5000/influencer/get_all_influencers",
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `${token}`,
            },
          }
        );
        influencers.value = response.data.influencers;
      };
  
      const fetchSponsors = async () => {
        const token = sessionStorage.getItem("admin_Token");
        const response = await axios.get(
          "http://127.0.0.1:5000/sponsor/get_all_sponsors",
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `${token}`,
            },
          }
        );
        sponsors.value = response.data.sponsors;
      };
  
      const fetchCampaigns = async () => {
        const token = sessionStorage.getItem("admin_Token");
        const response = await axios.get(
          "http://127.0.0.1:5000/campaigns/get_all_campaigns",
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `${token}`,
            },
          }
        );
        campaigns.value = response.data.campaigns;
      };
  
      const fetchAds = async () => {
        const token = sessionStorage.getItem("admin_Token");
        const response = await axios.get(
          "http://127.0.0.1:5000/ads/get_all_ads",
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `${token}`,
            },
          }
        );
        ads.value = response.data.ads;
      };
  
      const createCharts = () => {
        createApprovalChart();
        createUserCreationChart();
        createCampaignsPerSponsorChart();
        createAdStatusChart();
      };
  
      const createApprovalChart = () => {
        if (!approvalChartRef.value) return;
  
        const ctx = approvalChartRef.value.getContext('2d');
        const allUsers = [...influencers.value, ...sponsors.value];
        const approvedUsers = allUsers.filter(user => user.approval).length;
        const unapprovedUsers = allUsers.length - approvedUsers;
        
        new Chart(ctx, {
          type: 'pie',
          data: {
            labels: ['Approved Users', 'Unapproved Users'],
            datasets: [{
              data: [approvedUsers, unapprovedUsers],
              backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(255, 99, 132, 0.6)'],
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                labels: {
                  color: 'white'
                }
              }
            }
          }
        });
      };
  
      const createUserCreationChart = () => {
        if (!userCreationChartRef.value) return;
  
        const ctx = userCreationChartRef.value.getContext('2d');
        const influencerData = processUserCreationData(influencers.value);
        const sponsorData = processUserCreationData(sponsors.value);
        
        new Chart(ctx, {
          type: 'line',
          data: {
            labels: generateDateLabels(),
            datasets: [
              {
                label: 'Influencers',
                data: influencerData,
                borderColor: 'rgba(75, 192, 192, 1)',
                fill: false
              },
              {
                label: 'Sponsors',
                data: sponsorData,
                borderColor: 'rgba(255, 99, 132, 1)',
                fill: false
              }
            ]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Number of Users',
                  color: 'white'
                },
                ticks: {
                  color: 'white'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Date',
                  color: 'white'
                },
                ticks: {
                  color: 'white'
                }
              }
            },
            plugins: {
              legend: {
                labels: {
                  color: 'white'
                }
              }
            }
          }
        });
      };
  
      const createCampaignsPerSponsorChart = () => {
        if (!campaignsPerSponsorRef.value) return;
  
        const ctx = campaignsPerSponsorRef.value.getContext('2d');
        const campaignsPerSponsor = {};
        
        campaigns.value.forEach(campaign => {
          const sponsor = sponsors.value.find(s => s.user_id === campaign.sponsor_id);
          const sponsorName = sponsor ? sponsor.company_name : 'Unknown Sponsor';
          campaignsPerSponsor[sponsorName] = (campaignsPerSponsor[sponsorName] || 0) + 1;
        });
  
        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: Object.keys(campaignsPerSponsor),
            datasets: [{
              label: 'Number of Campaigns',
              data: Object.values(campaignsPerSponsor),
              backgroundColor: 'rgba(75, 192, 192, 0.6)',
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Number of Campaigns',
                  color: 'white'
                },
                ticks: {
                  color: 'white'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Sponsor',
                  color: 'white'
                },
                ticks: {
                  color: 'white'
                }
              }
            },
            plugins: {
              legend: {
                labels: {
                  color: 'white'
                }
              }
            }
          }
        });
      };
  
      const createAdStatusChart = () => {
        if (!adStatusChartRef.value) return;
  
        const ctx = adStatusChartRef.value.getContext('2d');
        const statusCount = {};
        
        ads.value.forEach(ad => {
          statusCount[ad.status] = (statusCount[ad.status] || 0) + 1;
        });
  
        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: Object.keys(statusCount),
            datasets: [{
              label: 'Number of Ad Requests',
              data: Object.values(statusCount),
              backgroundColor: 'rgba(255, 159, 64, 0.6)',
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Number of Requests',
                  color: 'white'
                },
                ticks: {
                  color: 'white'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Status',
                  color: 'white'
                },
                ticks: {
                  color: 'white'
                }
              }
            },
            plugins: {
              legend: {
                labels: {
                  color: 'white'
                }
              }
            }
          }
        });
      };
  
      const processUserCreationData = (users) => {
        const dateCounts = {};
        users.forEach(user => {
          const date = new Date(user.date_created).toISOString().split('T')[0];
          dateCounts[date] = (dateCounts[date] || 0) + 1;
        });
        return generateDateLabels().map(date => dateCounts[date] || 0);
      };
  
      const generateDateLabels = () => {
        const allUsers = [...influencers.value, ...sponsors.value];
        const startDate = new Date(Math.min(...allUsers.map(u => new Date(u.date_created))));
        const endDate = new Date();
        const dateLabels = [];
        for (let d = startDate; d <= endDate; d.setDate(d.getDate() + 1)) {
          dateLabels.push(d.toISOString().split('T')[0]);
        }
        return dateLabels;
      };
  
      const flaggedUsers = computed(() => {
        return [...influencers.value, ...sponsors.value].filter(user => user.flag).length;
      });
  
      const flaggedCampaigns = computed(() => {
        return campaigns.value.filter(campaign => campaign.flag).length;
      });
  
      const sortedAds = computed(() => {
        return ads.value.slice().sort((a, b) => {
          const modifier = sortAsc.value ? 1 : -1;
          if (a[sortKey.value] < b[sortKey.value]) return -1 * modifier;
          if (a[sortKey.value] > b[sortKey.value]) return 1 * modifier;
          return 0;
        });
      });
  
      const sortTable = (key) => {
        if (sortKey.value === key) {
          sortAsc.value = !sortAsc.value;
        } else {
          sortKey.value = key;
          sortAsc.value = true;
        }
      };
  
      const getSortClass = (key) => {
        if (sortKey.value === key) {
          return sortAsc.value ? 'asc' : 'desc';
        }
        return '';
      };
    
      onMounted(() => {
        fetchAllData().then(() => 
    {
        createCharts();
    });
      });
  
      return {
        influencers,
        sponsors,
        campaigns,
        ads,
        loading,
        approvalChartRef,
        userCreationChartRef,
        campaignsPerSponsorRef,
        adStatusChartRef,
        flaggedUsers,
        flaggedCampaigns,
        sortedAds,
        sortTable,
        getSortClass,
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
}

/* Stats Cards Styling */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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

/* Charts Styling */
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

/* Table Styling */
.table-container {
  background-color: #2c3e50;
  border-radius: 8px;
  padding: 20px;
  margin-top: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
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
  cursor: pointer;
  transition: background-color 0.2s ease;
  position: sticky;
  top: 0;
}

.requests-table th:hover {
  background-color: #3a536b;
}

.requests-table tr:nth-child(even) {
  background-color: #3a536b;
}

.requests-table tr:hover {
  background-color: #4a6278;
}

/* Sort indicators */
.asc::after {
  content: ' ▲';
  color: #64ffda;
}

.desc::after {
  content: ' ▼';
  color: #64ffda;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .charts-container {
    grid-template-columns: 1fr;
  }

  .table-container {
    overflow-x: auto;
  }

  .requests-table {
    font-size: 0.8rem;
  }

  .requests-table th,
  .requests-table td {
    padding: 8px 10px;
  }
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #2c3e50;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #4a6278;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64ffda;
}

/* Loading animation */
@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.loading {
  animation: pulse 1.5s infinite ease-in-out;
}

/* Empty state styling */
.empty-state {
  text-align: center;
  padding: 40px;
  color: #64ffda;
  font-style: italic;
}

/* Error state styling */
.error-state {
  background-color: rgba(255, 99, 132, 0.1);
  border: 1px solid rgba(255, 99, 132, 0.3);
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  color: #ff6384;
  text-align: center;
}
</style>