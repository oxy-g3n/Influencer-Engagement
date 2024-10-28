<template>
    <div class="influencer-dashboard">
      <h2>Influencer Dashboard</h2>
      <div v-if="loading" class="loading" aria-live="polite">Loading influencers...</div>
      <div v-else>
        <input 
          v-model="searchQuery" 
          class="search-bar" 
          placeholder="Search by name, category, niche, or reach"
        >
        
        <!-- Influencers Table -->
        <div class="table-container">
          <table class="influencers-table">
            <thead>
              <tr>
                <th @click="sortTable('user_id')">ID <span :class="getSortClass('user_id')"></span></th>
                <th @click="sortTable('full_name')">Full Name <span :class="getSortClass('full_name')"></span></th>
                <th @click="sortTable('influencer_name')">Influencer Name <span :class="getSortClass('influencer_name')"></span></th>
                <th @click="sortTable('category')">Category <span :class="getSortClass('category')"></span></th>
                <th @click="sortTable('niche')">Niche <span :class="getSortClass('niche')"></span></th>
                <th @click="sortTable('reach')">Reach <span :class="getSortClass('reach')"></span></th>
                <th @click="sortTable('date_created')">Date Created <span :class="getSortClass('date_created')"></span></th>
                <th @click="sortTable('approval')">Approval <span :class="getSortClass('approval')"></span></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="influencer in sortedInfluencers" :key="influencer.user_id">
                <td>{{ influencer.user_id }}</td>
                <td>{{ influencer.full_name }}</td>
                <td>{{ influencer.influencer_name }}</td>
                <td>{{ influencer.category }}</td>
                <td>{{ influencer.niche }}</td>
                <td>{{ influencer.reach }}</td>
                <td>{{ formatDate(influencer.date_created) }}</td>
                <td>{{ influencer.approval }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted, computed } from 'vue';
  import axios from 'axios';
  
  export default {
    setup() {
      const influencers = ref([]);
      const loading = ref(true);
      const sortKey = ref('');
      const sortAsc = ref(true);
      const searchQuery = ref('');
  
      const fetchInfluencers = async () => {
        loading.value = true;
        try {
          const token = sessionStorage.getItem("sponsor_Token"); // Adjust this based on how you store the token
          const response = await axios.get(
            'http://127.0.0.1:5000/influencer/get_all_influencers',
            {
              headers: {
                "Content-Type": "application/json",
                Authorization: `${token}`,
              },
            }
          );
          influencers.value = response.data.influencers;
        } catch (error) {
          console.error("Error fetching influencers:", error);
        } finally {
          loading.value = false;
        }
      };

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
  
      const filteredInfluencers = computed(() => {
        return influencers.value.filter(influencer => 
          influencer.full_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          influencer.category.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          influencer.niche.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          influencer.reach.toString().includes(searchQuery.value)
        );
      });
  
      const sortedInfluencers = computed(() => {
        return [...filteredInfluencers.value].sort((a, b) => {
          const modifier = sortAsc.value ? 1 : -1;
          if (a[sortKey.value] < b[sortKey.value]) return -1 * modifier;
          if (a[sortKey.value] > b[sortKey.value]) return 1 * modifier;
          return 0;
        });
      });
  
      const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
        });
      };
  
      onMounted(async () => {
        await fetchInfluencers();
      });
  
      return {
        loading,
        sortedInfluencers,
        searchQuery,
        sortTable,
        getSortClass,
        formatDate,
      };
    }
  };
  </script>
  
  <style scoped>
  .influencer-dashboard {
    font-family: Arial, sans-serif;
    background-color: #1e2a3a;
    color: white;
    padding: 20px;
    min-height: 100vh;
  }
  
  h2 {
    color: white;
    margin-bottom: 20px;
  }
  
  .loading {
    text-align: center;
    padding: 20px;
    background-color: #2c3e50;
    border-radius: 5px;
  }
  
  .search-bar {
    width: 100%;
    padding: 10px;
    margin-bottom: 20px;
    border: none;
    border-radius: 5px;
    background-color: #2c3e50;
    color: white;
  }
  
  .table-container {
    background-color: #2c3e50;
    border-radius: 5px;
    overflow-x: auto;
  }
  
  .influencers-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .influencers-table th,
  .influencers-table td {
    border: 1px solid #4a6278;
    padding: 12px;
    text-align: left;
  }
  
  .influencers-table th {
    background-color: #34495e;
    color: white;
    cursor: pointer;
  }
  
  .influencers-table tr:nth-child(even) {
    background-color: #3a536b;
  }
  
  .influencers-table tr:hover {
    background-color: #4a6278;
  }
  
  .asc::after {
    content: ' ▲';
  }
  
  .desc::after {
    content: ' ▼';
  }
  </style>