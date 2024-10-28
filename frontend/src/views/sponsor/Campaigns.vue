<template>
  <div class="campaign-dashboard container-fluid rounded-3 text-white py-4">
    <h1 class="mb-4">Campaign Dashboard</h1>

    <div class="row mb-4">
      <div class="col-md-6">
        <input 
          v-model="searchQuery"
          type="text"
          class="form-control"
          placeholder="Search campaigns by name or niche"
        >
      </div>
      <div class="col-md-6 text-end">
        <button @click="openNewCampaignModal" class="btn btn-primary">
          Add New Campaign
        </button>
      </div>
    </div>
    
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>
    
    <div v-else class="accordion" id="campaignAccordion">
      <div v-for="campaign in filteredCampaigns" :key="campaign.campaign_id" class="accordion-item text-white mb-3">
        <h2 class="accordion-header" :id="'heading' + campaign.campaign_id">
          <button 
            class="accordion-button text-white" 
            type="button" 
            data-bs-toggle="collapse" 
            :data-bs-target="'#collapse' + campaign.campaign_id" 
            aria-expanded="false" 
            :aria-controls="'collapse' + campaign.campaign_id"
          >
            {{ campaign.campaign_name }}
          </button>
        </h2>
        <div :id="'collapse' + campaign.campaign_id" class="accordion-collapse collapse" :aria-labelledby="'heading' + campaign.campaign_id" data-bs-parent="#campaignAccordion">
          <div class="accordion-body">
            <p><strong>Niche:</strong> {{ campaign.niche }}</p>
            <p><strong>Budget:</strong> ${{ campaign.budget }}</p>
            <div class="mb-3">
              <button @click="editCampaign(campaign)" class="btn btn-sm btn-outline-light me-2">Edit</button>
              <button @click="deleteCampaign(campaign.campaign_id)" class="btn btn-sm btn-outline-danger">Delete</button>
              <button @click="viewCampaignDetails(campaign)" class="btn btn-sm btn-outline-info ms-2">View Details</button>
            </div>

            <!-- Child Accordion for Ad Requests (Removed data-bs-parent to prevent issues) -->
            <div class="accordion" :id="'adRequestAccordion' + campaign.campaign_id">
              <div class="accordion-item text-white">
                <h2 class="accordion-header" :id="'adRequestHeading' + campaign.campaign_id">
                  <button 
                    class="accordion-button text-white collapsed" 
                    type="button" 
                    data-bs-toggle="collapse" 
                    :data-bs-target="'#adRequestCollapse' + campaign.campaign_id" 
                    aria-expanded="false" 
                    :aria-controls="'adRequestCollapse' + campaign.campaign_id"
                    @click="fetchAdRequests(campaign.campaign_id)"
                  >
                    View Ad Requests
                  </button>
                </h2>
                <div :id="'adRequestCollapse' + campaign.campaign_id" class="accordion-collapse collapse" :aria-labelledby="'adRequestHeading' + campaign.campaign_id">
                  <div class="accordion-body">
                    <div v-if="campaign.adRequests && campaign.adRequests.length > 0">
                      <h6 class="mb-3">Ad Requests</h6>
                      <div v-for="adRequest in campaign.adRequests" :key="adRequest.adRequest_id" class="card mb-2">
                        <div class="card-body text-white">
                          <h6>Ad Request #{{ adRequest.adRequest_id }}</h6>
                          <p><strong>Status:</strong> {{ adRequest.status }}</p>
                          <p><strong>Payout:</strong> ${{ adRequest.payout }}</p>
                          <div class="btn-group" role="group">
                            <button @click="editAdRequest(adRequest)" class="btn btn-sm btn-outline-primary">Edit</button>
                            <button 
                              v-if="['accepted', 'modification_accepted'].includes(adRequest.status)"
                              @click="closeAdRequest(adRequest.adRequest_id)" 
                              class="btn btn-sm btn-outline-warning"
                            >
                              Close
                            </button>
                            <button 
                              v-if="adRequest.status === 'open'"
                              @click="withdrawAdRequest(adRequest.adRequest_id)" 
                              class="btn btn-sm btn-outline-warning"
                            >
                              Withdraw
                            </button>
                            <button 
                              v-if="adRequest.status === 'modified'"
                              @click="acceptAdModification(adRequest.adRequest_id)"
                              class="btn btn-sm btn-outline-light"
                            >
                              Accept
                            </button>

                            <button 
                              v-if="adRequest.status === 'influencer_generated'"
                              @click="acceptRequestedAdModal(adRequest.adRequest_id)"
                              class="btn btn-sm btn-outline-light"
                            >
                              Accept
                            </button>

                            <button 
                              v-if="adRequest.status === 'modified' || adRequest.status === 'influencer_generated'"
                              @click="rejectAdModification(adRequest.adRequest_id)"
                              class="btn btn-sm btn-outline-danger"
                            >
                              Reject
                            </button>
                            <button @click="viewAdRequestDetails(adRequest)" class="btn btn-sm btn-outline-info">View Details</button>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-else class="text-muted">No ad requests found.</div>
                    <button @click="openNewAdRequestModal(campaign.campaign_id)" class="btn btn-success mt-3">
                      New Ad Request
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>

      <!-- New Campaign Modal -->
      <div class="modal fade" id="newCampaignModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content bg-dark text-white">
            <div class="modal-header">
              <h5 class="modal-title">Add New Campaign</h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body text-white">
              <input v-model="newCampaign.campaign_name" type="text" class="form-control text-white mb-3" placeholder="Campaign Name">
              <input v-model="newCampaign.campaign_description" type="text" class="form-control text-white mb-3" placeholder="Campaign Description">
              <input v-model="newCampaign.campaign_goals" type="text" class="form-control text-white mb-3" placeholder="Campaign Goals">
              <input v-model="newCampaign.niche" type="text" class="form-control text-white mb-3" placeholder="Campaign Niche">
              <input v-model="newCampaign.campaign_end_date" type="text" class="form-control text-white mb-3" placeholder="Campaign End Date YYYY-MM-DD">
              <input v-model="newCampaign.visibility" type="text" class="form-control text-white mb-3" placeholder="Campaign Visibility">
              <input v-model="newCampaign.budget" type="number" class="form-control text-white mb-3" placeholder="Campaign Budget">
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="submitNewCampaign">Submit</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Campaign Modal -->
      <div class="modal fade" id="editCampaignModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content bg-dark text-white">
            <div class="modal-header">
              <h5 class="modal-title">Edit Campaign</h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <input v-model="editedCampaign.campaign_name" type="text" class="form-control mb-3" placeholder="Campaign Name">
              <input v-model="editedCampaign.campaign_description" type="text" class="form-control mb-3" placeholder="Campaign Description">
              <input v-model="editedCampaign.campaign_goals" type="text" class="form-control mb-3" placeholder="Campaign Goals">
              <input v-model="editedCampaign.campaign_end_date" type="text" class="form-control mb-3" placeholder="Campaign End Date YYYY-MM-DD">
              <input v-model="editedCampaign.budget" type="number" class="form-control mb-3" placeholder="Campaign Budget">
              <input v-model="editedCampaign.niche" type="text" class="form-control mb-3" placeholder="Campaign Niche">
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="submitEditCampaign">Save Changes</button>
            </div>
          </div>
        </div>
      </div>
  
      <!-- New Ad Request Modal -->
      <div class="modal fade" id="newAdRequestModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content bg-dark text-white">
            <div class="modal-header">
              <h5 class="modal-title">Add New Ad Request</h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <input v-model="newAdRequest.influencer_id" type="number" class="form-control mb-3" placeholder="Influencer ID">
              <input v-model="newAdRequest.campaign_id" type="number" class="form-control mb-3" placeholder="Campaign ID">
              <input v-model="newAdRequest.requirements" type="text" class="form-control mb-3" placeholder="Ad Request Requirements">
              <input v-model="newAdRequest.payout" type="number" class="form-control mb-3" placeholder="Payout">
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="submitNewAdRequest">Submit</button>
            </div>
          </div>
        </div>
      </div>
  
