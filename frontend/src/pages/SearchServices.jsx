import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Search, MapPin, Phone, MessageCircle, Tractor, Wrench, Truck } from 'lucide-react'

const SearchServices = () => {
  const [services, setServices] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [serviceType, setServiceType] = useState('')
  const [location, setLocation] = useState({ lat: null, lng: null })
  const [showSuggestions, setShowSuggestions] = useState(true)
  const navigate = useNavigate()

  const API_URL = import.meta.env.VITE_API_URL || '/api'

  const serviceTypes = [
    { value: 'tractor', label: 'Tractor', icon: Tractor },
    { value: 'jcb', label: 'JCB', icon: Wrench },
    { value: 'auto', label: 'Auto', icon: Truck },
    { value: 'farm_service', label: 'Farm Service', icon: Tractor },
  ]

  useEffect(() => {
    // Get user location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          })
        },
        (error) => {
          console.error('Error getting location:', error)
        }
      )
    }
    
    // Load auto-suggestions based on user's location (village/district)
    loadSuggestions()
  }, [])

  const loadSuggestions = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_URL}/services/suggestions`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (response.data.suggestions && response.data.suggestions.length > 0) {
        setSuggestions(response.data.suggestions)
        setShowSuggestions(true)
      }
    } catch (error) {
      console.error('Error loading suggestions:', error)
    }
  }

  const handleSearch = async () => {
    if (!location.lat || !location.lng) {
      alert('Please allow location access to search services')
      return
    }

    setLoading(true)
    try {
      const response = await axios.get(`${API_URL}/services/search`, {
        params: {
          lat: location.lat,
          lng: location.lng,
          type: serviceType,
          search: searchTerm,
          radius: 10 // 10km radius
        }
      })
      setServices(response.data)
    } catch (error) {
      console.error('Search error:', error)
      alert('Failed to search services')
    } finally {
      setLoading(false)
    }
  }

  const handleCall = (phone) => {
    window.open(`tel:${phone}`)
  }

  const handleWhatsApp = (phone) => {
    window.open(`https://wa.me/${phone.replace(/\D/g, '')}`)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4 gradient-text">Find Services</h1>
        <p className="text-slate-600 dark:text-slate-400">
          Search for tractors, JCBs, autos, and more near you
        </p>
      </div>

      {/* Search Bar */}
      <div className="glass-card p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by name, village..."
                className="glass-input pl-10"
              />
            </div>
          </div>

          <div>
            <select
              value={serviceType}
              onChange={(e) => setServiceType(e.target.value)}
              className="glass-input"
            >
              <option value="">All Services</option>
              {serviceTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleSearch}
            disabled={loading}
            className="glass-button disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {/* Auto-Suggestions Section */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold gradient-text">
              💡 Suggested for You (Same Location)
            </h2>
            <button
              onClick={() => setShowSuggestions(false)}
              className="text-sm text-slate-600 dark:text-slate-400 hover:text-primary-600 dark:hover:text-primary-400"
            >
              Hide
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            {suggestions.map((service, index) => {
              const IconComponent = serviceTypes.find(t => t.value === service.type)?.icon || Tractor
              return (
                <div
                  key={service._id || index}
                  className="glass-card p-6 border-2 border-primary-500/30 relative"
                >
                  <div className="absolute top-2 right-2">
                    <span className="text-xs px-2 py-1 rounded-full bg-primary-500/20 text-primary-600 dark:text-primary-400">
                      {service.matchType === 'same_location' ? '📍 Same Location' : '🔍 Nearby'}
                    </span>
                  </div>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded-lg gradient-bg flex items-center justify-center">
                        <IconComponent className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">{service.providerName}</h3>
                        <p className="text-sm text-slate-600 dark:text-slate-400 capitalize">
                          {service.type.replace('_', ' ')}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-slate-600 dark:text-slate-400">
                      <MapPin className="w-4 h-4 mr-2" />
                      {service.village}, {service.district}
                    </div>
                    <div className="text-xs text-primary-600 dark:text-primary-400 font-semibold">
                      {service.matchText}
                    </div>
                    <div className="text-lg font-bold text-primary-600 dark:text-primary-400">
                      ₹{service.pricePerHour || service.pricePerTrip} / {service.pricePerHour ? 'hour' : 'trip'}
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleCall(service.phone)}
                      className="flex-1 glass-button flex items-center justify-center space-x-2"
                    >
                      <Phone className="w-4 h-4" />
                      <span>Call</span>
                    </button>
                    <button
                      onClick={() => handleWhatsApp(service.phone)}
                      className="flex-1 glass-button flex items-center justify-center space-x-2"
                    >
                      <MessageCircle className="w-4 h-4" />
                      <span>WhatsApp</span>
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Services Grid */}
      {services.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service) => {
            const IconComponent = serviceTypes.find(t => t.value === service.type)?.icon || Tractor
            return (
              <div key={service._id} className="glass-card p-6 hover:scale-105 transition-transform">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-lg gradient-bg flex items-center justify-center">
                      <IconComponent className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{service.providerName}</h3>
                      <p className="text-sm text-slate-600 dark:text-slate-400 capitalize">
                        {service.type.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-slate-600 dark:text-slate-400">
                    <MapPin className="w-4 h-4 mr-2" />
                    {service.village}, {service.district}
                  </div>
                  {service.distance && (
                    <div className="text-sm text-primary-600 dark:text-primary-400">
                      {service.distance.toFixed(1)} km away
                    </div>
                  )}
                  <div className="text-lg font-bold text-primary-600 dark:text-primary-400">
                    ₹{service.pricePerHour || service.pricePerTrip} / {service.pricePerHour ? 'hour' : 'trip'}
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => handleCall(service.phone)}
                    className="flex-1 glass-button flex items-center justify-center space-x-2"
                  >
                    <Phone className="w-4 h-4" />
                    <span>Call</span>
                  </button>
                  <button
                    onClick={() => handleWhatsApp(service.phone)}
                    className="flex-1 glass-button flex items-center justify-center space-x-2"
                  >
                    <MessageCircle className="w-4 h-4" />
                    <span>WhatsApp</span>
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="text-center py-12 glass-card">
          <Search className="w-16 h-16 mx-auto mb-4 text-slate-400" />
          <p className="text-slate-600 dark:text-slate-400">
            {loading ? 'Searching for services...' : 'Search for services to see results'}
          </p>
        </div>
      )}
    </div>
  )
}

export default SearchServices

