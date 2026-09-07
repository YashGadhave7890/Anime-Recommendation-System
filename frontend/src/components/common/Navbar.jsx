import React, { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import {
  Compass,
  Sparkles,
  Bookmark,
  User,
  Menu,
  X,
  ChevronDown,
  Layers,
  Search,
} from 'lucide-react';
import { useUser } from '../../context/UserContext';
import SearchBar from './SearchBar';

export default function Navbar() {
  const { currentUser, userId, switchUser, demoUsers, watchlist } = useUser();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);
  const navigate = useNavigate();

  const navLinks = [
    { name: 'Home', to: '/', icon: Layers },
    { name: 'Discover', to: '/discover', icon: Compass },
    { name: 'Recommendations', to: '/recommendations', icon: Sparkles, badge: 'ML' },
    { name: 'Watchlist', to: '/watchlist', icon: Bookmark, count: watchlist.length },
    { name: 'Profile', to: '/profile', icon: User },
  ];

  const handleSelectUser = (id) => {
    switchUser(id);
    setUserDropdownOpen(false);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-white/5 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20 gap-4">
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-3 shrink-0 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-violet-500 p-0.5 shadow-glow-sm group-hover:shadow-glow-md transition-all">
              <div className="w-full h-full bg-dark-900 rounded-[10px] flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-brand-400 group-hover:rotate-12 transition-transform duration-300" />
              </div>
            </div>
            <div>
              <span className="text-xl font-extrabold tracking-tight text-white font-sans bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
                ANIMORA
              </span>
              <span className="hidden lg:block text-[10px] uppercase font-semibold tracking-widest text-brand-400/90 -mt-1">
                AI Discovery
              </span>
            </div>
          </Link>

          {/* Desktop Search Bar */}
          <div className="hidden md:block flex-1 max-w-md mx-4">
            <SearchBar placeholder="Search 17,500+ anime titles..." />
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `relative flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-brand-500/15 text-brand-300 font-semibold shadow-sm'
                        : 'text-slate-300 hover:text-white hover:bg-white/5'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{link.name}</span>
                  {link.badge && (
                    <span className="px-1.5 py-0.2 rounded-md bg-gradient-to-r from-brand-500 to-violet-500 text-[10px] font-bold text-white uppercase tracking-wider">
                      {link.badge}
                    </span>
                  )}
                  {typeof link.count === 'number' && link.count > 0 && (
                    <span className="px-1.5 py-0.2 rounded-full bg-slate-800 text-[10px] font-semibold text-slate-300">
                      {link.count}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>

          {/* Demo User Switcher & Mobile Actions */}
          <div className="flex items-center gap-2">
            {/* Mobile Search Toggle */}
            <button
              onClick={() => setMobileSearchOpen(!mobileSearchOpen)}
              className="md:hidden p-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/10 transition"
              aria-label="Toggle search"
            >
              <Search className="w-5 h-5" />
            </button>

            {/* User Switcher Dropdown (Desktop & Mobile) */}
            <div className="relative">
              <button
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="flex items-center gap-2 p-1.5 pr-3 rounded-2xl bg-dark-900 border border-slate-700/80 hover:border-slate-600 text-slate-200 transition"
                aria-label="User profile switcher"
              >
                <img
                  src={currentUser.avatar}
                  alt={currentUser.displayName}
                  className="w-7 h-7 rounded-xl object-cover border border-brand-500/40"
                />
                <span className="hidden xl:inline text-xs font-medium max-w-[100px] truncate text-slate-300">
                  {currentUser.displayName.split(' ')[0]}
                </span>
                <span
                  className={`hidden sm:inline-block w-2 h-2 rounded-full ${
                    currentUser.isColdStart ? 'bg-amber-400' : 'bg-emerald-400'
                  }`}
                  title={currentUser.isColdStart ? 'Cold-Start Profile' : 'Trained Profile'}
                />
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {userDropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 rounded-2xl bg-dark-900/95 border border-slate-700/80 shadow-2xl backdrop-blur-xl p-2 z-50 animate-fade-in">
                  <div className="px-3 py-2 border-b border-slate-800/80 mb-1">
                    <div className="text-xs font-semibold text-slate-300">Switch Demo Persona</div>
                    <div className="text-[11px] text-slate-400">
                      Test personalized vs cold-start ML recs
                    </div>
                  </div>

                  <div className="space-y-1">
                    {demoUsers.map((u) => (
                      <button
                        key={u.id}
                        onClick={() => handleSelectUser(u.id)}
                        className={`w-full flex items-start gap-2.5 p-2 rounded-xl text-left transition ${
                          u.id === userId
                            ? 'bg-brand-500/15 border border-brand-500/30 text-white'
                            : 'hover:bg-white/5 text-slate-300'
                        }`}
                      >
                        <img
                          src={u.avatar}
                          alt={u.displayName}
                          className="w-8 h-8 rounded-lg object-cover mt-0.5 shrink-0"
                        />
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-1.5">
                            <span className="text-xs font-semibold">{u.displayName}</span>
                            <span
                              className={`text-[9px] px-1 py-0.2 rounded font-bold uppercase ${
                                u.isColdStart
                                  ? 'bg-amber-500/20 text-amber-300'
                                  : 'bg-emerald-500/20 text-emerald-300'
                              }`}
                            >
                              {u.isColdStart ? 'Cold Start' : 'Trained'}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                            {u.description}
                          </p>
                        </div>
                      </button>
                    ))}
                  </div>

                  <div className="mt-1 pt-1 border-t border-slate-800/80">
                    <Link
                      to="/profile"
                      onClick={() => setUserDropdownOpen(false)}
                      className="block text-center py-1.5 text-xs text-brand-400 hover:text-brand-300 font-medium"
                    >
                      Manage Profile & Preferences →
                    </Link>
                  </div>
                </div>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/10 transition"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Search Bar Drawer */}
        {mobileSearchOpen && (
          <div className="md:hidden pb-4 pt-1">
            <SearchBar
              placeholder="Search 17,500+ anime titles..."
              onSearch={() => setMobileSearchOpen(false)}
            />
          </div>
        )}

        {/* Mobile Dropdown Nav Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-800/80 space-y-1 animate-fade-in">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition ${
                      isActive
                        ? 'bg-brand-500/15 text-brand-300 font-semibold'
                        : 'text-slate-300 hover:bg-white/5 hover:text-white'
                    }`
                  }
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4" />
                    <span>{link.name}</span>
                  </div>
                  {link.badge && (
                    <span className="px-1.5 py-0.5 rounded-md bg-brand-500 text-[10px] font-bold text-white">
                      {link.badge}
                    </span>
                  )}
                  {typeof link.count === 'number' && link.count > 0 && (
                    <span className="px-2 py-0.5 rounded-full bg-slate-800 text-xs font-semibold text-slate-300">
                      {link.count}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </div>
        )}
      </div>
    </header>
  );
}