<!-- Requirements Modal -->
<div class="modal fade" id="RequirementsModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content bg-dark text-white">
            <div class="modal-header">
              <h5 class="modal-title">Add Requirements</h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <input v-model="newAdRequest.requirements" type="text" class="form-control mb-3" placeholder="Ad Request Requirements">
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="acceptRequestedAd">Submit</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Ad Request Modal -->
      <div class="modal fade" id="editAdRequestModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content bg-dark text-white">
            <div class="modal-header">|
              <h5 class="modal-title">Edit Ad Request</h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              Influencer_id:<input v-model="editedAdRequest.influencer_id" type="number" class="form-control mb-3" placeholder="Influencer_id">
              Requirements:<input v-model="editedAdRequest.requirements" type="text" class="form-control mb-3" placeholder="Ad Request Requirements">
              Payout:<input v-model="editedAdRequest.payout" type="number" class="form-control mb-3" placeholder="Payout">
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="submitEditAdRequest">Save Changes</button>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Campaign Details Modal -->
      <div class="modal fade" id="campaignDetailsModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content bg-dark text-white">
            <div class="modal-header">
              <h5 class="modal-title">Campaign Details</h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <p><strong>Campaign Name:</strong> {{ selectedCampaign.campaign_name }}</p>
              <p><strong>Description:</strong> {{ selectedCampaign.campaign_description }}</p>
              <p><strong>Goals:</strong> {{ selectedCampaign.campaign_goals }}</p>
              <p><strong>Niche:</strong> {{ selectedCampaign.niche }}</p>
              <p><strong>Budget:</strong> ${{ selectedCampaign.budget }}</p>
              <p><strong>Start Date:</strong> {{ selectedCampaign.campaign_start_date }}</p>
              <p><strong>End Date:</strong> {{ selectedCampaign.campaign_end_date }}</p>
              <p><strong>Visibility:</strong> {{ selectedCampaign.visibility?"Public":"Private" }}</p>
              <p><strong>Niche:</strong> {{ selectedCampaign.niche }}</p>
              <p><strong>Company name:</strong> {{ selectedCampaign.company_name }}</p>
              <p><strong>Industry:</strong> {{ selectedCampaign.industry }}</p>
              <!-- Add any additional campaign details here -->
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Ad Request Details Modal -->
      <div class="modal fade" id="adRequestDetailsModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content bg-dark text-white">
            <div class="modal-header">
              <h5 class="modal-title">Ad Request Details</h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <p><strong>Ad Request ID:</strong> {{ selectedAdRequest.adRequest_id }}</p>
              <p><strong>Campaign ID:</strong> {{ selectedAdRequest.campaign_id }}</p>
              <p><strong>Sponsor ID:</strong> {{ selectedAdRequest.sponsor_id }}</p>
              <p><strong>Influencer ID:</strong> {{ selectedAdRequest.influencer_id }}</p>
              <p><strong>Requirements:</strong> {{ selectedAdRequest.requirements }}</p>
              <p><strong>Payout:</strong> ${{ selectedAdRequest.payout }}</p>
              <p><strong>Status:</strong> {{ selectedAdRequest.status }}</p>
              <p><strong>New Payout:</strong> ${{ selectedAdRequest.new_payout }}</p>
              <!-- Add any additional ad request details here -->
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>


