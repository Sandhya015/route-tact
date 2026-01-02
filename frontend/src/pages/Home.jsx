import { Link } from 'react-router-dom'
import { Tractor, Wrench, Truck, MapPin, Phone, Star } from 'lucide-react'

const Home = () => {
  const services = [
    { icon: Tractor, name: 'Tractor', color: 'text-green-500' },
    { icon: Wrench, name: 'JCB', color: 'text-yellow-500' },
    { icon: Truck, name: 'Auto', color: 'text-blue-500' },
    { icon: Wrench, name: 'Farm Services', color: 'text-purple-500' },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl md:text-6xl font-bold mb-6">
          <span className="gradient-text">Connect with Rural Services</span>
        </h1>
        <p className="text-xl md:text-2xl text-slate-600 dark:text-slate-400 mb-8 max-w-3xl mx-auto">
          Find tractors, JCBs, autos, and farm services near you. 
          Connecting rural communities with trusted service providers.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/register"
            className="glass-button text-lg px-8 py-4 inline-flex items-center justify-center space-x-2"
          >
            <span>Sign Up</span>
          </Link>
          <Link
            to="/login"
            className="glass-card px-8 py-4 text-lg font-semibold text-primary-600 dark:text-primary-400 hover:bg-primary-500/10 dark:hover:bg-primary-500/20 transition-all inline-flex items-center justify-center"
          >
            Login
          </Link>
        </div>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        {services.map((service, index) => (
          <div key={index} className="glass-card p-6 hover:scale-105 transition-transform cursor-pointer group">
            <service.icon className={`w-12 h-12 ${service.color} mb-4 group-hover:scale-110 transition-transform`} />
            <h3 className="text-xl font-semibold mb-2">{service.name}</h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Find nearby {service.name.toLowerCase()} services
            </p>
          </div>
        ))}
      </div>

      {/* Features Section */}
      <div className="glass-card p-8 md:p-12 mb-16">
        <h2 className="text-3xl font-bold text-center mb-12 gradient-text">
          Why Choose RuralConnect?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-16 h-16 rounded-full gradient-bg flex items-center justify-center mx-auto mb-4">
              <MapPin className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Location-Based</h3>
            <p className="text-slate-600 dark:text-slate-400">
              Find services near your location instantly
            </p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 rounded-full gradient-bg flex items-center justify-center mx-auto mb-4">
              <Phone className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Direct Contact</h3>
            <p className="text-slate-600 dark:text-slate-400">
              Call or WhatsApp providers directly
            </p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 rounded-full gradient-bg flex items-center justify-center mx-auto mb-4">
              <Star className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Trusted Providers</h3>
            <p className="text-slate-600 dark:text-slate-400">
              Verified service providers in your area
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center glass-card p-8 md:p-12">
        <h2 className="text-3xl font-bold mb-4 gradient-text">
          Ready to Get Started?
        </h2>
        <p className="text-slate-600 dark:text-slate-400 mb-6">
          Join thousands of users finding and providing rural services
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/register"
            className="glass-button text-lg px-8 py-4 inline-block text-center"
          >
            Sign Up Now
          </Link>
          <Link
            to="/login"
            className="glass-card px-8 py-4 text-lg font-semibold text-primary-600 dark:text-primary-400 hover:bg-primary-500/10 dark:hover:bg-primary-500/20 transition-all inline-block text-center"
          >
            Login
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Home

