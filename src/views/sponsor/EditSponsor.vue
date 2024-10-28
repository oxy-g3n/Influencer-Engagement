<template>
    <div class="vh-100 d-flex justify-content-center align-items-center page-colour">
      <div v-if="isLoading" class="text-white">Loading...</div>
  
      <div v-else class="container">
        <div class="row">
          <div class="col-md-10 mx-auto">
            <h2 class="text-center text-white mb-4">Update Sponsor Profile</h2>
            <form @submit.prevent="updateProfile" class="form-container border p-4 border-primary rounded">
              <div class="row">
                <div class="col-md-6">
                  <div class="form-group mb-3">
                    <label for="password">New Password (leave blank to keep current):</label>
                    <input type="password" id="password" v-model="password" class="form-control">
                  </div>
                  <div class="form-group mb-3">
                    <label for="email">Email:</label>
                    <input type="email" id="email" v-model="mail" class="form-control">
                  </div>
                  <div class="form-group mb-3">
                    <label for="companyName">Company Name:</label>
                    <input type="text" id="companyName" v-model="companyName" class="form-control">
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-group mb-3">
                    <label for="fullName">Full Name:</label>
                    <input type="text" id="fullName" v-model="fullName" class="form-control">
                  </div>
                  <div class="form-group mb-3">
                    <label for="industry">Industry:</label>
                    <input type="text" id="industry" v-model="industry" class="form-control">
                  </div>
                </div>
              </div>
              <div class="row mt-3">
                  <button type="submit" class="btn btn-primary btn-block">Update Profile</button>
              </div>
            </form>
            <div v-if="alertMessage" class="alert-overlay d-flex justify-content-center align-items-center">
              <div class="alert" :class="alertClass" role="alert">
                {{ alertMessage }}
                <button type="button" class="btn-close" @click="alertMessage = ''" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
import axios from 'axios';
import { useRouter } from 'vue-router';
import VueJwtDecode from 'vue-jwt-decode';

export default {
  data() {
    return {
      password: '',
      mail: '',
      fullName: '',
      companyName: '',
      industry: '',
      alertMessage: '',
      alertClass: '',
      isLoading: true,
    };
  },
  setup() {
    const router = useRouter();
    return { router };
  },
  methods: {
    async fetchSponsorData() {
      try {
        let token = sessionStorage.getItem('sponsor_Token');
        let decoded = VueJwtDecode.decode(token);
        const userId = decoded['user_id'];

        const response = await axios.get(`http://127.0.0.1:5000/sponsor/get_sponsor/${userId}`, {
          headers: {
            'Authorization': token,
          },
        });
        
        // Updated to match the new route response structure
        const sponsorData = response.data.sponsor; // Changed from response.data.sponsors[0]
        
        // Populate form fields with fetched data
        this.mail = sponsorData.mail;
        this.fullName = sponsorData.full_name;
        this.companyName = sponsorData.company_name;
        this.industry = sponsorData.industry;

        console.log('Fetched sponsor data:', sponsorData);
      } catch (error) {
        console.error("Error fetching sponsor data:", error);
        if (error.response && error.response.status === 404) {
          this.showAlert("Sponsor not found", "alert-danger");
        } else {
          this.showAlert("Unable to fetch sponsor data", "alert-danger");
        }
      } finally {
        this.isLoading = false;
      }
    },

    async updateProfile() {
      try {
        let token = sessionStorage.getItem('sponsor_Token');
        let decoded = VueJwtDecode.decode(token);
        const userId = decoded['user_id'];

        const updateData = {
          full_name: this.fullName,
          mail: this.mail,
          company_name: this.companyName,
          industry: this.industry
        };

        if (this.password) {
          updateData.password = this.password;
        }

        const response = await axios.put(
          `http://127.0.0.1:5000/sponsor/update_profile/${userId}`,
          updateData,
          {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': token
            },
          }
        );

        this.showAlert('Profile updated successfully', 'alert-success');
      } catch (error) {
        console.error('Update error:', error);
        if (error.response && error.response.status === 404) {
          this.showAlert('Sponsor profile not found', 'alert-danger');
        } else {
          this.showAlert('An error occurred during profile update', 'alert-danger');
        }
      }
    },

    cancel() {
      this.router.push('/sponsordash');
    },

    showAlert(message, alertClass) {
      this.alertMessage = message;
      this.alertClass = `alert ${alertClass} alert-dismissible fade show`;
      setTimeout(() => {
        this.alertMessage = '';
      }, 5000);
    },
  },
  mounted() {
    this.fetchSponsorData();
  }
};
</script>
  
  <style scoped>
  .vh-100 {
    height: 100vh;
  }
  
  .d-flex {
    display: flex;
  }
  
  .justify-content-center {
    justify-content: center;
  }
  
  .align-items-center {
    align-items: center;
  }
  
  .container {
    max-width: auto;
    padding: 20px;
  }
  
  .form-container {
    background-color: #2c3e50;
    color: white;
  }
  
  .border {
    border: 1px solid #007bff;
  }
  
  .p-4 {
    padding: 1.5rem !important;
  }
  
  .mb-3 {
    margin-bottom: 1rem !important;
  }
  
  .btn-block {
    display: block;
    width: 100%;
  }
  
  .mx-auto {
    margin-left: auto !important;
    margin-right: auto !important;
  }
  
  .text-center {
    text-align: center !important;
  }
  
  .page-colour {  
    background-color:#1e2a3a;
  }
  
  .alert-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1050;
  }
  
  .btn-close {
    background: none;
    border: none;
  }
  </style>