<script>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { Modal } from 'bootstrap';
import VueJwtDecode from 'vue-jwt-decode';

export default {
  name: 'CampaignDashboard',
  setup() {
    const campaigns = ref([]);
    const searchQuery = ref('');
    const loading = ref(true);
    const error = ref(null);
    const newCampaign = ref({ name: '', niche: '', budget: null });
    const editedCampaign = ref({});
    const newAdRequest = ref({ requirements: '', payout: null , adRequest_id: null});
    const editedAdRequest = ref({});
    const selectedCampaign = ref({});
    const selectedAdRequest = ref({});

    const fetchCampaigns = async () => {
      try {
        loading.value = true;
        let token = sessionStorage.getItem('sponsor_Token');
        let decoded = VueJwtDecode.decode(token)
        const userID = decoded['user_id'];
        const response = await axios.get('http://127.0.0.1:5000/campaigns/get_campaigns/'+userID+'?action=sponsor_id', {
          params: { action: 'user_id' },
          headers: {
            'Authorization': sessionStorage.getItem('sponsor_Token'),
            'Content-Type': 'application/json'
          }
        });
        campaigns.value = response.data.campaigns;
        loading.value = false;
      } catch (err) {
        console.error('Error fetching campaigns:', err);
        error.value = 'An error occurred while fetching campaigns. Please try again.';
        loading.value = false;
      }
    };

    const fetchAdRequests = async (campaignId) => {
      try {
        
        const response = await axios.get(`http://127.0.0.1:5000/ads/get_ads/${campaignId}`, {
          params: { action: 'campaign_id' },
          headers: {
            'Authorization': sessionStorage.getItem('sponsor_Token'),
            'Content-Type': 'application/json'
          }
        });
        const campaign = campaigns.value.find(c => c.campaign_id === campaignId);
        if (campaign) {
          campaign.adRequests = response.data.ads.map(ad => ({
            adRequest_id: ad.adRequest_id,
            campaign_id: ad.campaign_id,
            sponsor_id: ad.sponsor_id,
            influencer_id: ad.influencer_id,
            requirements: ad.requirements,
            payout: ad.payout,
            status: ad.status,
            new_payout: ad.new_payout
          })).filter(ad => 
            ad.status === 'accepted' || ad.status === 'open' || ad.status === 'modified' || ad.status === 'modification_accepted' || ad.status === 'influencer_generated'
          );
        }
      } catch (err) {
        console.error('Error fetching ad requests:', err);
        error.value = 'An error occurred while fetching ad requests. Please try again.';
      }
    };

    onMounted(fetchCampaigns);

    const filteredCampaigns = computed(() => {
      
      
      const text = searchQuery.value.toString();
      const query = text.toLowerCase();

      return campaigns.value.filter(campaign => 
        campaign.campaign_name.toLowerCase().includes(query) ||
        campaign.niche.toLowerCase().includes(query)
      );
    });

    const openNewCampaignModal = () => {
      new Modal(document.getElementById('newCampaignModal')).show();
    };

    const submitNewCampaign = async () => {
      try {
      let token = sessionStorage.getItem('sponsor_Token');
      let decoded = VueJwtDecode.decode(token)
      const local_company_name = decoded['company_name'];
      const local_industry = decoded['industry']
        const dataToSend = 
        {
          ...newCampaign.value,  // Spread the existing newCampaign data
          company_name: local_company_name,  // Add any additional fields
          industry: local_industry
        };
        const response = await axios.post('http://127.0.0.1:5000/campaigns/make_campaign', dataToSend, {
          headers: {
            'Authorization': sessionStorage.getItem('sponsor_Token'),
            'Content-Type': 'application/json'
          }
        });
        alert(response.data.status);
      } catch (err) {
        console.error('Error creating new campaign:', err);
        alert( 'An error occurred while creating the campaign. Please try again.');
      }
    };

    const editCampaign = (campaign) => {
      editedCampaign.value = { ...campaign };
      new Modal(document.getElementById('editCampaignModal')).show();
    };

    const submitEditCampaign = async () => {
      try {
        const response = await axios.put(`http://127.0.0.1:5000/campaigns/edit_campaign/${editedCampaign.value.campaign_id}`, editedCampaign.value, {
          headers: {
            'Authorization': sessionStorage.getItem('sponsor_Token'),
            'Content-Type': 'application/json'
          }
        });

        alert(response.data.status);
      } catch (err) {
        console.error('Error updating campaign:', err);
        alert( 'An error occurred while updating the campaign. Please try again.');
      }
    };

    const deleteCampaign = async (campaignId) => {
      if (confirm('Are you sure you want to delete this campaign?')) {
        try {
          await axios.delete(`http://127.0.0.1:5000/campaigns/delete_campaign/${campaignId}`, {
            headers: {
              'Authorization': sessionStorage.getItem('sponsor_Token'),
              'Content-Type': 'application/json'
            }
          });
          campaigns.value = campaigns.value.filter(c => c.campaign_id !== campaignId);
        } catch (err) {
          console.error('Error deleting campaign:', err);
          error.value = 'An error occurred while deleting the campaign. Please try again.';
        }
      }
    };
    const acceptRequestedAdModal = (adRequestId) => {
      newAdRequest.value.adRequest_id = adRequestId;
      new Modal(document.getElementById('RequirementsModal')).show();
    };

    const acceptRequestedAd = async () => {
      try {
        const adRequestId = newAdRequest.value.adRequest_id;
        let currentStatus = '';
        let campaignId = null;
        campaigns.value.forEach(campaign => {
          if (campaign.adRequests) {
            const adRequest = campaign.adRequests.find(ar => ar.adRequest_id === adRequestId);
            if (adRequest) {
              currentStatus = adRequest.status;
              campaignId = campaign.campaign_id;
            }
          }
        });

        const requirements = newAdRequest.value.requirements;

        const response = await axios.put(`http://127.0.0.1:5000/ads/edit_ad_status/${adRequestId}`, {
          'current_status': currentStatus,
          'new_status': 'accepted',
          'requirements': requirements
        }, {
          headers: {
            'Authorization': sessionStorage.getItem('sponsor_Token'),
            'Content-Type': 'application/json'
          }
        });

        alert(response.data.status);
        // Close the modal after successful submission
        Modal.getInstance(document.getElementById('RequirementsModal')).hide();
        // Refresh the ad requests for the campaign
        if (campaignId) {
          await fetchAdRequests(campaignId);
        }
      } catch (err) {
        console.error('Error accepting the requested ad:', err);
        alert('An error occurred while accepting the requested ad. Please try again.');
      }
    };


    const openNewAdRequestModal = (campaignId) => {
      newAdRequest.value.campaign_id = campaignId;
      new Modal(document.getElementById('newAdRequestModal')).show();
    };

    const submitNewAdRequest = async () => {
      try {
        const response = await axios.post('http://127.0.0.1:5000/ads/make_ad_request', newAdRequest.value, {
          headers: {
            'Authorization': sessionStorage.getItem('sponsor_Token'),
            'Content-Type': 'application/json'
          }
        });

        alert(response.data.status);
      } catch (err) {
        console.error('Error creating new ad request:', err);
        alert('An error occurred while creating the ad request. Please try again.');
      }
    };

    const editAdRequest = (adRequest) => {
      editedAdRequest.value = { ...adRequest };
      new Modal(document.getElementById('editAdRequestModal')).show();
    };

    const submitEditAdRequest = async () => {
      try {
        const response = await axios.put(`http://127.0.0.1:5000/ads/edit_ad_request/${editedAdRequest.value.adRequest_id}`, editedAdRequest.value, {
          headers: {
            'Authorization': sessionStorage.getItem('sponsor_Token'),
            'Content-Type': 'application/json'
          }
        });
        alert(response.data.status);
      } catch (err) {
        console.error('Error updating ad request:', err);
        alert('An error occurred while editing the ad request. Please try again.');
      }
    };

    

    const acceptAdModification = async (adRequestId) => {
  try {
    let currentStatus = '';
    campaigns.value.forEach(campaign => {
      if (campaign.adRequests) {
        const adRequest = campaign.adRequests.find(ar => ar.adRequest_id === adRequestId);
        if (adRequest) {
          currentStatus = adRequest.status;
        }
      }
    });
    const response = await axios.put(`http://127.0.0.1:5000/ads/edit_ad_status/${adRequestId}`, {
      'current_status': currentStatus,
      'new_status': 'modification_accepted'
    }, {
      headers: {
        'Authorization': sessionStorage.getItem('sponsor_Token'),
        'Content-Type': 'application/json'
      }
    });
    alert(response.data.status);
  } catch (err) {
    console.error('Error accepting the modification:', err);
    alert('An error occurred while accepting the modification. Please try again.');
  }
};


const rejectAdModification = async (adRequestId) => {
  try {
    let currentStatus = '';
    campaigns.value.forEach(campaign => {
      if (campaign.adRequests) {
        const adRequest = campaign.adRequests.find(ar => ar.adRequest_id === adRequestId);
        if (adRequest) {
          currentStatus = adRequest.status;
        }
      }
    });
    const response = await axios.put(`http://127.0.0.1:5000/ads/edit_ad_status/${adRequestId}`, {
      'current_status': currentStatus,
      'new_status': 'modification_rejected'
    }, {
      headers: {
        'Authorization': sessionStorage.getItem('sponsor_Token'),
        'Content-Type': 'application/json'
      }
    });
    alert(response.data.status);
  } catch (err) {
    console.error('Error accepting the modification:', err);
    alert('An error occurred while accepting the modification. Please try again.');
  }
};






    const withdrawAdRequest = async (adRequestId) => {
  try {
    let currentStatus = '';
    campaigns.value.forEach(campaign => {
      if (campaign.adRequests) {
        const adRequest = campaign.adRequests.find(ar => ar.adRequest_id === adRequestId);
        if (adRequest) {
          currentStatus = adRequest.status;
        }
      }
    });

    const response = await axios.put(`http://127.0.0.1:5000/ads/edit_ad_status/${adRequestId}`, {
      'current_status': currentStatus,
      'new_status': 'withdrawn'
    }, {
      headers: {
        'Authorization': sessionStorage.getItem('sponsor_Token'),
        'Content-Type': 'application/json'
      }
    });
    alert(response.data.status);
  } catch (err) {
    console.error('Error withdrawing ad request:', err);
    alert('An error occurred while withdrawing the ad request. Please try again.');
  }
};

const closeAdRequest = async (adRequestId) => {
  try {
    let currentStatus = '';
    campaigns.value.forEach(campaign => {
      if (campaign.adRequests) {
        const adRequest = campaign.adRequests.find(ar => ar.adRequest_id === adRequestId);
        if (adRequest) {
          currentStatus = adRequest.status;
        }
      }
    });

    const response = await axios.put(`http://127.0.0.1:5000/ads/edit_ad_status/${adRequestId}`, {
      'current_status': currentStatus,
      'new_status': 'completed'
    }, {
      headers: {
        'Authorization': sessionStorage.getItem('sponsor_Token'),
        'Content-Type': 'application/json'
      }
    });
    alert(response.data.status);
  } catch (err) {
    console.error('Error closing ad request:', err);
    alert('An error occurred while closing the ad request. Please try again.');
  }
};
    const viewCampaignDetails = (campaign) => {
      selectedCampaign.value = campaign;
      new Modal(document.getElementById('campaignDetailsModal')).show();
    };

    const viewAdRequestDetails = (adRequest) => {
      selectedAdRequest.value = adRequest;
      new Modal(document.getElementById('adRequestDetailsModal')).show();
    };

    return {
      campaigns,
      searchQuery,
      loading,
      error,
      newCampaign,
      editedCampaign,
      newAdRequest,
      editedAdRequest,
      selectedCampaign,
      selectedAdRequest,
      filteredCampaigns,
      fetchAdRequests,
      openNewCampaignModal,
      submitNewCampaign,
      editCampaign,
      submitEditCampaign,
      deleteCampaign,
      openNewAdRequestModal,
      submitNewAdRequest,
      editAdRequest,
      submitEditAdRequest,
      acceptRequestedAd,
      acceptRequestedAdModal,
      closeAdRequest,
      withdrawAdRequest,
      acceptAdModification,
      rejectAdModification,
      viewCampaignDetails,
      viewAdRequestDetails
    };
  }
};
</script>

