import cv2
import torch
import clip
import faiss
import numpy as np
import os
import json

class LocalClipInsight:
    def __init__(self, model_name="ViT-B/32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load(model_name, device=self.device)
        self.index = None
        self.metadata = []

    def index_video(self, video_path, sample_rate=1):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            if frame_count % int(fps * sample_rate) == 0:
                # Preprocess frame
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = clip.preprocess(torch.from_numpy(image).permute(2, 0, 1).float().to(self.device))
                
                with torch.no_grad():
                    feature = self.model.encode_image(image.unsqueeze(0))
                    feature /= feature.norm(dim=-1, keepdim=True)
                    
                feat_np = feature.cpu().numpy()
                if self.index is None:
                    self.index = faiss.IndexFlatIP(feat_np.shape[1])
                
                self.index.add(feat_np)
                self.metadata.append({"video": video_path, "timestamp": frame_count / fps})
            
            frame_count += 1
        cap.release()

    def search(self, query, top_k=5):
        text = clip.tokenize([query]).to(self.device)
        with torch.no_grad():
            text_feature = self.model.encode_text(text)
            text_feature /= text_feature.norm(dim=-1, keepdim=True)
        
        distances, indices = self.index.search(text_feature.cpu().numpy(), top_k)
        results = [self.metadata[idx] for idx in indices[0] if idx != -1]
        return results

if __name__ == "__main__":
    # Example usage
    lci = LocalClipInsight()
    print("System initialized. Ready to index.")