import shutil
import time
from pathlib import Path
from src.engine.scanner import get_image_paths
from src.engine.processor import FaceProcessor
from src.utils.auth import get_drive_service
from src.utils.drive_handler import DriveHandler
from src.utils.extract_id_from_link import extract_folder_id


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


def run_drive_search(target_path, drive_folder_id, output_dir):
    service = get_drive_service() # This will use your credentials.json
    handler = DriveHandler(service)
    processor = FaceProcessor()
    
    # Analyze local target
    print(f"[*] Analyzing local target: {target_path}")
    target_emb = processor.get_embedding(target_path)
    if target_emb is None: return

    # Recursive Discovery
    print(f"[*] Scanning Drive folder {drive_folder_id} recursively...")
    drive_files = handler.list_all_images_recursive(drive_folder_id)
    print(f"[*] Found {len(drive_files)} images total. Starting memory-stream scan...")

    for file in drive_files:
        # In-memory processing
        img_bytes = handler.get_file_bytes(file['id'])
        candidate_embs = processor.get_all_embeddings_from_bytes(img_bytes)
        
        if candidate_embs:
            # Cosine similarity math
            is_match, score = processor.compare_faces(target_emb, candidate_embs)
            if is_match:
                # Targeted download
                save_path = Path(output_dir) / file['name']
                with open(save_path, "wb") as f:
                    f.write(img_bytes)
                print(f"[+] Match found on Drive ({score:.2f}): {file['name']}")


if __name__ == "__main__":
    # Configuration
    TARGET_IMG = "data/targets/me.jpg"
    OUT_DIR = "data/found_images"
    
    print("--- FaceSearch Utility Agent ---")
    print("1. Search Local Directory")
    print("2. Search Google Drive")
    choice = input("Select mode (1/2): ")

    if choice == "1":
        search_path = input("Enter local path to scan (e.g., data/test_samples): ")
        run_search(TARGET_IMG, search_path, OUT_DIR)
        
    elif choice == "2":
        # Note: You can find the Folder ID in your browser URL when the folder is open
        raw_input = input("Paste Google Drive Folder Link or ID: ")
        folder_id = extract_folder_id(raw_input) # Automatically cleans the link
        run_drive_search(TARGET_IMG, folder_id, OUT_DIR)
        
    else:
        print("[!] Invalid choice. Exiting.")