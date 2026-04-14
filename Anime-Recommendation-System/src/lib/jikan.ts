/**
 * Fetch anime poster using Jikan API (MyAnimeList)
 * Includes a request queue and retry logic to handle rate limiting (429 errors).
 */

// Simple request queue to respect Jikan's rate limit (3 requests per second)
let requestQueue: Promise<any> = Promise.resolve();
const MIN_DELAY = 400; // 400ms between requests to be safe

async function queueRequest<T>(requestFn: () => Promise<T>): Promise<T> {
  const result = requestQueue.then(async () => {
    await new Promise(resolve => setTimeout(resolve, MIN_DELAY));
    return requestFn();
  });
  requestQueue = result.catch(() => {}); // Continue queue even if one fails
  return result;
}

export async function getAnimePoster(name: string, retries = 2): Promise<string> {
  // Sanitize name for better search results (remove some special characters)
  const sanitizedName = name
    .replace(/[;°!!.]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  try {
    return await queueRequest(async () => {
      const response = await fetch(`https://api.jikan.moe/v4/anime?q=${encodeURIComponent(sanitizedName)}&limit=1`);
      
      if (response.status === 429) {
        if (retries > 0) {
          console.warn(`Rate limited for ${name}, retrying...`);
          await new Promise(resolve => setTimeout(resolve, 1000 * (3 - retries)));
          return getAnimePoster(name, retries - 1);
        }
        throw new Error('Jikan API rate limit exceeded');
      }

      if (!response.ok) throw new Error(`Jikan API error: ${response.status}`);
      
      const data = await response.json();
      if (data.data && data.data.length > 0) {
        return data.data[0].images.webp.large_image_url || data.data[0].images.jpg.large_image_url;
      }
      throw new Error('No poster found');
    });
  } catch (error) {
    console.error(`Failed to fetch poster for ${name}:`, error);
    // Fallback to a high-quality placeholder
    return `https://picsum.photos/seed/${encodeURIComponent(name)}/400/600`;
  }
}
