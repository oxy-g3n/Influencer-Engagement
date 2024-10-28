<template>
    <div class="user-dashboard">
      <h2>User Management Dashboard</h2>
      <div v-if="loading" class="loading" aria-live="polite">Loading users...</div>
      <div v-else>
        <input 
          v-model="searchQuery" 
          class="search-bar" 
          placeholder="Search by ID, name, username, or email"
        >
        
        <div class="table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th @click="sortTable('user_id')">User ID <span :class="getSortClass('user_id')"></span></th>
                <th @click="sortTable('username')">Username <span :class="getSortClass('username')"></span></th>
                <th @click="sortTable('full_name')">Full Name <span :class="getSortClass('full_name')"></span></th>
                <th @click="sortTable('mail')">Email <span :class="getSortClass('mail')"></span></th>
                <th @click="sortTable('role')">Role <span :class="getSortClass('role')"></span></th>
                <th @click="sortTable('date_created')">Date Created <span :class="getSortClass('date_created')"></span></th>
                <th>Approval Status</th>
                <th>Flag Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in sortedUsers" :key="user.user_id">
                <td>{{ user.user_id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.full_name }}</td>
                <td>{{ user.mail }}</td>
                <td>{{ user.role }}</td>
                <td>{{ formatDate(user.date_created) }}</td>
                <td>
                  <div class="status-column">
                    <span :class="['status-badge', user.approval ? 'approved' : 'not-approved']">
                      {{ user.approval ? 'Approved' : 'Not Approved' }}
                    </span>
                    <button 
                      :class="['action-button', user.approval ? 'remove' : 'approve']"
                      @click="handleApproval(user)"
                    >
                      {{ user.approval ? 'Remove Approval' : 'Approve' }}
                    </button>
                  </div>
                </td>
                <td>
                  <div class="status-column">
                    <span :class="['status-badge', user.flag ? 'flagged' : 'not-flagged']">
                      {{ user.flag ? 'Flagged' : 'Not Flagged' }}
                    </span>
                    <button 
                      :class="['action-button', user.flag ? 'unflag' : 'flag']"
                      @click="handleFlag(user)"
                    >
                      {{ user.flag ? 'Remove Flag' : 'Flag User' }}
                    </button>
                  </div>
                </td>
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
      const users = ref([]);
      const loading = ref(true);
      const sortKey = ref('');
      const sortAsc = ref(true);
      const searchQuery = ref('');
  
      const fetchUsers = async () => {
        loading.value = true;
        try {
          const token = sessionStorage.getItem("admin_Token");
          const response = await axios.get(
            'http://127.0.0.1:5000/users/get_all_users',
            {
              headers: {
                "Content-Type": "application/json",
                Authorization: `${token}`,
              },
            }
          );
          users.value = response.data.users;
        } catch (error) {
          console.error("Error fetching users:", error);
        } finally {
          loading.value = false;
        }
      };
  
      const handleApproval = async (user) => {
        try {
          const token = sessionStorage.getItem("admin_Token");
          await axios.put(
            `http://127.0.0.1:5000/users/change_approval/${user.user_id}`,
            {},
            {
              headers: {
                "Content-Type": "application/json",
                Authorization: `${token}`,
              },
            }
          );
          await fetchUsers(); // Refresh the user list
        } catch (error) {
          console.error("Error updating approval status:", error);
        }
      };
  
      const handleFlag = async (user) => {
        try {
          const token = sessionStorage.getItem("admin_Token");
          await axios.put(
            `http://127.0.0.1:5000/users/change_flag/${user.user_id}`,
            {},
            {
              headers: {
                "Content-Type": "application/json",
                Authorization: `${token}`,
              },
            }
          );
          await fetchUsers(); // Refresh the user list
        } catch (error) {
          console.error("Error updating flag status:", error);
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
  
      const filteredUsers = computed(() => {
        const query = searchQuery.value.toLowerCase();
        return users.value.filter(user => 
          user.user_id.toString().includes(query) ||
          user.username.toLowerCase().includes(query) ||
          user.full_name.toLowerCase().includes(query) ||
          user.mail.toLowerCase().includes(query) ||
          user.role.toLowerCase().includes(query)
        );
      });
  
      const sortedUsers = computed(() => {
        return [...filteredUsers.value].sort((a, b) => {
          if (!sortKey.value) return 0;
          
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
        await fetchUsers();
      });
  
      return {
        loading,
        sortedUsers,
        searchQuery,
        sortTable,
        getSortClass,
        formatDate,
        handleApproval,
        handleFlag,
      };
    }
  };
  </script>
  
  <style scoped>
  .user-dashboard {
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
  
  .users-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .users-table th,
  .users-table td {
    border: 1px solid #4a6278;
    padding: 12px;
    text-align: left;
  }
  
  .users-table th {
    background-color: #34495e;
    color: white;
    cursor: pointer;
  }
  
  .users-table tr:nth-child(even) {
    background-color: #3a536b;
  }
  
  .users-table tr:hover {
    background-color: #4a6278;
  }
  
  .asc::after {
    content: ' ▲';
  }
  
  .desc::after {
    content: ' ▼';
  }
  
  .status-column {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .status-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.875rem;
    font-weight: 500;
    text-align: center;
  }
  
  .approved {
    background-color: #10b981;
    color: white;
  }
  
  .not-approved {
    background-color: #6b7280;
    color: white;
  }
  
  .flagged {
    background-color: #ef4444;
    color: white;
  }
  
  .not-flagged {
    background-color: #6b7280;
    color: white;
  }
  
  .action-button {
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .approve {
    background-color: #059669;
    color: white;
  }
  
  .approve:hover {
    background-color: #047857;
  }
  
  .remove {
    background-color: #dc2626;
    color: white;
  }
  
  .remove:hover {
    background-color: #b91c1c;
  }
  
  .flag {
    background-color: #dc2626;
    color: white;
  }
  
  .flag:hover {
    background-color: #b91c1c;
  }
  
  .unflag {
    background-color: #6b7280;
    color: white;
  }
  
  .unflag:hover {
    background-color: #4b5563;
  }
  </style>