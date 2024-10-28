<template>
    <div class="campaigns-container">
      <div class="header">
        <div class="logo-section">
          <h1>Campaigns</h1>
          <p>All Available Campaigns</p>
        </div>
        <div class="search-create-container">
          <label for="search-input" class="sr-only">Search campaigns</label>
          <input
            id="search-input"
            type="text"
            class="form-control search-input"
            placeholder="Search campaigns"
            v-model="searchQuery"
            aria-label="Search campaigns"
          />
        </div>
      </div>
  
      <div class="content-container">
        <div class="campaigns-grid-container">
          <div v-if="filteredCampaigns.length" class="campaigns-grid">
            <div
              v-for="campaign in filteredCampaigns"
              :key="campaign.campaign_id"
              class="campaign-card"
              @click="selectCampaign(campaign)"
              tabindex="0"
              role="button"
              :aria-expanded="selectedCampaign && selectedCampaign.campaign_id === campaign.campaign_id"
            >
              <div class="campaign-content">
                <h2>{{ campaign.campaign_name }}</h2>
                <p>Budget: ${{ campaign.budget }}</p>
                <p>Visibility: {{ campaign.visibility ? 'Public' : 'Private' }}</p>
                <p>Niche: {{ campaign.niche }}</p>
                <div v-if="campaign.flag" class="flag-indicator">
                  <span class="flag-icon">🚩</span> Flagged
                </div>
              </div>
              <button
                @click.stop="toggleFlag(campaign)"
                class="btn btn-primary flag-btn"
                :class="{ 'btn-danger': campaign.flag }"
              >
                {{ campaign.flag ? 'Remove Flag' : 'Flag Campaign' }}
              </button>
            </div>
          </div>
          <div v-else-if="loading" class="loading" aria-live="polite">Loading campaigns...</div>
          <div v-else class="no-campaigns" aria-live="polite">No campaigns available.</div>
        </div>
      </div>
  
      <!-- Campaign Details Modal -->
      <div v-if="selectedCampaign" class="modal" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h2>{{ selectedCampaign.campaign_name }}</h2>
          <p><strong>Description:</strong> {{ selectedCampaign.campaign_description }}</p>
          <p><strong>Goals:</strong> {{ selectedCampaign.campaign_goals }}</p>
          <p><strong>Start Date:</strong> {{ selectedCampaign.campaign_start_date }}</p>
          <p><strong>End Date:</strong> {{ selectedCampaign.campaign_end_date }}</p>
          <p><strong>Budget:</strong> ${{ selectedCampaign.budget }}</p>
          <p><strong>Visibility:</strong> {{ selectedCampaign.visibility ? 'Public' : 'Private' }}</p>
          <p><strong>Niche:</strong> {{ selectedCampaign.niche }}</p>
          <p><strong>Company:</strong> {{ selectedCampaign.company_name }}</p>
          <p><strong>Industry:</strong> {{ selectedCampaign.industry }}</p>
          <p v-if="selectedCampaign.flag"><strong>Flagged:</strong> Yes</p>
          <button @click="closeModal" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        campaigns: [],
        selectedCampaign: null,
        loading: true,
        searchQuery: '',
      };
    },
    computed: {
      filteredCampaigns() {
        const searchLower = this.searchQuery.toLowerCase();
        return this.campaigns.filter((campaign) =>
          campaign.campaign_name.toLowerCase().includes(searchLower) ||
          campaign.niche.toLowerCase().includes(searchLower)
        );
      },
    },
    methods: {
      async fetchCampaigns() {
        this.loading = true;
        try {
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
          if (Array.isArray(response.data.campaigns)) {
            this.campaigns = response.data.campaigns;
          } else {
            console.error("Unexpected data format:", response.data);
            this.campaigns = [];
          }
        } catch (error) {
          console.error("Error fetching campaigns:", error);
          this.campaigns = [];
        } finally {
          this.loading = false;
        }
      },
      async toggleFlag(campaign) {
        try {
          const token = sessionStorage.getItem("admin_Token");
          const response = await axios.put(
            `http://127.0.0.1:5000/campaigns/change_campaign_flag/${campaign.campaign_id}`,
            {},
            {
              headers: {
                "Content-Type": "application/json",
                Authorization: `${token}`,
              },
            }
          );
          if (response.status === 200) {
            await this.fetchCampaigns(); // Refresh the campaigns list
          }
        } catch (error) {
          console.error("Error toggling flag:", error);
          alert("Failed to update flag status");
        }
      },
      selectCampaign(campaign) {
        this.selectedCampaign = campaign;
      },
      closeModal() {
        this.selectedCampaign = null;
      },
    },
    created() {
      this.fetchCampaigns();
    },
  };
  </script>
  
  <style scoped>
  .campaigns-container {
    font-family: Arial, sans-serif;
    background-color: #1e2a3a;
    color: white;
    padding: 20px;
    min-height: 100vh;
  }
  
  .header {
    background-color: #2c3e50;
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 5px 5px 0 0;
  }
  
  .logo-section h1 {
    margin: 0;
    font-size: 24px;
  }
  
  .logo-section p {
    margin: 5px 0 0;
    font-size: 14px;
  }
  
  .content-container {
    background-color: #34495e;
    color: white;
    padding: 20px;
    border-radius: 0 0 5px 5px;
  }
  
  .campaigns-grid-container {
    overflow-x: auto;
    max-width: 100%;
  }
  
  .campaigns-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    padding: 10px;
  }
  
  .campaign-card {
    background-color: #2c3e50;
    border: 1px solid #4a6278;
    border-radius: 5px;
    overflow: hidden;
    transition: box-shadow 0.3s;
    cursor: pointer;
  }
  
  .campaign-card:hover,
  .campaign-card:focus {
    box-shadow: 0 8px 8px rgba(0, 0, 0, 0.4);
    outline: none;
  }
  
  .campaign-content {
    padding: 15px;
  }
  
  .campaign-content h2 {
    margin-top: 0;
    font-size: 18px;
  }
  
  .campaign-content p {
    margin: 5px 0;
    font-size: 14px;
  }
  
  .flag-indicator {
    color: #e74c3c;
    font-weight: bold;
    margin-top: 10px;
  }
  
  .flag-icon {
    margin-right: 5px;
  }
  
  .flag-btn {
    width: 100%;
    padding: 10px;
    border: none;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .btn-primary {
    background-color: #3498db;
    color: white;
  }
  
  .btn-primary:hover {
    background-color: #2980b9;
  }
  
  .btn-danger {
    background-color: #e74c3c;
  }
  
  .btn-danger:hover {
    background-color: #c0392b;
  }
  
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .modal-content {
    background-color: #34495e;
    padding: 20px;
    border-radius: 5px;
    max-width: 500px;
    width: 100%;
  }
  
  .btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
    margin-top: 10px;
  }
  
  .btn-secondary {
    background-color: #95a5a6;
    color: white;
  }
  
  .search-input {
    width: 100%;
    padding: 10px;
    border: none;
    border-radius: 4px;
    background-color: #34495e;
    color: white;
  }
  
  .search-input::placeholder {
    color: #95a5a6;
  }
  
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  }
  
  @media (max-width: 768px) {
    .header {
      flex-direction: column;
      align-items: flex-start;
    }
  
    .search-create-container {
      width: 100%;
      margin-top: 10px;
    }
  }
  </style>