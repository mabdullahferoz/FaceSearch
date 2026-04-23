import cv2
import numpy as np
from insightface.app import FaceAnalysis

class FaceProcessor:
    def __init__(self, det_size=(640, 640)):
        # CPU-optimized provider as per README requirements
        self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=det_size)

    def get_embedding(self, image_path):
        """Extracts the embedding for the largest face in an image."""
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        faces = self.app.get(img)
        if not faces:
            return None
        
        # Sort by box size to get the primary face (useful for target images)
        faces.sort(key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)
        return faces[0].normed_embedding
    
    def get_all_embeddings(self, image_path):
        """Extracts embeddings for EVERY face found in an image."""
        img = cv2.imread(image_path)
        if img is None:
            print("No image found!")
            return None
        
        faces = self.app.get(img)
        if not faces:
            print("No clear faces found!")
            return None
        
        return [face.normed_embedding for face in faces]

    def get_all_embeddings_from_bytes(self, image_bytes):
        """Processes an image directly from memory/buffer."""
        # Convert byte stream to a numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        # Decode the array into an OpenCV image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return []
            
        faces = self.app.get(img)
        return [face.normed_embedding for face in faces]

    @staticmethod
    def compare_faces(target_emb, candidate_embeddings, threshold=0.6):
        """
        Compares one target against a LIST of candidate embeddings.
        Returns True if ANY face matches.
        """
        for cand_emb in candidate_embeddings:
            sim = np.dot(target_emb, cand_emb)
            if sim >= threshold:
                return True, sim
        return False, 0.0