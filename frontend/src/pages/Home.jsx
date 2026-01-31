import React, { useState, useEffect } from 'react';

import {

  BrainCircuit,

  ArrowRight,

  Sparkles,

  Target,

  Globe,

  Menu,

  X,

  ChevronRight,

  Award,

  Zap,          

  ShieldCheck,  

  MousePointer2,

  Code2,

  Cpu,

  Building2

} from 'lucide-react';

import { Link } from 'react-router-dom';



const Home = () => {

  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const [scrolled, setScrolled] = useState(false);

  const [currentJobIndex, setCurrentJobIndex] = useState(0);

  

  const jobs = [

    { title: 'Senior Backend Engineer', company: 'Google', location: 'Mountain View', match: 98 },

    { title: 'Full Stack Developer', company: 'Microsoft', location: 'Seattle', match: 96 },

    { title: 'ML Engineer', company: 'OpenAI', location: 'San Francisco', match: 94 },

    { title: 'DevOps Architect', company: 'Amazon', location: 'Austin', match: 92 },

    { title: 'Frontend Lead', company: 'Meta', location: 'New York', match: 95 },

    { title: 'Data Scientist', company: 'Netflix', location: 'Los Gatos', match: 97 }

  ];



  useEffect(() => {

    const handleScroll = () => setScrolled(window.scrollY > 20);

    window.addEventListener('scroll', handleScroll);

    return () => window.removeEventListener('scroll', handleScroll);

  }, []);

  

  useEffect(() => {

    const interval = setInterval(() => {

      setCurrentJobIndex((prev) => (prev + 1) % jobs.length);

    }, 3000);

    return () => clearInterval(interval);

  }, []);



  return (

    <div className="relative min-h-screen bg-brand-bg font-sans text-brand-dark selection:bg-brand-accent/30 selection:text-brand-dark">

      {/* Navigation */}

      <nav className={`fixed top-0 w-full z-50 transition-all duration-500 ${scrolled ? 'bg-white/90 backdrop-blur-xl shadow-sm py-4' : 'bg-transparent py-8'}`}>

        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">

          <div className="flex items-center gap-2 group cursor-pointer">

            <div className="bg-brand-dark p-2 rounded-xl shadow-lg group-hover:scale-110 transition-transform duration-500">

              <BrainCircuit className="text-white w-6 h-6" />

            </div>

            <span className="text-2xl font-black tracking-tighter text-brand-dark uppercase">HireStorm</span>

          </div>



          <div className="hidden md:flex items-center gap-10 font-bold text-slate-500">

            <a href="#features" className="hover:text-brand-accent transition-colors text-xs uppercase tracking-widest">Features</a>

            <a href="#how-it-works" className="hover:text-brand-accent transition-colors text-xs uppercase tracking-widest">How it Works</a>

           

<Link to="/login">

  <button className="bg-brand-dark text-white px-8 py-3 rounded-full font-black hover:bg-brand-accent transition-all text-xs uppercase tracking-widest">

    Login

  </button>

</Link>

          </div>



          <button className="md:hidden p-2 text-brand-dark" onClick={() => setIsMenuOpen(!isMenuOpen)}>

            {isMenuOpen ? <X /> : <Menu />}

          </button>

        </div>



        {isMenuOpen && (

          <div className="absolute top-full left-0 w-full bg-white border-b border-slate-100 p-8 flex flex-col gap-6 md:hidden animate-in slide-in-from-top duration-500 shadow-2xl">

            <a href="#features" className="text-lg font-black uppercase tracking-tighter">Features</a>

            <a href="#how-it-works" className="text-lg font-black uppercase tracking-tighter">How it Works</a>

            <Link to="/login" onClick={() => setIsMenuOpen(false)}>

              <button className="bg-brand-dark text-white w-full py-5 rounded-2xl font-black uppercase">Login</button>

            </Link>

          </div>

        )}

      </nav>



      {/* Hero Section */}

      <header className="relative pt-44 pb-20 md:pt-60 md:pb-40 px-6 overflow-hidden">

        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-20 items-center">

          <div className="space-y-10 text-center lg:text-left">

            <div className="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm text-brand-accent px-5 py-2 rounded-full text-[10px] font-black border border-brand-accent/10 uppercase tracking-[0.2em] shadow-sm animate-bounce">

              <Sparkles size={14} /> Neural Engine v2.0

            </div>

           

            <h1 className="text-6xl md:text-[4.5rem] font-black tracking-tighter leading-[0.9] text-brand-dark">

              Your Skills. <span className="text-brand-accent animate-pulse">Perfect Match.</span> <br />

              <span className="bg-gradient-to-r from-brand-dark via-brand-accent to-brand-dark bg-clip-text text-transparent">No More Rejections.</span>

            </h1>

           

            <p className="text-xl md:text-2xl text-slate-500 max-w-xl mx-auto lg:mx-0 leading-relaxed font-medium italic opacity-80">

              <span className="text-brand-accent font-black">Neural Matching Engine</span> decodes your resume, maps skill graphs, and predicts culture-fit using <span className="text-brand-dark font-bold">semantic analysis & behavioral profiling.</span>

            </p>



            <div className="pt-4 space-y-10">

              <div className="relative w-full max-w-md h-[2px] bg-slate-200/50 rounded-full overflow-hidden mx-auto lg:mx-0">

                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-brand-accent to-transparent animate-shimmer" style={{ width: '40%', backgroundSize: '200% 100%' }}></div>

              </div>



              <div className="flex items-center justify-center lg:justify-start gap-6 group cursor-default">

                <div className="flex flex-col items-center gap-3">

                  <div className="w-[2px] h-14 rounded-full bg-slate-200 relative overflow-hidden">

                    <div className="absolute top-0 left-0 w-full h-1/2 bg-brand-accent animate-scroll-line"></div>

                  </div>

                </div>

                <div className="text-left">

                  <p className="text-[10px] font-black uppercase tracking-[0.4em] text-brand-dark opacity-30 group-hover:opacity-100 group-hover:text-brand-accent transition-all duration-700">

                    Intelligent Talent Mapping

                  </p>

                  <p className="text-sm font-bold text-slate-400 mt-1">Scroll to explore features</p>

                </div>

              </div>

            </div>

          </div>



          <div className="relative group perspective-1000">

            <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl shadow-[0_50px_100px_-20px_rgba(0,0,0,0.15)] border border-white p-6 md:p-12 transition-all duration-700 group-hover:scale-105 group-hover:shadow-2xl">

              <div className="flex items-center justify-between mb-6">

                <div className="flex items-center gap-3">

                  <div className="w-10 h-10 rounded-xl bg-brand-accent/10 flex items-center justify-center text-brand-accent shadow-inner animate-pulse">

                    <Target size={20} />

                  </div>

                  <div>

                    <h4 className="font-black text-xs text-brand-dark uppercase tracking-tighter">Live Matching</h4>

                    <p className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Real-Time Feed</p>

                  </div>

                </div>

                <div className="bg-green-500/20 text-green-600 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border border-green-500/30 animate-pulse">

                  <span className="inline-block w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5 animate-ping"></span>

                  Active

                </div>

              </div>



              <div className="bg-gradient-to-br from-brand-dark to-brand-dark/80 rounded-2xl p-5 text-white mb-5 min-h-[160px] flex flex-col justify-between relative overflow-hidden">

                <div className="absolute top-0 right-0 w-32 h-32 bg-brand-accent/10 rounded-full blur-3xl"></div>

                <div className="relative z-10">

                  <div className="flex gap-4 mb-4 items-start">

                    <div className="w-12 h-12 bg-white/10 backdrop-blur-md rounded-xl flex items-center justify-center shadow-lg border border-white/20">

                      <BrainCircuit className="text-brand-accent" size={24} />

                    </div>

                    <div className="flex-1 transition-all duration-500">

                      <h3 className="font-black text-xl tracking-tighter text-white mb-1 animate-fadeIn">

                        {jobs[currentJobIndex].title}

                      </h3>

                      <p className="text-[11px] font-bold text-brand-accent uppercase tracking-wider animate-fadeIn">

                        {jobs[currentJobIndex].company} • {jobs[currentJobIndex].location}

                      </p>

                    </div>

                  </div>

                  <div className="space-y-2">

                    <div className="flex justify-between items-center">

                      <span className="text-[10px] font-bold text-white/60 uppercase tracking-widest">Match Score</span>

                      <span className="text-lg font-black text-brand-accent">{jobs[currentJobIndex].match}%</span>

                    </div>

                    <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">

                      <div 

                        className="h-full bg-gradient-to-r from-brand-accent to-green-400 rounded-full shadow-lg transition-all duration-1000 ease-out"

                        style={{ width: `${jobs[currentJobIndex].match}%` }}

                      ></div>

                    </div>

                  </div>

                </div>

              </div>



              <div className="grid grid-cols-3 gap-3">

                <div className="p-3 bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border border-green-100 text-center">

                  <p className="text-[9px] font-black text-green-600 uppercase tracking-widest mb-1">Applied</p>

                  <p className="text-2xl font-black text-green-700">847</p>

                </div>

                <div className="p-3 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border border-blue-100 text-center">

                  <p className="text-[9px] font-black text-blue-600 uppercase tracking-widest mb-1">Matched</p>

                  <p className="text-2xl font-black text-blue-700">156</p>

                </div>

                <div className="p-3 bg-gradient-to-br from-orange-50 to-amber-50 rounded-2xl border border-orange-100 text-center">

                  <p className="text-[9px] font-black text-orange-600 uppercase tracking-widest mb-1">Offers</p>

                  <p className="text-2xl font-black text-orange-700">23</p>

                </div>

              </div>

            </div>

          </div>

        </div>

      </header>



      {/* Companies Providing Jobs - Real-time Feed */}

      <section className="py-16 border-y border-slate-100 bg-white/30 backdrop-blur-sm overflow-hidden">

        <div className="max-w-7xl mx-auto px-6">

          <p className="text-center text-2xl font-black uppercase tracking-tight text-brand-dark mb-10">

            <span className="text-brand-accent">Live Jobs & Internships</span> from 500+ Companies

          </p>

          <div className="relative">

            <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-white/30 to-transparent z-10"></div>

            <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-white/30 to-transparent z-10"></div>

            

            <div className="flex gap-16 animate-scroll-companies">

              {[

                'Google', 'Microsoft', 'Amazon', 'Meta', 'Apple', 'Netflix', 'Tesla', 'Adobe',

                'Salesforce', 'Oracle', 'IBM', 'Intel', 'Cisco', 'PayPal', 'Uber', 'Airbnb',

                'Spotify', 'Twitter', 'LinkedIn', 'Stripe', 'Shopify', 'Snapchat', 'Zoom', 'Slack',

                'Dropbox', 'GitHub', 'Atlassian', 'ServiceNow', 'Workday', 'Square', 'Pinterest', 'Reddit',

                'Google', 'Microsoft', 'Amazon', 'Meta', 'Apple', 'Netflix', 'Tesla', 'Adobe'

              ].map((company, index) => (

                <div 

                  key={index} 

                  className="flex-shrink-0 bg-white/80 backdrop-blur-sm rounded-2xl px-6 py-4 border border-slate-200/50 shadow-sm hover:shadow-lg hover:border-brand-accent/30 transition-all duration-300 group"

                >

                  <div className="flex items-center gap-4 min-w-[180px]">

                    <div className="w-12 h-12 bg-gradient-to-br from-slate-100 to-white rounded-xl flex items-center justify-center shadow-md border border-slate-200/50 group-hover:scale-110 transition-transform">

                      <Building2 className="text-brand-dark w-6 h-6" />

                    </div>

                    <div className="flex-1">

                      <p className="text-sm font-black tracking-tight text-brand-dark mb-1">

                        {company}

                      </p>

                      <div className="flex items-center gap-2">

                        <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>

                        <span className="text-[10px] font-bold text-green-600 uppercase tracking-wider">

                          {Math.floor(Math.random() * 50) + 10} Jobs

                        </span>

                      </div>

                    </div>

                  </div>

                </div>

              ))}

            </div>

          </div>

        </div>

      </section>



      {/* Features Grid */}

      <section id="features" className="py-32 px-6 relative">

        <div className="max-w-7xl mx-auto">

          <div className="text-center max-w-3xl mx-auto mb-24 space-y-4">

            <h2 className="text-5xl font-black tracking-tighter text-brand-dark uppercase">Revolutionizing Talent.</h2>

            <p className="text-lg text-slate-500 font-medium italic">We scan code, not just keywords.</p>

          </div>



          <div className="grid md:grid-cols-3 gap-12">

            <FeatureCard

              icon={<BrainCircuit size={32} />}

              title="Data Parsing"

              description="Our engine analyzes project complexity and repo architecture."

            />

            <FeatureCard

              icon={<Zap size={32} className="text-brand-accent" />}

              title="Instant Intake"

              description="Direct matchmaking with technical founders within 24 hours."

            />

            <FeatureCard

              icon={<ShieldCheck size={32} />}

              title="Identity Guard"

              description="Full anonymity until both sides signal high interest."

            />

          </div>

        </div>

      </section>



      {/* HOW IT WORKS SECTION - Naya code yahan add kiya hai */}

      <section id="how-it-works" className="py-32 px-6 bg-brand-dark text-white rounded-[4rem] mx-4 overflow-hidden relative">

        <div className="max-w-7xl mx-auto">

          <div className="grid lg:grid-cols-2 gap-20 items-center">

            <div className="space-y-12">

              <h2 className="text-5xl font-black tracking-tighter uppercase text-brand-accent">How it Works</h2>

              <div className="space-y-16">

                <Step

                  num="01"

                  title="Upload Resume & Job Context"

                  desc="Instantly upload your CV and any target job description. Our system parses technical stacks and experience markers to understand your unique value proposition."

                />

                <Step

                  num="02"

                  title="AI Matching Engine"

                  desc="Our neural 'AI Machine' cross-references your profile against role requirements, simulating team resonance and project alignment to find hidden synergies."

                />

                <Step

                  num="03"

                  title="Career Intelligence & Action"

                  desc="Receive a strategic roadmap with verified compatibility reports. Move beyond 'applying' and start executing with direct access to decision-makers."

                />

              </div>

            </div>

            <div className="hidden lg:grid grid-cols-2 gap-6 relative z-10">

              {[{ label: 'Active Talent', val: '45k+' }, { label: 'Match %', val: '92%' }, { label: 'Orgs', val: '850+' }, { label: 'Time', val: '14d' }].map((stat, i) => (

                <div key={i} className="bg-white/5 backdrop-blur-md p-10 rounded-[3rem] border border-white/10 text-center hover:bg-white/10 transition-colors">

                  <p className="text-brand-accent font-black text-xs uppercase tracking-widest mb-3">{stat.label}</p>

                  <p className="text-5xl font-black">{stat.val}</p>

                </div>

              ))}

            </div>

          </div>

        </div>

      </section>



      {/* CTA Section */}

      <section className="py-32 px-6">

        <div className="max-w-6xl mx-auto bg-brand-dark rounded-[4rem] p-16 md:p-24 text-center text-white relative shadow-[0_50px_100px_rgba(0,0,0,0.3)] overflow-hidden border border-white/5">

          <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[50%] bg-brand-accent/10 rounded-full blur-[120px]"></div>

          <h2 className="text-5xl md:text-7xl font-black mb-8 tracking-tighter uppercase leading-none">Ready to Enter?</h2>

          <p className="text-slate-400 text-lg mb-14 max-w-xl mx-auto font-medium">Join the ecosystem where potential meets reality.</p>

          <Link to="/dashboard">

            <button className="bg-brand-accent text-brand-dark px-14 py-6 rounded-full font-black text-2xl hover:scale-105 transition-all shadow-2xl active:scale-95 uppercase tracking-tighter shadow-brand-accent/20">

              Launch Profile <ChevronRight className="inline-block ml-1" />

            </button>

          </Link>

        </div>

      </section>



      {/* Footer */}

      <footer className="bg-brand-bg pt-24 pb-12 border-t border-slate-200">

        <div className="max-w-7xl mx-auto px-6">

          <div className="flex items-center gap-3 mb-10">

            <div className="bg-brand-dark p-2 rounded-xl text-white">

              <BrainCircuit size={24} />

            </div>

            <span className="text-2xl font-black uppercase tracking-tighter">HireStorm</span>

          </div>

          <div className="pt-10 border-t border-slate-200 flex flex-col md:flex-row justify-between items-center gap-6 text-slate-400 font-bold text-[10px] uppercase tracking-[0.3em]">

            <p>© 2026 HireStorm AI • Future of talent</p>

            <p className="flex items-center gap-2">Built for high potential <Sparkles size={12} className="text-brand-accent" /></p>

          </div>

        </div>

      </footer>

    </div>

  );

};



const FeatureCard = ({ icon, title, description }) => (

  <div className="p-12 rounded-[4rem] bg-white/60 backdrop-blur-md border border-white hover:border-brand-accent transition-all duration-700 group shadow-sm hover:shadow-2xl hover:bg-white flex flex-col items-center text-center">

    <div className="mb-10 p-7 rounded-3xl bg-brand-bg text-brand-dark group-hover:scale-110 group-hover:bg-brand-dark group-hover:text-white transition-all duration-500 shadow-inner">

      {icon}

    </div>

    <h3 className="text-3xl font-black mb-6 text-brand-dark tracking-tighter uppercase">{title}</h3>

    <p className="text-slate-500 leading-relaxed font-medium">{description}</p>

  </div>

);



const Step = ({ num, title, desc }) => (

  <div className="flex gap-8 group">

    <div className="text-7xl font-black text-brand-accent/10 group-hover:text-brand-accent transition-all duration-700 leading-none">{num}</div>

    <div className="pt-2">

      <h4 className="text-2xl font-black text-white tracking-tight uppercase mb-2">{title}</h4>

      <p className="text-slate-400 leading-relaxed font-medium text-sm italic">{desc}</p>

    </div>

  </div>

);



export default Home;