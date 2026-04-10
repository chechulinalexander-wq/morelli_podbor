import sqlite3
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple


class RecommendationEngine:
    def __init__(self, db_path: str = 'handles.db'):
        self.db_path = db_path
        self.metadata_weight = 0.7
        self.embedding_weight = 0.3
        
    def recommend_handles(self, door_features: dict, top_n: int = 5) -> List[Dict]:
        print(f'[RecommendationEngine] Starting recommendation process for top {top_n} handles')
        
        filtered_handles = self._filter_by_metadata(door_features)
        print(f'[RecommendationEngine] Filtered to {len(filtered_handles)} handles')
        
        if not filtered_handles:
            print('[RecommendationEngine] WARNING: No handles passed filter, using all')
            filtered_handles = self._get_all_handles()
        
        scored_handles = self._calculate_scores(door_features, filtered_handles)
        scored_handles.sort(key=lambda x: x['final_score'], reverse=True)
        top_recommendations = scored_handles[:top_n]
        
        print('[RecommendationEngine] Top recommendations:')
        for i, handle in enumerate(top_recommendations, 1):
            print(f"  {i}. {handle['name']} (score: {handle['final_score']:.3f})")
        
        return top_recommendations
    
    def _filter_by_metadata(self, door_features: dict) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, product_id, name, description, material, type, rose_shape, 
                   url, finish_color, style, color_group, series, image_path, image_url, image_embedding
            FROM handles
            WHERE type = ?
        '''
        
        cursor.execute(query, ('Раздельная',))
        rows = cursor.fetchall()
        
        handles = []
        for row in rows:
            try:
                embedding_data = row[14]
                if isinstance(embedding_data, str):
                    embedding = json.loads(embedding_data)
                elif isinstance(embedding_data, bytes):
                    embedding = json.loads(embedding_data.decode('utf-8'))
                else:
                    embedding = embedding_data
            except:
                embedding = None
            
            handles.append({
                'id': row[0],
                'product_id': row[1],
                'name': row[2],
                'description': row[3],
                'material': row[4],
                'type': row[5],
                'rose_shape': row[6],
                'url': row[7],
                'finish_color': row[8],
                'style': row[9],
                'color_group': row[10],
                'series': row[11],
                'image_path': row[12],
                'image_url': row[13],
                'embedding': embedding
            })
        
        conn.close()
        return handles
    
    def _get_all_handles(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, product_id, name, description, material, type, rose_shape, 
                   url, finish_color, style, color_group, series, image_path, image_url, image_embedding
            FROM handles
        ''')
        
        rows = cursor.fetchall()
        handles = []
        
        for row in rows:
            try:
                embedding_data = row[14]
                if isinstance(embedding_data, str):
                    embedding = json.loads(embedding_data)
                elif isinstance(embedding_data, bytes):
                    embedding = json.loads(embedding_data.decode('utf-8'))
                else:
                    embedding = embedding_data
            except:
                embedding = None
            
            handles.append({
                'id': row[0],
                'product_id': row[1],
                'name': row[2],
                'description': row[3],
                'material': row[4],
                'type': row[5],
                'rose_shape': row[6],
                'url': row[7],
                'finish_color': row[8],
                'style': row[9],
                'color_group': row[10],
                'series': row[11],
                'image_path': row[12],
                'image_url': row[13],
                'embedding': embedding
            })
        
        conn.close()
        return handles
    
    def _calculate_scores(self, door_features: dict, handles: List[Dict]) -> List[Dict]:
        door_embedding = np.array(door_features['embedding']).reshape(1, -1)
        
        for handle in handles:
            metadata_score = self._calculate_metadata_score(door_features, handle)
            
            embedding_score = 0.0
            if handle.get('embedding'):
                try:
                    handle_embedding = np.array(handle['embedding']).reshape(1, -1)
                    similarity = cosine_similarity(door_embedding, handle_embedding)[0][0]
                    embedding_score = float(similarity)
                except Exception as e:
                    print(f'[RecommendationEngine] Embedding calc error: {e}')
            
            final_score = (metadata_score * self.metadata_weight + 
                          embedding_score * self.embedding_weight)
            
            handle['metadata_score'] = metadata_score
            handle['embedding_score'] = embedding_score
            handle['final_score'] = final_score
        
        return handles
    
    def _calculate_metadata_score(self, door_features: dict, handle: Dict) -> float:
        score = 0.0
        total_weight = 0.0
        
        # Rose shape matching (weight: 0.2)
        if door_features.get('preferred_rose_shape') == handle.get('rose_shape'):
            score += 0.2
        total_weight += 0.2
        
        # Color group matching (weight: 0.4)
        if door_features.get('preferred_color_group') == handle.get('color_group'):
            score += 0.4
        elif door_features.get('need_contrast'):
            if handle.get('color_group') and handle.get('color_group') != door_features.get('door_color_group'):
                score += 0.2
        total_weight += 0.4
        
        # Style matching (weight: 0.3)
        door_style = door_features.get('door_style', '')
        handle_style = handle.get('style', '')
        if handle_style and door_style:
            style_match = any(keyword in handle_style.lower() for keyword in door_style.lower().split('_'))
            if style_match:
                score += 0.3
        total_weight += 0.3
        
        # Finish color matching (weight: 0.1)
        preferred_colors = door_features.get('preferred_finish_colors', [])
        handle_color = handle.get('finish_color', '')
        if any(pref_color in handle_color.lower() for pref_color in preferred_colors):
            score += 0.1
        total_weight += 0.1
        
        return score / total_weight if total_weight > 0 else 0.0
