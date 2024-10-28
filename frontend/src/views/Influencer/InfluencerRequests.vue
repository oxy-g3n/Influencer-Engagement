<template>
    <div class="services-container">
      <div class="header">
        <div class="logo-section">
          <h1>Ad Requests</h1>
          <p>Manage your ad requests</p>
        </div>
        <div class="search-create-container">
          <label for="search-input" class="sr-only">Search ad requests</label>
          <input
            id="search-input"
            type="text"
            class="search-input"
            placeholder="Search ad requests"
            v-model="searchQuery"
            aria-label="Search ad requests"
          />
        </div>
      </div>
      <div class="content-container">
        <div v-for="(requests, status) in groupedRequests" :key="status" class="table-container">
          <h2>{{ status }} Requests</h2>
          <table :class="['servicemen-table', status.toLowerCase()]">
            <thead>
              <tr>
                <th @click="sortTable(status, 'adRequest_id')">
                  Request ID <span :class="getSortClass(status, 'adRequest_id')"></span>
                </th>
                <th @click="sortTable(status, 'campaign_id')">
                  Campaign ID <span :class="getSortClass(status, 'campaign_id')"></span>
                </th>
                <th @click="sortTable(status, 'sponsor_id')">
                  Sponsor ID <span :class="getSortClass(status, 'sponsor_id')"></span>
                </th>
                <th @click="sortTable(status, 'influencer_id')">
                  Influencer ID <span :class="getSortClass(status, 'influencer_id')"></span>
                </th>
                <th @click="sortTable(status, 'requirements')">
                  Requirements <span :class="getSortClass(status, 'requirements')"></span>
                </th>
                <th @click="sortTable(status, 'payout')">
                  Payout <span :class="getSortClass(status, 'payout')"></span>
                </th>
                <th @click="sortTable(status, 'status')">
                  Status <span :class="getSortClass(status, 'status')"></span>
                </th>
                <th v-if="status === 'Modified'" @click="sortTable(status, 'new_payout')">
                  New Payout <span :class="getSortClass(status, 'new_payout')"></span>
                </th>
                <th v-if="status === 'Open'">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="request in sortedRequests(status)" :key="request.adRequest_id">
                <td>{{ request.adRequest_id }}</td>
                <td>{{ request.campaign_id }}</td>
                <td>{{ request.sponsor_id }}</td>
                <td>{{ request.influencer_id }}</td>
                <td>{{ request.requirements }}</td>
                <td>${{ request.payout }}</td>
                <td>{{ request.status }}</td>
                <td v-if="status === 'Modified'">${{ request.new_payout }}</td>
                <td v-if="status === 'Open'">
                  <div  class="button-group">
                    <button @click="acceptRequest(request)" class="btn btn-primary">Accept</button>
                    <button @click="rejectRequest(request)" class="btn btn-secondary">Reject</button>
                    <button @click="openModifyModal(request)" class="btn btn-primary">Modify</button>
                  </div>
                  <div v-if="request.status === 'influencer_generated'" class="button-group">
                    <button @click="withdrawRequest(request)" class="btn btn-secondary">Withdraw</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
  
      <!-- Modify Modal -->
      <div v-if="showModifyModal" class="modal">
        <div class="modal-content">
          <h2>Modify Payout</h2>
          <label for="new-payout">New Payout:</label>
          <input id="new-payout" v-model="newPayout" type="number" min="0" step="0.01" />
          <div class="button-group">
            <button @click="submitModification" class="btn btn-primary">Submit</button>
            <button @click="closeModifyModal" class="btn btn-secondary">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import VueJwtDecode from 'vue-jwt-decode';
  
  export default {
    data() {
      return {
        adRequests: [],
        searchQuery: '',
        sortKey: {},
        sortOrder: {},
        showModifyModal: false,
        selectedRequest: null,
        newPayout: 0,
      };
    },
    computed: {
      groupedRequests() {
        const filtered = this.adRequests.filter(request =>
          Object.values(request).some(value =>
            String(value).toLowerCase().includes(this.searchQuery.toLowerCase())
          )
        );
  
        return {
          Open: filtered.filter(request => request.status === 'open'),
          Accepted: filtered.filter(request => request.status === 'accepted'),
          Modified: filtered.filter(request => request.status === 'modified'),
          Other: filtered.filter(request => !['open', 'accepted', 'modified'].includes(request.status)),
        };
      },
    },
    methods: {
      async fetchAdRequests() {
        try {
          const token = sessionStorage.getItem('influencer_Token');
          let decoded = VueJwtDecode.decode(token)
          const userId = decoded['user_id']

          const response = await axios.get(`http://127.0.0.1:5000/ads/get_ads/${userId}?action=influencer_id`, {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `${token}`,
            },
          });
          this.adRequests = response.data.ads;
        } catch (error) {
          console.error('Error fetching ad requests:', error);
          alert('Failed to fetch ad requests. Please try again.');
        }
      },
      sortedRequests(status) {
        const key = this.sortKey[status];
        const order = this.sortOrder[status];
        return [...this.groupedRequests[status]].sort((a, b) => {
          let comparison = 0;
          if (a[key] < b[key]) comparison = -1;
          if (a[key] > b[key]) comparison = 1;
          return order === 'asc' ? comparison : -comparison;
        });
      },
      sortTable(status, key) {
        if (this.sortKey[status] === key) {
          this.sortOrder[status] = this.sortOrder[status] === 'asc' ? 'desc' : 'asc';
        } else {
          this.sortKey[status] = key;
          this.sortOrder[status] = 'asc';
        }
      },
      getSortClass(status, key) {
        if (this.sortKey[status] === key) {
          return this.sortOrder[status] === 'asc' ? 'asc' : 'desc';
        }
        return '';
      },
      async updateAdStatus(request, newStatus) {
      try {
        const token = sessionStorage.getItem('influencer_Token');
        const response = await axios.put(
          `http://127.0.0.1:5000/ads/edit_ad_status/${request.adRequest_id}`,
          {
            current_status: request.status,
            new_status: newStatus,
            requirements: request.requirements // Only used for influencer generated to accepted
          },
          {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `${token}`
            }
          }
        );

        if (response.status === 200) {
          alert(`Successfully updated status to ${newStatus}`);
          // Update the local state
          const index = this.adRequests.findIndex(r => r.adRequest_id === request.adRequest_id);
          if (index !== -1) {
            this.adRequests[index].status = newStatus;
          }
        } else {
          throw new Error('Failed to update status');
        }
      } catch (error) {
        console.error('Error updating ad status:', error);
        alert(`Failed to update status: ${error.message}`);
      }
    },

    async acceptRequest(request) {
      await this.updateAdStatus(request, 'accepted');
    },

    async rejectRequest(request) {
      await this.updateAdStatus(request, 'rejected');
    },

    async withdrawRequest(request) {
      await this.updateAdStatus(request, 'withdrawn');
    },
      openModifyModal(request) {
        this.selectedRequest = request;
        this.newPayout = request.payout;
        this.showModifyModal = true;
      },
      closeModifyModal() {
        this.showModifyModal = false;
        this.selectedRequest = null;
        this.newPayout = 0;
      },


      async submitModification() {
      if (!this.selectedRequest || !this.newPayout) {
        alert('Please select a request and enter a new payout amount.');
        return;
      }

      try {
        const token = sessionStorage.getItem('influencer_Token');
        const response = await axios.put(
          `http://127.0.0.1:5000/ads/edit_ad_request/${this.selectedRequest.adRequest_id}`,
          {
            new_payout: this.newPayout
          },
          {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `${token}`
            }
          }
        );

        if (response.status === 200) {
          alert('Successfully requested new payout');
          
          // Update the local state
          const index = this.adRequests.findIndex(r => r.adRequest_id === this.selectedRequest.adRequest_id);
          if (index !== -1) {
            this.adRequests[index].new_payout = this.newPayout;
            this.adRequests[index].status = 'modified';
          }

          this.closeModifyModal();
        } else {
          throw new Error('Failed to update payout');
        }
      } catch (error) {
        console.error('Error modifying ad request:', error);
        alert(`Failed to modify request: ${error.message}`);
      }
    },

    openModifyModal(request) {
      this.selectedRequest = request;
      this.newPayout = request.payout; // Initialize with current payout
      this.showModifyModal = true;
    },

    closeModifyModal() {
      this.showModifyModal = false;
      this.selectedRequest = null;
      this.newPayout = 0;
    },

    },
    created() {
      this.fetchAdRequests();
    },
  };
  </script>
  
  <style scoped>
  .services-container {
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
  
  .table-container {
    margin-top: 20px;
    padding: 10px;
    background-color: #2c3e50;
    border-radius: 5px;
  }
  
  .servicemen-table {
    width: 100%;
    background-color: #34495e;
    border-radius: 5px;
    border-collapse: collapse;
    color: white;
  }
  
  .servicemen-table th,
  .servicemen-table td {
    border: 1px solid #4a6278;
    padding: 10px;
    text-align: left;
  }
  
  .servicemen-table th {
    background-color: #2c3e50;
    cursor: pointer;
  }
  
  .servicemen-table td {
    background-color: #34495e;
  }
  
  .asc::after {
    content: ' ▲';
  }
  
  .desc::after {
    content: ' ▼';
  }
  
  .btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
    margin-right: 5px;
  }
  
  .btn-primary {
    background-color: #3498db;
    color: white;
  }
  
  .btn-primary:hover {
    background-color: #2980b9;
  }
  
  .btn-secondary {
    background-color: #2ecc71;
    color: white;
  }
  
  .btn-secondary:hover {
    background-color: #27ae60;
  }
  
  .search-input {
    min-width: 200px;
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
  
  .button-group {
    display: flex;
    gap: 5px;
  }
  
  .modal {
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background-color: rgba(0,0,0,0.4);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .modal-content {
    background-color: #2c3e50;
    padding: 20px;
    border-radius: 5px;
    width: 300px;
  }
  
  .modal-content h2 {
    margin-top: 0;
  }
  
  .modal-content input {
    width: 100%;
    padding: 8px;
    margin: 10px 0;
    border: 1px solid #4a6278;
    border-radius: 4px;
    background-color: #34495e;
    color: white;
  }
  
  .modal-content .button-group {
    display: flex;
    justify-content: flex-end;
    margin-top: 15px;
  }
  </style>