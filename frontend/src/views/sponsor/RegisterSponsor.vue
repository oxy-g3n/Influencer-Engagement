<template>
  <div class="vh-100 d-flex justify-content-center align-items-center page-colour">
    <div class="container">
      <div class="row">
        <div class="col-md-10 mx-auto">
          <h2 class="text-center text-white mb-4">Sponsor Registration</h2>
          <form @submit.prevent="registerSponsor" class="form-container border p-4 border-primary rounded">
            <div class="row">
              <div class="col-md-6">
                <div class="form-group mb-3">
                  <label for="username">Username:</label>
                  <input type="text" id="username" v-model="formData.username" class="form-control" required>
                </div>
                <div class="form-group mb-3">
                  <label for="password">Password:</label>
                  <input type="password" id="password" v-model="formData.password" class="form-control" required>
                </div>
                <div class="form-group mb-3">
                  <label for="email">Email:</label>
                  <input type="email" id="email" v-model="formData.mail" class="form-control" required>
                </div>
                <div class="form-group mb-3">
                  <label for="fullName">Full Name:</label>
                  <input type="text" id="fullName" v-model="formData.full_name" class="form-control" required>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-group mb-3">
                  <label for="companyName">Company Name:</label>
                  <input type="text" id="companyName" v-model="formData.company_name" class="form-control" required>
                </div>
                <div class="form-group mb-3">
                  <label for="industry">Industry:</label>
                  <input type="text" id="industry" v-model="formData.industry" class="form-control" required>
                </div>
              </div>
            </div>
            <div class="row mt-3">
              <div class="col-md-6 mb-3">
                <button type="submit" class="btn btn-primary btn-block">Register</button>
              </div>
              <div class="col-md-6">
                <button type="button" class="btn btn-secondary btn-block" @click="cancel">Cancel</button>
              </div>
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

export default {
  data() {
    return {
      formData: {
        username: '',
        password: '',
        mail: '',
        full_name: '',
        company_name: '',
        industry: '',
      },
      alertMessage: '',
      alertClass: '',
    };
  },
  setup() {
    const router = useRouter();
    return { router };
  },
  methods: {
    async registerSponsor() {
      const formData = new FormData();
      formData.append('action', 'sponsor_reg');
      Object.keys(this.formData).forEach(key => {
        formData.append(key, this.formData[key]);
      });

      try {
        const response = await axios.post('http://127.0.0.1:5000/users/register', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        this.showAlert(response.data, 'alert-success');
        setTimeout(() => {
          this.$router.push('/');
        }, 2000);
      } catch (error) {
        console.error('Registration error:', error);
        this.showAlert(error.response.data || 'An error occurred during registration', 'alert-danger');
      }
    },
    cancel() {
      this.$router.push('/');
    },
    showAlert(message, alertClass) {
      this.alertMessage = message;
      this.alertClass = `alert ${alertClass} alert-dismissible fade show`;
      setTimeout(() => {
        this.alertMessage = '';
      }, 5000);
    }
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