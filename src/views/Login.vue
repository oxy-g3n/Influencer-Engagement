<template>
  <div class="py-tutorial-container d-flex justify-content-center align-items-center">
    <div class="content-container">
      <div class="header">
        <h2>Login</h2>
      </div>
      <form @submit.prevent="login" class="form-container border p-5 rounded">
        <div class="form-group">
          <label for="username">Username:</label>
          <input type="text" id="username" v-model="username" class="form-control">
        </div>
        <div class="form-group">
          <label for="password">Password:</label>
          <input type="password" id="password" v-model="password" class="form-control">
        </div>
        <div class="row">
          <div class="col-md-12 mb-3">
            <button type="submit" class="btn btn-primary btn-block">Login</button>
          </div>
          <div class="col-md-6 mb-2">
            <button type="button" class="btn btn-info btn-block" @click="InfluencerRegister">Influencer<br>Registration</button>
          </div>
          <div class="col-md-6">
            <button type="button" class="btn btn-info btn-block" @click="SponsorRegister">Sponsor<br>Registration</button>
          </div>
        </div>
      </form>
      <!-- Fullscreen Alert Overlay -->
      <div v-if="alertMessage" class="alert-overlay d-flex justify-content-center align-items-center">
        <div class="alert" :class="alertClass" role="alert">
          {{ alertMessage }}
          <button type="button" class="close" @click="alertMessage = ''" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
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
      username: '',
      password: '',
      alertMessage: '',
      alertClass: '',
    };
  },
  setup() {
    const router = useRouter();
    return { router };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/users/auth', {
          username: this.username,
          password: this.password,
          action: "login"
        });
        if (response.data.Success) {
          this.showAlert('Login Successful', 'alert-success');
          const token = response.data.token;
          // const user_id = response.data.user_id;
          // const full_name = response.data.full_name;
          // const pin_code = response.data.pin_code;
          // const approval = response.data.approval;
          // const username = this.username;
          if (response.data.role === 'influencer') {
            setTimeout(() => {
              sessionStorage.setItem('influencer_Token', token);
              // sessionStorage.setItem('cust_name', username);
              // sessionStorage.setItem('cust_id', user_id);
              // sessionStorage.setItem('cust_Fullname', full_name);
              // sessionStorage.setItem('cust_pin', pin_code);
              // sessionStorage.setItem('cust_approval', approval);

              this.$router.push('/influencerDash');
            }, 1000);
          }
          if (response.data.role === 'sponsor') {
            setTimeout(() => {
              sessionStorage.setItem('sponsor_Token', token);
              sessionStorage.setItem('sponsor', "something");
              // sessionStorage.setItem('service_name', username);
              // sessionStorage.setItem('service_id', user_id);
              // sessionStorage.setItem('service_Fullname', full_name);

              this.$router.push('/sponsorDash');
            }, 1000);
          }
          if (response.data.role === 'admin') {
            setTimeout(() => {
              sessionStorage.setItem('admin_Token', token);

              // sessionStorage.setItem('admin_name', username);
              // sessionStorage.setItem('admin_id', user_id);
              // sessionStorage.setItem('admin_Fullname', full_name);

              this.$router.push('/AdminDash');
            }, 1000);
          }
        } else {
          this.showAlert('The username entered does not exist or the password is incorrect!', 'alert-warning');
        }
      } catch (error) {
        console.error('Login error:', error);
        this.showAlert('The username entered does not exist or the password is incorrect!', 'alert-warning');
      }
    },
    InfluencerRegister() {
      this.$router.push('/InfluencerRegistration');
    },
    SponsorRegister() {
      this.$router.push('/SponsorRegistration');
    },
    showAlert(message, alertClass) {
      this.alertMessage = message;
      this.alertClass = `alert ${alertClass} alert-dismissible fade show`;
    }
  }
};
</script>

<style scoped>
.py-tutorial-container {
  font-family: Arial, sans-serif;
  background-color: #1e2a3a;
  color: white;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.content-container {
  background-color: white;
  color: black;
  border-radius: 5px;
  width: 100%;
  max-width: 500px;
  padding: 20px;
}

.header {
  background-color: #2c3e50;
  padding: 20px;
  border-radius: 5px;
  text-align: center;
  margin-bottom: 20px;
}

.form-container {
  border: 1px solid #007bff;
}

.form-group {
  margin-bottom: 1rem;
}

.btn-block {
  display: block;
  width: 100%;
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

.alert {
  flex :auto;
  position: relative;
  margin: 1.25rem auto;
  border: 1px solid transparent;
  border-radius: .375rem;
  padding: .75rem 1.25rem;
  max-width: 500px;
}

.close {
  position: absolute;
  top: .5rem;
  right: .5rem;
}

@media (max-width: 768px) {
  .form-container {
    padding: 1rem;
  }
}

.header h2 {
  color: white;
}
</style>
