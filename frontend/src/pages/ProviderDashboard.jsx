import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'
import { Plus, Trash2, Edit, Tractor, Wrench, Truck, MapPin, Phone } from 'lucide-react'

const ProviderDashboard = () => {
  const { user } = useAuth()
  const [services, setServices] = useState([])
  const [loading, setLoading] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    type: 'tractor',
    pricePerHour: '',
    pricePerTrip: '',
    description: '',
    available: true
  })

  const API_URL = import.meta.env.VITE_API_URL || '/api'
  const token = localStorage.getItem('token')

  useEffect(() => {
    fetchServices()
  }, [])

  const fetchServices = async () => {
    try {
      const response = await axios.get(`${API_URL}/services/my-services`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setServices(response.data)
    } catch (error) {
      console.error('Error fetching services:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      await axios.post(
        `${API_URL}/services`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      setShowForm(false)
      setFormData({
        type: 'tractor',
        pricePerHour: '',
        pricePerTrip: '',
        description: '',
        available: true
      })
      fetchServices()
    } catch (error) {
      alert('Failed to add service')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this service?')) return

    try {
      await axios.delete(`${API_URL}/services/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      fetchServices()
    } catch (error) {
      alert('Failed to delete service')
    }
  }

  const toggleAvailability = async (id, currentStatus) => {
    try {
      await axios.patch(
        `${API_URL}/services/${id}`,
        { available: !currentStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      fetchServices()
    } catch (error) {
      alert('Failed to update availability')
    }
  }

  const serviceIcons = {
    tractor: Tractor,
    jcb: Wrench,
    auto: Truck,
    farm_service: Tractor
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2 gradient-text">Provider Dashboard</h1>
          <p className="text-slate-600 dark:text-slate-400">
            Manage your services and availability
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="glass-button flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Add Service</span>
        </button>
      </div>

      {/* Add Service Form */}
      {showForm && (
        <div className="glass-card p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">Add New Service</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Service Type</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="glass-input"
                  required
                >
                  <option value="tractor">Tractor</option>
                  <option value="jcb">JCB</option>
                  <option value="auto">Auto</option>
                  <option value="farm_service">Farm Service</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Price per Hour (₹)</label>
                <input
                  type="number"
                  value={formData.pricePerHour}
                  onChange={(e) => setFormData({ ...formData, pricePerHour: e.target.value })}
                  className="glass-input"
                  placeholder="500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Price per Trip (₹)</label>
                <input
                  type="number"
                  value={formData.pricePerTrip}
                  onChange={(e) => setFormData({ ...formData, pricePerTrip: e.target.value })}
                  className="glass-input"
                  placeholder="2000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="glass-input"
                  rows="3"
                  placeholder="Service description..."
                />
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={loading}
                className="glass-button disabled:opacity-50"
              >
                {loading ? 'Adding...' : 'Add Service'}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="glass-card px-6 py-3 hover:bg-red-500/10 dark:hover:bg-red-500/20"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Services List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {services.map((service) => {
          const IconComponent = serviceIcons[service.type] || Tractor
          return (
            <div key={service._id} className="glass-card p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 rounded-lg gradient-bg flex items-center justify-center">
                    <IconComponent className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold capitalize">{service.type.replace('_', ' ')}</h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      service.available
                        ? 'bg-green-500/20 text-green-500'
                        : 'bg-red-500/20 text-red-500'
                    }`}>
                      {service.available ? 'Available' : 'Not Available'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-2 mb-4">
                {service.pricePerHour && (
                  <div className="text-sm">
                    <span className="text-slate-600 dark:text-slate-400">Per Hour: </span>
                    <span className="font-semibold">₹{service.pricePerHour}</span>
                  </div>
                )}
                {service.pricePerTrip && (
                  <div className="text-sm">
                    <span className="text-slate-600 dark:text-slate-400">Per Trip: </span>
                    <span className="font-semibold">₹{service.pricePerTrip}</span>
                  </div>
                )}
                {service.description && (
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    {service.description}
                  </p>
                )}
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={() => toggleAvailability(service._id, service.available)}
                  className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    service.available
                      ? 'bg-red-500/10 text-red-500 hover:bg-red-500/20'
                      : 'bg-green-500/10 text-green-500 hover:bg-green-500/20'
                  }`}
                >
                  {service.available ? 'Mark Unavailable' : 'Mark Available'}
                </button>
                <button
                  onClick={() => handleDelete(service._id)}
                  className="p-2 rounded-lg bg-red-500/10 text-red-500 hover:bg-red-500/20 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {services.length === 0 && (
        <div className="text-center py-12 glass-card">
          <Tractor className="w-16 h-16 mx-auto mb-4 text-slate-400" />
          <p className="text-slate-600 dark:text-slate-400 mb-4">
            No services added yet
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="glass-button"
          >
            Add Your First Service
          </button>
        </div>
      )}
    </div>
  )
}

export default ProviderDashboard

