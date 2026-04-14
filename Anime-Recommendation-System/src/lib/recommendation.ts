import Papa from 'papaparse';

export interface Anime {
  anime_id: number;
  name: string;
  genre: string;
  type: string;
  episodes: string | number;
  rating: number;
  members: number;
}

export async function loadAnimeData(): Promise<Anime[]> {
  try {
    const response = await fetch('/data/anime.csv');
    const csvText = await response.text();
    const result = Papa.parse<Anime>(csvText, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
    });
    return result.data;
  } catch (error) {
    console.error('Error loading anime data:', error);
    return [];
  }
}

export function getRecommendations(
  favorites: string[],
  allAnime: Anime[],
  filterType: string = 'All'
): Anime[] {
  if (favorites.length === 0) return [];

  // 1. Clean and prepare data
  const filteredAnime = allAnime.filter(a => a.name && a.genre);
  
  // 2. Extract all genres
  const allGenres = Array.from(new Set(filteredAnime.flatMap(a => a.genre.split(', ').map(g => g.trim()))));
  
  // 3. Compute IDF
  const idf: Record<string, number> = {};
  const N = filteredAnime.length;
  allGenres.forEach(genre => {
    const count = filteredAnime.filter(a => a.genre.includes(genre)).length;
    idf[genre] = Math.log(N / (count || 1));
  });

  // 4. Vectorize each anime
  const vectors = filteredAnime.map(anime => {
    const genres = anime.genre.split(', ').map(g => g.trim());
    const vector: Record<string, number> = {};
    genres.forEach(g => {
      vector[g] = idf[g];
    });
    return { anime, vector };
  });

  // 5. Get favorite vectors
  const favoriteAnimes = favorites.map(fav => 
    filteredAnime.find(a => a.name.toLowerCase() === fav.toLowerCase())
  ).filter(Boolean) as Anime[];

  if (favoriteAnimes.length === 0) return [];

  // Combine favorite vectors into one "user profile" vector
  const userVector: Record<string, number> = {};
  favoriteAnimes.forEach(anime => {
    const genres = anime.genre.split(', ').map(g => g.trim());
    genres.forEach(g => {
      userVector[g] = (userVector[g] || 0) + idf[g];
    });
  });

  // 6. Compute Similarity
  const similarities = vectors.map(({ anime, vector }) => {
    // Skip if it's already in favorites
    if (favorites.some(fav => fav.toLowerCase() === anime.name.toLowerCase())) {
      return { anime, score: -1 };
    }

    // Filter by type if not 'All'
    if (filterType !== 'All' && anime.type !== filterType) {
      return { anime, score: -1 };
    }

    let dotProduct = 0;
    let userMag = 0;
    let animeMag = 0;

    allGenres.forEach(g => {
      const u = userVector[g] || 0;
      const a = vector[g] || 0;
      dotProduct += u * a;
      userMag += u * u;
      animeMag += a * a;
    });

    const cosineSim = dotProduct / (Math.sqrt(userMag) * Math.sqrt(animeMag) || 1);
    
    // Rank based on similarity + rating (normalized)
    const finalScore = (cosineSim * 0.8) + ((anime.rating / 10) * 0.2);

    return { anime, score: finalScore };
  });

  // 7. Sort and return top 10
  return similarities
    .sort((a, b) => b.score - a.score)
    .filter(s => s.score > 0)
    .slice(0, 12)
    .map(s => s.anime);
}
