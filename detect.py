import cv2
import numpy as np
from PIL import Image
from imagehash import phash
from sklearn.metrics.pairwise import cosine_similarity
import timm
import torch
from torchvision import transforms
import torch.nn as nn
import os
import time

TEMPORAL_WINDOW = 3
PHASH_DISTANCE_THRESHOLD = 0.2
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((299, 299)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5]*3, std=[0.5]*3),
])

def load_xception_model(weights_path=None):
    model = timm.create_model('xception', pretrained=True)
    model.fc = torch.nn.Identity()
    if weights_path and os.path.exists(weights_path):
        model.load_state_dict(torch.load(weights_path, map_location=device))
    model.to(device)
    model.eval()
    return model

def phash_to_binary_vector(p_hash):
    return np.array(p_hash.hash.flatten(), dtype=int)

def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(rgb)
    cap.release()
    return frames

def compute_cosine_similarity(vec1, vec2):
    return cosine_similarity([vec1], [vec2])[0][0]

def select_unique_frames(frames):
    selected, indices, hashes = [], [], []
    for i, frame in enumerate(frames):
        h = phash(Image.fromarray(frame))
        hash_vector = phash_to_binary_vector(h)
        if all(compute_cosine_similarity(hash_vector, prev) < PHASH_DISTANCE_THRESHOLD for prev in hashes):
            hashes.append(hash_vector)
            selected.append(frame)
            indices.append(i)
    return selected, indices

class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2, output_size=2):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        lstm_out, (_, _) = self.lstm(x)
        out = self.fc(lstm_out[:, -1, :])
        return out

def prepare_lstm_input(frames, model):
    tensor_batch = torch.stack([transform(Image.fromarray(f)) for f in frames]).to(device)
    with torch.no_grad():
        features = model(tensor_batch)
    return features

def detect_deepfake(video_path, model_weights=None):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found at: {video_path}")

    start_time = time.time()
    model = load_xception_model(model_weights)
    model_load_time = time.time() - start_time
    start_time = time.time()

    all_frames = extract_frames(video_path)
    frame_extraction_time = time.time() - start_time
    start_time = time.time()

    unique_frames, unique_indices = select_unique_frames(all_frames)
    frame_selection_time = time.time() - start_time
    start_time = time.time()

    if not unique_frames:
        return {
            "label": "Unknown",
            "confidence": 0.0,
            "reason": "No unique frames found",
            "time_taken": {
                "total": model_load_time + frame_extraction_time + frame_selection_time
            }
        }

    lstm_input = []
    for frame in unique_frames:
        lstm_input.append(prepare_lstm_input([frame], model))
    lstm_input = torch.stack(lstm_input).to(device)
    feature_extraction_time = time.time() - start_time
    start_time = time.time()

    lstm_model = LSTMModel(input_size=lstm_input.size(2)).to(device)
    lstm_output = lstm_model(lstm_input)
    lstm_probs = torch.nn.functional.softmax(lstm_output, dim=1).cpu().detach().numpy()
    inference_time = time.time() - start_time

    final_label = np.argmax(lstm_probs[0])

    total_time = (
        model_load_time +
        frame_extraction_time +
        frame_selection_time +
        feature_extraction_time +
        inference_time
    )

    return {
        "label": "FAKE" if final_label == 1 else "REAL",
        "confidence": float(lstm_probs[0][final_label]),
        "time_taken": {
            "model_load": model_load_time,
            "frame_extraction": frame_extraction_time,
            "frame_selection": frame_selection_time,
            "feature_extraction": feature_extraction_time,
            "inference": inference_time,
            "total": total_time
        }
    }
