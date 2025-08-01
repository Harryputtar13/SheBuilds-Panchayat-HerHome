import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  HomeIcon, 
  CogIcon,
  PlayIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');
  
  // Data states
  const [preprocessingStats, setPreprocessingStats] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);
  const [trainingRequirements, setTrainingRequirements] = useState(null);
  const [allocationStatus, setAllocationStatus] = useState(null);
  const [users, setUsers] = useState([]);
  const [rooms, setRooms] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load all dashboard data in parallel
      const [
        preprocessingResponse,
        modelStatusResponse,
        trainingRequirementsResponse,
        allocationStatusResponse,
        usersResponse,
        roomsResponse
      ] = await Promise.all([
        axios.get('/api/v1/preprocessing-stats/'),
        axios.get('/api/v1/model-status/'),
        axios.get('/api/v1/training-requirements/'),
        axios.get('/api/v1/allocation-status/'),
        axios.get('/api/v1/users/'),
        axios.get('/api/v1/rooms/')
      ]);

      setPreprocessingStats(preprocessingResponse.data);
      setModelStatus(modelStatusResponse.data);
      setTrainingRequirements(trainingRequirementsResponse.data);
      setAllocationStatus(allocationStatusResponse.data);
      setUsers(usersResponse.data);
      setRooms(roomsResponse.data);
    } catch (error) {
      showMessage('Error loading dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (msg, type = 'info') => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => setMessage(''), 5000);
  };

  const handlePreprocessDataset = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/preprocess-dataset/');
      showMessage('Dataset preprocessing completed successfully!', 'success');
      loadDashboardData(); // Refresh data
    } catch (error) {
      showMessage('Error preprocessing dataset: ' + error.response?.data?.detail || error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleTrainModels = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/train-models/');
      showMessage('ML models trained successfully!', 'success');
      loadDashboardData(); // Refresh data
    } catch (error) {
      showMessage('Error training models: ' + error.response?.data?.detail || error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadModels = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/load-models/');
      showMessage('Models loaded successfully!', 'success');
      loadDashboardData(); // Refresh data
    } catch (error) {
      showMessage('Error loading models: ' + error.response?.data?.detail || error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAllocateRooms = async (strategy = 'balanced') => {
    setLoading(true);
    try {
      const response = await axios.post(`/api/v1/allocate-rooms/?strategy=${strategy}`);
      showMessage(`Room allocation completed using ${strategy} strategy!`, 'success');
      loadDashboardData(); // Refresh data
    } catch (error) {
      showMessage('Error allocating rooms: ' + error.response?.data?.detail || error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <UserGroupIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-2xl font-semibold text-gray-900">
                {allocationStatus?.total_users || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <HomeIcon className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Available Rooms</p>
              <p className="text-2xl font-semibold text-gray-900">
                {allocationStatus?.available_rooms || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Assigned Users</p>
              <p className="text-2xl font-semibold text-gray-900">
                {allocationStatus?.assigned_users || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <CogIcon className="h-8 w-8 text-orange-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">ML Models</p>
              <p className="text-2xl font-semibold text-gray-900">
                {modelStatus?.models_status?.models_trained ? 'Ready' : 'Not Ready'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={handlePreprocessDataset}
            disabled={loading}
            className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <PlayIcon className="h-4 w-4 mr-2" />
            Preprocess Data
          </button>

          <button
            onClick={handleTrainModels}
            disabled={loading || !trainingRequirements?.training_requirements?.can_train}
            className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
          >
            <CogIcon className="h-4 w-4 mr-2" />
            Train Models
          </button>

          <button
            onClick={handleLoadModels}
            disabled={loading}
            className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 disabled:opacity-50"
          >
            <InformationCircleIcon className="h-4 w-4 mr-2" />
            Load Models
          </button>

          <button
            onClick={() => handleAllocateRooms('balanced')}
            disabled={loading}
            className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 disabled:opacity-50"
          >
            <HomeIcon className="h-4 w-4 mr-2" />
            Allocate Rooms
          </button>
        </div>
      </div>

      {/* Progress Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Data Preprocessing</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>Users with Embeddings</span>
                <span>{preprocessingStats?.users_with_embeddings || 0} / {preprocessingStats?.total_users || 0}</span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${preprocessingStats?.completion_percentage || 0}%` }}
                ></div>
              </div>
            </div>
            <p className="text-sm text-gray-500">
              {preprocessingStats?.completion_percentage || 0}% complete
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Room Allocation</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>Assignment Rate</span>
                <span>{allocationStatus?.assignment_rate || 0}%</span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${allocationStatus?.assignment_rate || 0}%` }}
                ></div>
              </div>
            </div>
            <p className="text-sm text-gray-500">
              {allocationStatus?.assigned_users || 0} of {allocationStatus?.total_users || 0} users assigned
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderMLTraining = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Model Training Status</h3>
        
        {modelStatus && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Model Status</h4>
              <div className="space-y-2">
                <div className="flex items-center">
                  <span className="text-sm text-gray-600">KNN Model:</span>
                  <span className={`ml-2 text-sm ${modelStatus.models_status?.knn_model ? 'text-green-600' : 'text-red-600'}`}>
                    {modelStatus.models_status?.knn_model ? 'Ready' : 'Not Ready'}
                  </span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-600">SVD Model:</span>
                  <span className={`ml-2 text-sm ${modelStatus.models_status?.svd_model ? 'text-green-600' : 'text-red-600'}`}>
                    {modelStatus.models_status?.svd_model ? 'Ready' : 'Not Ready'}
                  </span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-600">Logistic Model:</span>
                  <span className={`ml-2 text-sm ${modelStatus.models_status?.logistic_model ? 'text-green-600' : 'text-red-600'}`}>
                    {modelStatus.models_status?.logistic_model ? 'Ready' : 'Not Ready'}
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-700 mb-2">Training Requirements</h4>
              {trainingRequirements && (
                <div className="space-y-2">
                  <div className="flex items-center">
                    <span className="text-sm text-gray-600">Minimum Users:</span>
                    <span className="ml-2 text-sm font-medium">{trainingRequirements.training_requirements?.minimum_users || 0}</span>
                  </div>
                  <div className="flex items-center">
                    <span className="text-sm text-gray-600">Current Users:</span>
                    <span className="ml-2 text-sm font-medium">{trainingRequirements.training_requirements?.current_users || 0}</span>
                  </div>
                  <div className="flex items-center">
                    <span className="text-sm text-gray-600">Can Train:</span>
                    <span className={`ml-2 text-sm ${trainingRequirements.training_requirements?.can_train ? 'text-green-600' : 'text-red-600'}`}>
                      {trainingRequirements.training_requirements?.can_train ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="mt-6 space-y-4">
          <button
            onClick={handlePreprocessDataset}
            disabled={loading}
            className="w-full md:w-auto px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            Preprocess Dataset
          </button>

          <button
            onClick={handleTrainModels}
            disabled={loading || !trainingRequirements?.training_requirements?.can_train}
            className="w-full md:w-auto px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 ml-2"
          >
            Train ML Models
          </button>

          <button
            onClick={handleLoadModels}
            disabled={loading}
            className="w-full md:w-auto px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 disabled:opacity-50 ml-2"
          >
            Load Saved Models
          </button>
        </div>
      </div>
    </div>
  );

  const renderRoomAllocation = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Room Allocation Strategies</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={() => handleAllocateRooms('compatibility_first')}
            disabled={loading}
            className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            Compatibility First
          </button>

          <button
            onClick={() => handleAllocateRooms('budget_first')}
            disabled={loading}
            className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
          >
            Budget First
          </button>

          <button
            onClick={() => handleAllocateRooms('location_first')}
            disabled={loading}
            className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 disabled:opacity-50"
          >
            Location First
          </button>

          <button
            onClick={() => handleAllocateRooms('balanced')}
            disabled={loading}
            className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 disabled:opacity-50"
          >
            Balanced
          </button>
        </div>
      </div>

      {allocationStatus && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Allocation Statistics</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{allocationStatus.total_users}</p>
              <p className="text-sm text-gray-600">Total Users</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{allocationStatus.assigned_users}</p>
              <p className="text-sm text-gray-600">Assigned Users</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">{allocationStatus.available_rooms}</p>
              <p className="text-sm text-gray-600">Available Rooms</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{allocationStatus.occupancy_rate}%</p>
              <p className="text-sm text-gray-600">Occupancy Rate</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderUsers = () => (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Users ({users.length})</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Age</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Occupation</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Budget</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map((user) => (
              <tr key={user.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.age}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.occupation}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.budget_range}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    user.embedding_vector ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {user.embedding_vector ? 'Processed' : 'Pending'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderRooms = () => (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Rooms ({rooms.length})</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Room</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Floor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Capacity</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rent</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {rooms.map((room) => (
              <tr key={room.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{room.room_number}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{room.floor_number}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{room.room_type}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{room.capacity}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${room.monthly_rent}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    room.is_occupied ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {room.is_occupied ? 'Occupied' : 'Available'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage AI Roommate Matching System - Data preprocessing, ML training, and room allocation
          </p>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 px-4 py-3 rounded-md ${
            messageType === 'success' ? 'bg-green-50 text-green-800' :
            messageType === 'error' ? 'bg-red-50 text-red-800' :
            'bg-blue-50 text-blue-800'
          }`}>
            {message}
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Overview', icon: ChartBarIcon },
              { id: 'ml-training', name: 'ML Training', icon: CogIcon },
              { id: 'room-allocation', name: 'Room Allocation', icon: HomeIcon },
              { id: 'users', name: 'Users', icon: UserGroupIcon },
              { id: 'rooms', name: 'Rooms', icon: HomeIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5 inline mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Loading Overlay */}
        {loading && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3 text-center">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mt-4">Processing...</h3>
                <p className="text-sm text-gray-500 mt-2">Please wait while we process your request.</p>
              </div>
            </div>
          </div>
        )}

        {/* Tab Content */}
        <div className="px-4 sm:px-0">
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'ml-training' && renderMLTraining()}
          {activeTab === 'room-allocation' && renderRoomAllocation()}
          {activeTab === 'users' && renderUsers()}
          {activeTab === 'rooms' && renderRooms()}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard; 