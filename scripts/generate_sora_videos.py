#!/usr/bin/env python3
"""
EverReach Sora Video Generator
Generates actual videos from prompts using OpenAI Sora API
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from openai import OpenAI

class SoraVideoGenerator:
    """Generate videos from EverReach prompts using Sora API"""
    
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self.poll_interval = 10  # seconds
        self.output_dir = Path(__file__).parent.parent / "videos"
        self.output_dir.mkdir(exist_ok=True)
        
    def build_sora_prompt(self, generation: dict) -> str:
        """Convert our prompt spec into a Sora-ready prompt"""
        content = generation.get("generated_content", "")
        sora_core = generation.get("sora_core", "")
        
        # Extract voiceover from generated content
        voiceover_start = content.find("VOICEOVER:")
        if voiceover_start != -1:
            voiceover = content[voiceover_start + 10:].split("\n\n")[0].strip()
        else:
            voiceover = ""
        
        # Extract scene plan
        scene_start = content.find("SCENE_PLAN:")
        scene_end = content.find("ON_SCREEN_TEXT:")
        if scene_start != -1 and scene_end != -1:
            scene_plan = content[scene_start + 11:scene_end].strip()
        else:
            scene_plan = ""
            
        # Build comprehensive Sora prompt
        sora_prompt = f"""
{sora_core}

VIDEO CONTENT:
{scene_plan}

STYLE: Modern UGC ad for EverReach relationship app. Clean, high contrast, natural lighting.
Main character: Professional in their late 20s-30s, founder/consultant vibe.
Setting: Home office or coworking space.
Mood: Confident, relatable, slightly intense.
End with: EverReach logo and "Start with 1 person" CTA.

NARRATIVE FLOW:
{voiceover[:500]}
"""
        return sora_prompt.strip()
    
    def generate_video(self, prompt: str, prompt_id: str, seconds: int = 10) -> dict:
        """Generate a single video using Sora API"""
        print(f"\n{'='*60}")
        print(f"Generating video for: {prompt_id}")
        print(f"{'='*60}")
        
        try:
            # Create video generation job using correct Sora API format
            # sora-2 supports: size='720x1280' or '1280x720', seconds='4','8','12'
            response = self.client.videos.create(
                prompt=prompt,
                model="sora-2",
                size="720x1280",  # 9:16 vertical for social ads
                seconds="8"
            )
            
            job_id = response.id
            print(f"✓ Video job created: {job_id}")
            
            return {
                "job_id": job_id,
                "prompt_id": prompt_id,
                "status": response.status if hasattr(response, 'status') else "queued",
                "created_at": time.time()
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Error creating video: {error_msg}")
            return {
                "prompt_id": prompt_id,
                "status": "error",
                "error": error_msg
            }
    
    def poll_job(self, job_id: str, timeout: int = 600) -> dict:
        """Poll until video is ready or timeout"""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            try:
                job = self.client.videos.retrieve(job_id)
                
                if job.status == "completed":
                    print(f"✓ Video completed!")
                    return {
                        "status": "completed",
                        "job_id": job_id
                    }
                elif job.status == "failed":
                    error = str(job.error) if hasattr(job, 'error') else "Unknown error"
                    print(f"✗ Video failed: {error}")
                    return {"status": "failed", "error": error, "job_id": job_id}
                else:
                    elapsed = int(time.time() - start_time)
                    print(f"⏳ Status: {job.status} (elapsed: {elapsed}s)")
                    time.sleep(self.poll_interval)
                    
            except Exception as e:
                print(f"✗ Poll error: {e}")
                time.sleep(self.poll_interval)
        
        return {"status": "timeout", "job_id": job_id}
    
    def download_video(self, job_id: str, output_path: Path) -> bool:
        """Download video using OpenAI's download_content method"""
        try:
            content = self.client.videos.download_content(job_id)
            with open(output_path, 'wb') as f:
                f.write(content.read())
            
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"✓ Downloaded: {output_path.name} ({size_mb:.2f} MB)")
            return True
            
        except Exception as e:
            print(f"✗ Download failed: {e}")
            return False
    
    def process_generation(self, generation: dict, index: int) -> dict:
        """Process a single generation: build prompt, generate, poll, download"""
        prompt_id = f"ER-{generation['awareness_level'].upper()[:2]}-{index:03d}"
        
        # Build Sora prompt
        sora_prompt = self.build_sora_prompt(generation)
        
        # Generate video
        job_result = self.generate_video(sora_prompt, prompt_id)
        
        if job_result.get("status") == "error":
            return job_result
        
        # Poll for completion
        poll_result = self.poll_job(job_result["job_id"])
        
        if poll_result.get("status") == "completed":
            # Download video using job_id
            job_id = poll_result.get("job_id")
            output_path = self.output_dir / f"{prompt_id}.mp4"
            
            if self.download_video(job_id, output_path):
                poll_result["local_path"] = str(output_path)
        
        poll_result["prompt_id"] = prompt_id
        poll_result["awareness_level"] = generation["awareness_level"]
        poll_result["belief"] = generation["belief"]
        poll_result["hook"] = generation["hook"]
        
        return poll_result


def main():
    # Load generations
    generations_path = Path(__file__).parent.parent / "generations" / "test_generations.json"
    
    if not generations_path.exists():
        print("✗ No generations found. Run generate_sora_prompts.py first.")
        sys.exit(1)
    
    with open(generations_path) as f:
        generations = json.load(f)
    
    print(f"\n{'='*60}")
    print(f"EverReach Sora Video Generator")
    print(f"Found {len(generations)} prompts to process")
    print(f"{'='*60}")
    
    # Check for existing videos
    generator = SoraVideoGenerator()
    existing_videos = list(generator.output_dir.glob("*.mp4"))
    print(f"Existing videos: {len(existing_videos)}")
    
    # Track results
    results = []
    
    # Process each generation
    for i, gen in enumerate(generations, 1):
        prompt_id = f"ER-{gen['awareness_level'].upper()[:2]}-{i:03d}"
        video_path = generator.output_dir / f"{prompt_id}.mp4"
        
        # Skip if already generated
        if video_path.exists():
            print(f"\n⏭ Skipping {prompt_id} - already exists")
            results.append({
                "prompt_id": prompt_id,
                "status": "exists",
                "local_path": str(video_path)
            })
            continue
        
        # Generate video
        result = generator.process_generation(gen, i)
        results.append(result)
        
        # Save progress after each video
        results_path = generator.output_dir / "generation_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    # Summary
    print(f"\n{'='*60}")
    print("GENERATION SUMMARY")
    print(f"{'='*60}")
    
    completed = sum(1 for r in results if r.get("status") in ["completed", "exists"])
    failed = sum(1 for r in results if r.get("status") == "failed")
    errors = sum(1 for r in results if r.get("status") == "error")
    
    print(f"✓ Completed: {completed}")
    print(f"✗ Failed: {failed}")
    print(f"⚠ Errors: {errors}")
    print(f"\nVideos saved to: {generator.output_dir}")
    
    return results


if __name__ == "__main__":
    main()
