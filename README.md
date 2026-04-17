
---

# FaceSearch: The Utility Agent

**FaceSearch** is a high-performance file-traversal and facial-recognition agent designed to automate the discovery and extraction of specific individuals from large, unorganized image datasets.

## Problem Statement
Manually searching for specific people across deep local directories or cloud storage is time-consuming. FaceSearch automates this by treating facial data as a searchable index, allowing for rapid, autonomous isolation of relevant files.

## Key Features
* **Recursive Deep-Scan:** Automatically traverses multi-level folder structures to ensure complete coverage.
* **Vectorized Recognition:** Uses high-dimensional embeddings to identify target faces with high precision, moving beyond simple metadata searches.
* **Autonomous Extraction:** Automatically creates a centralized `found_images` directory and copies all matched files there.
* **CPU-Optimized Inference:** Engineered to deliver high-speed results on local consumer hardware without requiring dedicated GPU resources.
* **Cloud Integration:** Capable of bridging with Google Drive via MCP to treat cloud directories as local filesystems.

## Capabilities & Performance
* **High Efficiency:** Targeted to process **1,000+ images in under 5 minutes** on standard local CPUs.
* **Accuracy:** Designed to maintain a **95%+ success rate** in isolating target face occurrences.
* **Non-Destructive:** Performs copy operations by default to ensure original directory structures remain intact.

## Tech Stack
* **Language:** Python
* **Frameworks:** InsightFace / YOLOv8-face
* **Backend:** ONNX Runtime (Optimized for CPU)
* **Automation:** Model Context Protocol (MCP) for cloud-local bridging

---
