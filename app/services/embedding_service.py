import numpy as np
import hashlib
import logging
from typing import List

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, settings):
        self.settings = settings
        self.model = settings.GOOGLE_EMBEDDING_MODEL
        self.api_key = settings.GOOGLE_API_KEY
        # default embedding dimension; may be updated from provider responses
        self.dim = getattr(settings, 'EMBEDDING_DIM', 1536)
        # batch size for embedding API calls (can be configured in settings)
        self.batch_size = getattr(settings, 'EMBEDDING_BATCH_SIZE', 16)
        # lazy import of google client
        try:
            from google import genai
            self.genai = genai
        except Exception:
            self.genai = None

    def _local_embedding(self, text: str) -> np.ndarray:
        # deterministic pseudo-embedding based on hash
        h = hashlib.md5(text.encode('utf-8')).hexdigest()
        seed = int(h[:8], 16)
        rnd = np.random.RandomState(seed)
        vec = rnd.normal(size=(self.dim,))
        # normalize
        vec = vec / np.linalg.norm(vec)
        return vec

    def _extract_embedding(self, response):
        if hasattr(response, 'data') and response.data:
            first = response.data[0]
            if hasattr(first, 'values') and first.values is not None:
                return first.values
            if hasattr(first, 'embedding'):
                return first.embedding
            if isinstance(first, dict):
                return first.get('values') or first.get('embedding')
        if hasattr(response, 'embeddings') and response.embeddings:
            first = response.embeddings[0]
            if hasattr(first, 'values') and first.values is not None:
                return first.values
            if hasattr(first, 'embedding'):
                return first.embedding
            if isinstance(first, dict):
                return first.get('values') or first.get('embedding')
        if isinstance(response, dict):
            data = response.get('data') or response.get('embeddings')
            if data:
                first = data[0]
                if isinstance(first, dict):
                    return first.get('values') or first.get('embedding')
        raise ValueError('Unable to extract embedding from Google response')

    def _extract_embeddings(self, response):
        # Return a list of embedding vectors extracted from a batch response
        items = None
        if hasattr(response, 'data') and response.data:
            items = response.data
        elif hasattr(response, 'embeddings') and response.embeddings:
            items = response.embeddings
        elif isinstance(response, dict):
            items = response.get('data') or response.get('embeddings')

        if not items:
            raise ValueError('No embedding items found in response')

        results = []
        for first in items:
            if hasattr(first, 'values') and first.values is not None:
                results.append(first.values)
                continue
            if hasattr(first, 'embedding'):
                results.append(first.embedding)
                continue
            if isinstance(first, dict):
                results.append(first.get('values') or first.get('embedding'))
                continue
            raise ValueError('Unable to extract an embedding entry from item')

        return results

    def embed_text(self, text: str) -> np.ndarray:
        if self.api_key and self.genai:
            try:
                client = self.genai.Client(api_key=self.api_key)
                if hasattr(client, 'models') and hasattr(client.models, 'embed_content'):
                    resp = client.models.embed_content(model=self.model, contents=[text])
                elif hasattr(client, 'embeddings'):
                    resp = client.embeddings.create(model=self.model, input=[text])
                else:
                    raise AttributeError('Google GenAI client has no embeddings interface')
                emb_vector = self._extract_embedding(resp)
                emb = np.array(emb_vector, dtype=float)
                # update dimension from provider if it differs
                try:
                    self.dim = int(emb.shape[0])
                except Exception:
                    pass
                return emb
            except Exception as e:
                # Avoid printing full stacktrace for quota/client errors; warn and fallback
                logger.warning("Google embedding failed, falling back to local embeddings: %s", str(e))
                return self._local_embedding(text)
        return self._local_embedding(text)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        # If Google client available and API key present, call embeddings in batches
        if self.api_key and self.genai:
            try:
                client = self.genai.Client(api_key=self.api_key)
                embeddings = []
                # chunk texts
                for i in range(0, len(texts), self.batch_size):
                    batch = texts[i:i + self.batch_size]
                    if hasattr(client, 'models') and hasattr(client.models, 'embed_content'):
                        resp = client.models.embed_content(model=self.model, contents=batch)
                    elif hasattr(client, 'embeddings'):
                        resp = client.embeddings.create(model=self.model, input=batch)
                    else:
                        raise AttributeError('Google GenAI client has no embeddings interface')
                    batch_embs = self._extract_embeddings(resp)
                    embeddings.extend(batch_embs)
                arr = np.array(embeddings, dtype=float)
                return arr
            except Exception as e:
                # Avoid printing full stacktrace for quota/client errors; warn and fallback
                logger.warning("Google embedding failed, falling back to local embeddings: %s", str(e))

        # Fallback: deterministic local embeddings
        arr = [self._local_embedding(t) for t in texts]
        arr = np.vstack(arr)
        # update dimension to match local embeddings
        try:
            self.dim = int(arr.shape[1])
        except Exception:
            pass
        return arr
