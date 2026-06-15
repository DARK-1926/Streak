import os
import tempfile
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import faiss
import numpy as np

class VideoIndexer:
    def __init__(self, model_name="openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.index = None
        self.metadata = []

    def extract_frames(self, video_path, max_frames=10):
        # Placeholder: in real implementation use cv2 to read video frames
        frames = []
        for i in range(max_frames):
            img = Image.new("RGB", (224, 224), color="gray")
            frames.append(img)
        return frames

    def embed_frames(self, frames):
        inputs = self.processor(images=frames, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            embeddings = self.model.get_image_features(**inputs).cpu().numpy()
        return embeddings

    def build_index(self, video_dir):
        all_embeddings = []
        for root, _, files in os.walk(video_dir):
            for f in files:
                if f.lower().endswith(('.mp4', '.mov', '.avi')):
                    video_path = os.path.join(root, f)
                    frames = self.extract_frames(video_path)
                    embs = self.embed_frames(frames)
                    all_embeddings.append(embs)
                    self.metadata.append(video_path)
        # Concatenate embeddings
        all_embeddings = np.vstack(all_embeddings)
        self.index = faiss.IndexFlatL2(all_embeddings.shape[1])
        self.index.add(all_embeddings)

    def search(self, query, top_k=5):
        if self.index is None:
            raise RuntimeError("Index not built yet.")
        inputs = self.processor(text=[query], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            txt_emb = self.model.get_text_features(**inputs).cpu().numpy()
        D, I = self.index.search(txt_emb, top_k)
        results = []
        for idx in I[0]:
            results.append(self.metadata[idx])
        return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Path to video directory")
    args = parser.parse_args()
    idx = VideoIndexer()
    idx.build_index(args.dir)
    print("Index built. Ready for search.")
