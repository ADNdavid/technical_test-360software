from pathlib import Path
import numpy as np
from typing import List
from app.core.config import Settings
from app.utils.excel_loader import load_table, REQUIRED_PRODUCT_COLUMNS
import json
from pathlib import Path
import hashlib


class ProductRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.products = load_table(Path(settings.PRODUCTS_EXCEL_PATH), required_columns=REQUIRED_PRODUCT_COLUMNS)
        self.embeddings = None
        self.ids = list(self.products.get('PLU', self.products.index.astype(str)))
        # prepare texts and hashes for change detection
        self.texts = [self.build_text_for_product(r) for _, r in self.products.iterrows()]
        self.hashes = [hashlib.md5(t.encode('utf-8')).hexdigest() for t in self.texts]

        # embedding cache paths
        self.cache_dir = Path(getattr(settings, 'EMBEDDINGS_CACHE_DIR', Path('data/embeddings')))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._emb_path = self.cache_dir / 'embeddings.npy'
        self._ids_path = self.cache_dir / 'ids.json'
        self._hashes_path = self.cache_dir / 'hashes.json'

        # try loading cached embeddings if they match
        try:
            if self._emb_path.exists() and self._ids_path.exists() and self._hashes_path.exists():
                with open(self._ids_path, 'r', encoding='utf-8') as f:
                    cached_ids = json.load(f)
                with open(self._hashes_path, 'r', encoding='utf-8') as f:
                    cached_hashes = json.load(f)
                if cached_ids == self.ids and cached_hashes == self.hashes:
                    import numpy as _np
                    self.embeddings = _np.load(self._emb_path)
        except Exception:
            # ignore cache load errors and rebuild on demand
            self.embeddings = None

    def build_text_for_product(self, row) -> str:
        parts = []
        if row.get('descripcion'):
            parts.append(f"Descripción: {row.get('descripcion')}")
        if row.get('nompro'):
            parts.append(f"Nombre: {row.get('nompro')}")
        if row.get('codpro'):
            parts.append(f"Código: {row.get('codpro')}")
        return " \n ".join(parts)

    def index_products(self, embedding_service):
        # recompute texts and hashes in case products changed
        self.texts = [self.build_text_for_product(r) for _, r in self.products.iterrows()]
        self.hashes = [hashlib.md5(t.encode('utf-8')).hexdigest() for t in self.texts]

        if not self.texts:
            self.embeddings = np.zeros((0, embedding_service.dim))
            return

        # load existing embeddings if available
        existing = None
        if self._emb_path.exists() and self._ids_path.exists():
            try:
                import numpy as _np
                existing = _np.load(self._emb_path)
            except Exception:
                existing = None

        # determine which indices need recomputing by comparing hashes
        recompute_idx = []
        if existing is None or existing.shape[0] != len(self.texts):
            recompute_idx = list(range(len(self.texts)))
        else:
            try:
                with open(self._hashes_path, 'r', encoding='utf-8') as f:
                    cached_hashes = json.load(f)
                for i, (old_h, new_h) in enumerate(zip(cached_hashes, self.hashes)):
                    if old_h != new_h:
                        recompute_idx.append(i)
            except Exception:
                recompute_idx = list(range(len(self.texts)))

        # if nothing to recompute, assign existing
        if not recompute_idx and existing is not None:
            self.embeddings = existing
            return

        # build or update embeddings array lazily once we know embedding dim
        import numpy as _np
        embeddings = existing if existing is not None else None

        # process recompute in batches to avoid memory issues
        batch_size = getattr(self.settings, 'EMBEDDING_BATCH_SIZE', 16)
        idx_batches = [recompute_idx[i:i+batch_size] for i in range(0, len(recompute_idx), batch_size)]
        for batch_idxs in idx_batches:
            batch_texts = [self.texts[i] for i in batch_idxs]
            batch_embs = embedding_service.embed_texts(batch_texts)

            # ensure numpy array
            batch_embs = _np.asarray(batch_embs, dtype=float)

            # on first batch, if embeddings not initialized, create array with proper dim
            if embeddings is None:
                dim = batch_embs.shape[1]
                embeddings = _np.zeros((len(self.texts), dim), dtype=float)
                # if existing was present but had mismatched dim, we overwrite
            # verify dims match
            if embeddings.shape[1] != batch_embs.shape[1]:
                # incompatible dims: recreate full embeddings array with new dim
                dim = batch_embs.shape[1]
                embeddings = _np.zeros((len(self.texts), dim), dtype=float)

            for j, emb in enumerate(batch_embs):
                embeddings[batch_idxs[j]] = emb

        # save cache
        try:
            _np.save(self._emb_path, embeddings)
            with open(self._ids_path, 'w', encoding='utf-8') as f:
                json.dump(self.ids, f)
            with open(self._hashes_path, 'w', encoding='utf-8') as f:
                json.dump(self.hashes, f)
        except Exception:
            logger = logging.getLogger(__name__)
            logger.warning('Failed to save embeddings cache; continuing without persistence')

        self.embeddings = embeddings

    def _text_match_score(self, query: str, text: str) -> float:
        if not query or not text:
            return 0.0
        query = query.lower().strip()
        text = text.lower().strip()
        if query in text:
            return 1.0
        # partial match score based on token overlap
        query_tokens = set(query.split())
        text_tokens = set(text.split())
        if not query_tokens:
            return 0.0
        overlap = len(query_tokens & text_tokens)
        score = overlap / len(query_tokens)
        return float(score)

    def top_k_similar(self, query_embedding: np.ndarray, query_text: str, k: int = 5) -> List[dict]:
        if self.embeddings is None or len(self.embeddings) == 0:
            return []
        query = query_embedding.reshape(1, -1)
        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            return []
        embeddings_norm = np.linalg.norm(self.embeddings, axis=1)
        zero_mask = embeddings_norm == 0
        embeddings_norm[zero_mask] = 1.0
        semantic_sims = np.dot(self.embeddings, query.flatten()) / (embeddings_norm * query_norm)

        results = []
        for i, sim in enumerate(semantic_sims):
            row = self.products.iloc[i].to_dict()
            category = str(row.get('nompro', '') or row.get('tipo_inv', ''))
            description = str(row.get('descripcion', ''))
            text_score = max(
                self._text_match_score(query_text, category),
                self._text_match_score(query_text, description),
            )
            # combine semantic similarity with lexical match
            score = 0.7 * float(sim) + 0.3 * text_score
            results.append({
                "product_id": str(row.get('PLU') or row.get('codpro') or i),
                "description": description,
                "category": category,
                "similarity": float(score),
                "semantic_similarity": float(sim),
                "text_match": float(text_score),
            })

        results.sort(key=lambda item: item['similarity'], reverse=True)
        return results[:k]