<style scoped>

.accordion-body{
  background-color: #34495e;
}

.campaign-dashboard {
  font-family: Arial, sans-serif;
  background-color: #1e2a3a;
  
  padding: 20px;
  min-height: 100vh;
}

.accordion-item {
  transition: all 0.3s ease;
  border-color:#3a536b;
}

.accordion-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.card-body{
  background-color: #3a536b;
}

.btn-group .btn {
  transition: all 0.2s ease;
}

.btn-group .btn:hover {
  transform: translateY(-2px);
}

.modal-content {
  border: 1px solid #4a6278;
}

.modal-header, .modal-footer {
  border-color: #4a6278;
}

.form-control, .form-select {
  background-color: #2c3e50;
  border-color: #2c3e50;
  color: white;
}

.form-control::placeholder, .form-select::placeholder {
  color: #a0aec0;
}

.form-control:focus, .form-select:focus {
  background-color: #34495e;
  border-color: #3498db;
  box-shadow: 0 0 0 0.2rem rgba(52, 152, 219, 0.25);
}

.accordion-button{
  color: #2c3e50;
  background-color: #2c3e50;
}

.accordion-button:not(.collapsed) {
  color: #2c3e50;
  background-color: #2c3e50;
}

.accordion-button:focus {
  box-shadow: none;
  border-color: rgba(0,0,0,.125);
}

.accordion-button::after {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23ffffff'%3e%3cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3e%3c/svg%3e");
}

.accordion-button:not(.collapsed)::after {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23ffffff'%3e%3cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3e%3c/svg%3e");
}
</style>