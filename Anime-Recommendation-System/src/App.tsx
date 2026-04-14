/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Search, X, Star, Loader2, Play, TrendingUp, Sparkles, ChevronRight } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { loadAnimeData, getRecommendations, Anime } from '@/lib/recommendation';
import { getAnimePoster } from '@/lib/jikan';

export default function App() {
  const [allAnime, setAllAnime] = useState<Anime[]>([]);
  const [favorites, setFavorites] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [recommendations, setRecommendations] = useState<Anime[]>([]);
  const [posters, setPosters] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [filterType, setFilterType] = useState('All');
  const [isDataLoaded, setIsDataLoaded] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Load data
  useEffect(() => {
    loadAnimeData().then(data => {
      setAllAnime(data);
      setIsDataLoaded(true);
    });
  }, []);

  // Trending anime (top rated from dataset)
  const trendingAnime = useMemo(() => {
    return [...allAnime]
      .sort((a, b) => b.rating - a.rating)
      .slice(0, 8);
  }, [allAnime]);

  // Fetch posters for trending
  useEffect(() => {
    if (trendingAnime.length > 0) {
      trendingAnime.forEach(async (anime) => {
        if (!posters[anime.name]) {
          const poster = await getAnimePoster(anime.name);
          setPosters(prev => ({ ...prev, [anime.name]: poster }));
        }
      });
    }
  }, [trendingAnime]);

  // Update recommendations when favorites or filter changes
  useEffect(() => {
    if (favorites.length > 0) {
      setIsLoading(true);
      const timer = setTimeout(() => {
        const recs = getRecommendations(favorites, allAnime, filterType);
        setRecommendations(recs);
        
        recs.forEach(async (anime) => {
          if (!posters[anime.name]) {
            const poster = await getAnimePoster(anime.name);
            setPosters(prev => ({ ...prev, [anime.name]: poster }));
          }
        });
        
        setIsLoading(false);
      }, 600);
      return () => clearTimeout(timer);
    } else {
      setRecommendations([]);
    }
  }, [favorites, filterType, allAnime]);

  const handleAddFavorite = (name: string) => {
    if (!favorites.includes(name)) {
      setFavorites([...favorites, name]);
    }
    setSearchQuery('');
    searchInputRef.current?.focus();
  };

  const handleRemoveFavorite = (name: string) => {
    setFavorites(favorites.filter(f => f !== name));
  };

  const filteredSuggestions = useMemo(() => {
    if (!searchQuery || searchQuery.length < 2) return [];
    return allAnime
      .filter(a => a.name.toLowerCase().includes(searchQuery.toLowerCase()))
      .filter(a => !favorites.includes(a.name))
      .slice(0, 6);
  }, [searchQuery, allAnime, favorites]);

  if (!isDataLoaded) {
    return (
      <div className="h-screen flex items-center justify-center bg-background">
        <motion.div
          animate={{ scale: [1, 1.1, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          <Loader2 className="text-primary" size={64} />
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background selection:bg-primary/30">
      <div className="max-w-7xl mx-auto px-6 py-16 space-y-24">
        
        {/* Header */}
        <header className="text-center space-y-6 relative">
          <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-96 h-96 bg-primary/10 blur-[120px] rounded-full -z-10" />
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs font-bold tracking-[0.2em] text-primary uppercase mb-4"
          >
            <Sparkles size={14} /> Next-Gen Recommender
          </motion.div>
          <motion.h1 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-6xl md:text-9xl font-black tracking-tighter red-glow text-white leading-none"
          >
            🎌 ANIME REC
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-muted-foreground text-xl font-medium tracking-wide max-w-xl mx-auto"
          >
            The ultimate discovery engine for your next binge-watch.
          </motion.p>
        </header>

        {/* Search Section (Tag-Style) */}
        <section className="max-w-3xl mx-auto space-y-8">
          <div className="space-y-4">
            <div className="search-container group">
              <Search className="ml-2 text-muted-foreground group-focus-within:text-primary transition-colors" size={22} />
              
              <div className="flex flex-wrap gap-2 flex-1">
                <AnimatePresence>
                  {favorites.map(fav => (
                    <motion.div
                      key={fav}
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      exit={{ scale: 0.8, opacity: 0 }}
                    >
                      <Badge 
                        variant="secondary" 
                        className="pl-3 pr-1 py-1.5 text-sm gap-1.5 border border-white/10 bg-white/5 hover:bg-white/10 text-white transition-all group/badge"
                      >
                        {fav}
                        <button 
                          onClick={() => handleRemoveFavorite(fav)}
                          className="hover:bg-primary/20 rounded-full p-0.5 transition-colors text-muted-foreground group-hover/badge:text-primary"
                        >
                          <X size={14} />
                        </button>
                      </Badge>
                    </motion.div>
                  ))}
                </AnimatePresence>
                
                <Input 
                  ref={searchInputRef}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={favorites.length === 0 ? "Search and add your favorite anime..." : "Add more..."}
                  className="flex-1 min-w-[200px] border-none bg-transparent focus-visible:ring-0 text-lg h-10 placeholder:text-muted-foreground/40"
                />
              </div>
            </div>
            
            {/* Autocomplete Suggestions */}
            <AnimatePresence>
              {filteredSuggestions.length > 0 && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="absolute left-0 right-0 mt-2 bg-secondary/95 backdrop-blur-3xl border border-white/10 rounded-2xl overflow-hidden z-50 shadow-2xl max-w-3xl mx-auto"
                >
                  <div className="p-2 border-b border-white/5 bg-white/5">
                    <span className="text-[10px] uppercase tracking-widest font-bold text-muted-foreground/60 px-3">Suggestions</span>
                  </div>
                  {filteredSuggestions.map(anime => (
                    <button
                      key={anime.anime_id}
                      onClick={() => handleAddFavorite(anime.name)}
                      className="w-full text-left px-4 py-4 hover:bg-primary/10 transition-all flex items-center justify-between group"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-14 rounded-md bg-white/5 overflow-hidden">
                          {posters[anime.name] && <img src={posters[anime.name]} className="w-full h-full object-cover" />}
                        </div>
                        <div>
                          <span className="font-bold text-white block group-hover:text-primary transition-colors">{anime.name}</span>
                          <span className="text-xs text-muted-foreground">{anime.genre.split(',')[0]}</span>
                        </div>
                      </div>
                      <Badge variant="outline" className="opacity-0 group-hover:opacity-100 transition-all border-primary/30 text-primary translate-x-2 group-hover:translate-x-0">Add Favorite</Badge>
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </section>

        <Separator className="bg-white/5" />

        {/* Trending Section */}
        <section className="space-y-8">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-black tracking-tight text-white flex items-center gap-3">
              <TrendingUp className="text-primary" size={28} />
              Trending Now
            </h2>
            <Button variant="ghost" className="text-muted-foreground hover:text-white gap-2 group">
              View All <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>
          
          {trendingAnime.length > 0 ? (
            <div className="flex gap-6 overflow-x-auto pb-8 trending-scroll -mx-6 px-6">
              {trendingAnime.map((anime, idx) => (
                <motion.div
                  key={anime.anime_id}
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="flex-shrink-0 w-48 group cursor-pointer"
                >
                  <div className="relative aspect-[2/3] rounded-2xl overflow-hidden mb-4 border border-white/5 group-hover:border-primary/30 transition-all duration-500">
                    {posters[anime.name] ? (
                      <img 
                        src={posters[anime.name]} 
                        className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" 
                        referrerPolicy="no-referrer"
                      />
                    ) : (
                      <Skeleton className="w-full h-full" />
                    )}
                    <div className="absolute top-3 left-3">
                      <Badge className="bg-black/60 backdrop-blur-md border border-white/10 text-yellow-500 font-black gap-1">
                        <Star size={12} fill="currentColor" /> {anime.rating}
                      </Badge>
                    </div>
                  </div>
                  <h3 className="font-bold text-sm text-white line-clamp-1 group-hover:text-primary transition-colors">{anime.name}</h3>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-widest mt-1">{anime.type}</p>
                </motion.div>
              ))}
            </div>
          ) : (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="py-16 text-center bg-white/5 rounded-3xl border border-dashed border-white/10 space-y-3"
            >
              <TrendingUp className="mx-auto text-muted-foreground/20" size={40} />
              <p className="text-muted-foreground font-medium">No trending anime available at the moment.</p>
            </motion.div>
          )}
        </section>

        {/* Recommendations Section */}
        <ErrorBoundary>
          <section className="space-y-12">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-white/5 pb-8">
              <div className="space-y-1">
                <h2 className="text-3xl font-black tracking-tight text-white flex items-center gap-3">
                  <span className="w-1.5 h-10 bg-primary rounded-full" />
                  {favorites.length > 0 ? 'Picked For You' : 'Your Recommendations'}
                </h2>
                <p className="text-muted-foreground font-medium">Based on your unique taste profile</p>
              </div>
              
              <div className="flex items-center gap-2 p-1.5 bg-white/5 rounded-full border border-white/10">
                {['All', 'TV', 'Movie', 'OVA'].map(type => (
                  <button
                    key={type}
                    onClick={() => setFilterType(type)}
                    className={`px-6 py-2 rounded-full text-xs font-black uppercase tracking-widest transition-all duration-300 ${
                      filterType === type 
                        ? 'bg-primary text-white shadow-lg shadow-primary/20' 
                        : 'text-muted-foreground hover:text-white hover:bg-white/5'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            {isLoading ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
                {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
                  <div key={i} className="space-y-4">
                    <Skeleton className="aspect-[2/3] rounded-2xl" />
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
                <AnimatePresence mode="popLayout">
                  {recommendations.map((anime, index) => (
                    <motion.div
                      key={anime.anime_id}
                      layout
                      initial={{ opacity: 0, scale: 0.9, y: 20 }}
                      animate={{ opacity: 1, scale: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      transition={{ duration: 0.4, delay: index * 0.05 }}
                    >
                      <Card className="glass-card group h-full flex flex-col">
                        <div className="relative aspect-[2/3] overflow-hidden">
                          {posters[anime.name] ? (
                            <img 
                              src={posters[anime.name]} 
                              alt={anime.name}
                              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                              referrerPolicy="no-referrer"
                            />
                          ) : (
                            <Skeleton className="w-full h-full" />
                          )}
                          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500 flex flex-col justify-end p-6">
                            <Button className="w-full bg-primary hover:bg-primary/90 text-white font-black gap-2 shadow-2xl translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                              <Play size={18} fill="currentColor" /> Watch Now
                            </Button>
                          </div>
                        </div>
                        <CardContent className="p-6 space-y-4 flex-grow flex flex-col justify-between">
                          <div className="space-y-1">
                            <h3 className="font-black text-lg text-white line-clamp-1 group-hover:text-primary transition-colors duration-300">{anime.name}</h3>
                            <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest">{anime.genre.split(',')[0]}</p>
                          </div>
                          <div className="flex items-center justify-between pt-4 border-t border-white/5">
                            <div className="flex items-center gap-1.5 text-yellow-500 font-black text-sm">
                              <Star size={16} fill="currentColor" />
                              <span>{anime.rating}</span>
                            </div>
                            <Badge variant="outline" className="text-[9px] uppercase tracking-[0.2em] font-black border-white/10 text-muted-foreground/60 px-2 py-0.5">
                              {anime.type}
                            </Badge>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            )}

            {favorites.length > 0 && recommendations.length === 0 && !isLoading && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-40 space-y-6 bg-white/5 rounded-3xl border border-dashed border-white/10"
              >
                <div className="inline-flex p-8 rounded-full bg-white/5 border border-white/10">
                  <Search className="text-muted-foreground/20" size={48} />
                </div>
                <div className="space-y-2">
                  <p className="text-white font-bold text-xl">No matches found</p>
                  <p className="text-muted-foreground max-w-xs mx-auto">Try adjusting your filters or adding more diverse favorites.</p>
                </div>
                <Button variant="outline" onClick={() => setFilterType('All')} className="rounded-full border-white/10 hover:bg-white/5">Clear Filters</Button>
              </motion.div>
            )}

            {favorites.length === 0 && (
              <div className="text-center py-40 space-y-6 bg-white/5 rounded-3xl border border-dashed border-white/10">
                <div className="inline-flex p-8 rounded-full bg-white/5 border border-white/10">
                  <Sparkles className="text-primary/40" size={48} />
                </div>
                <div className="space-y-2">
                  <p className="text-white font-bold text-xl">Your journey begins here</p>
                  <p className="text-muted-foreground max-w-xs mx-auto">Add at least one anime to see personalized recommendations.</p>
                </div>
              </div>
            )}
          </section>
        </ErrorBoundary>

        {/* Footer */}
        <footer className="pt-32 pb-12 text-center space-y-8">
          <Separator className="bg-white/5 mb-12" />
          <div className="flex justify-center gap-8 text-muted-foreground/30">
            {['TF-IDF Engine', 'Jikan API', 'Framer Motion', 'Tailwind 4'].map(tag => (
              <span key={tag} className="text-[10px] uppercase tracking-[0.4em] font-black">{tag}</span>
            ))}
          </div>
          <div className="space-y-2">
            <p className="text-sm font-bold text-white/40">🎌 ANIME RECOMMENDER</p>
            <p className="text-[10px] text-muted-foreground/20 uppercase tracking-[0.2em]">
              Crafted for the ultimate Otaku experience • 2026
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
