import shutil
import time
from pathlib import Path
from src.engine.scanner import get_image_paths
from src.engine.processor import FaceProcessor

def run_search(target_image_path, search_dir, output_dir):
    # Initialize the CPU-optimized processor
    processor = FaceProcessor()
    
    # 1. Generate Target Embedding (The Reference)
    # For the target, we still want the primary/largest face to ensure quality
    print(f"[*] Analyzing target: {target_image_path}")
    target_embedding = processor.get_embedding(target_image_path)
    
    if target_embedding is None:
        print("[!] No face detected in target image. Please use a clearer photo.")
        return

    # 2. Prepare Output Directory (Autonomous Extraction)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 3. Scan and Match
    print(f"[*] Starting Deep-Scan in: {search_dir}")
    start_time = time.time()
    count = 0
    matches = 0
    
    
    

    for img_path in get_image_paths(search_dir):
        count += 1
        
        # Get ALL faces in the current image (handles small/background faces)
        candidate_embeddings = processor.get_all_embeddings(img_path)
        
        if candidate_embeddings:
            # Check if ANY of the faces in this image match the target
            is_match, score = processor.compare_faces(target_embedding, candidate_embeddings)
            
            if is_match:
                matches += 1
                # Non-destructive copy to the centralized directory
                destination = out_path / Path(img_path).name
                
                # Handle duplicate filenames in different folders
                if destination.exists():
                    destination = out_path / f"{matches}_{Path(img_path).name}"
                
                shutil.copy(img_path, destination)
                print(f"[+] Match found ({score:.2f}): {Path(img_path).name}")

    # 4. Performance Summary
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n{'='*30}")
    print(f"Scan Complete!")
    print(f"Processed: {count} images")
    print(f"Matches Found: {matches}")
    print(f"Total Time: {duration:.2f} seconds")
    print(f"Average Speed: {count/duration:.2f} images/sec")
    print(f"{'='*30}")

if __name__ == "__main__":
    # Ensure these paths exist before running
    run_search(
        target_image_path="data/targets/me.jpg", 
        search_dir="data/test_samples", 
        output_dir="data/found_images"
    )