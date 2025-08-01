import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Mic, Users, Sparkles, ArrowRight } from 'lucide-react';

const HomePage = () => {
  const features = [
    {
      icon: <Mic className="w-8 h-8" />,
      title: "Smart Survey",
      description: "Complete your roommate preferences survey with our intuitive interface."
    },
    {
      icon: <Sparkles className="w-8 h-8" />,
      title: "AI-Powered Matching",
      description: "Advanced machine learning algorithms find your perfect roommate match."
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Smart Compatibility",
      description: "Get detailed compatibility scores and explanations for each match."
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 text-white">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              Find Your Perfect
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-orange-300">
                Roommate
              </span>
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100 max-w-3xl mx-auto">
              AI-powered roommate matching system designed specifically for women
            </p>
            
            {/* Her Home Highlight */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 mb-8 max-w-2xl mx-auto">
              <div className="flex items-center justify-center mb-4">
                <Sparkles className="w-8 h-8 mr-3 text-yellow-300" />
                <span className="text-lg font-semibold">Her Home</span>
              </div>
              <p className="text-blue-100 mb-4">
                Find your perfect roommate with our AI-powered matching system
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/survey"
                  className="bg-white text-blue-600 px-6 py-3 rounded-full font-semibold hover:bg-gray-100 transition-all duration-300 inline-flex items-center"
                >
                  <Mic className="w-5 h-5 mr-2" />
                  Start Survey
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
                <button className="bg-white/20 text-white px-6 py-3 rounded-full font-semibold hover:bg-white/30 transition-all duration-300">
                  Learn More
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our AI-powered system uses advanced machine learning
              to find your ideal roommate match.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.2 }}
                viewport={{ once: true }}
                className="text-center p-6 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 hover:shadow-lg transition-all duration-300"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white mx-auto mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to Find Your Perfect Roommate?
            </h2>
            <p className="text-xl text-blue-100 mb-8">
              Join thousands of students who have found their ideal living situation
              through our AI-powered matching system.
            </p>
            <Link
              to="/survey"
              className="bg-white text-blue-600 px-8 py-4 rounded-full font-semibold text-lg hover:bg-gray-100 transition-all duration-300 inline-flex items-center"
            >
              <Mic className="w-6 h-6 mr-2" />
              Start Your Survey
              <ArrowRight className="w-6 h-6 ml-2" />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default HomePage; 