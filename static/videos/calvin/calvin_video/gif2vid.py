import os
import re
from moviepy.editor import VideoFileClip, concatenate_videoclips

def create_individual_videos_for_successful_trials(gif_directory, output_directory):
    """
    Finds successful trials and creates a SEPARATE video for EACH trial.

    A trial is considered successful if it contains 5 successful steps (tasks 0 through 4).
    For each such trial, the script concatenates its 5 GIFs into a single .mp4 video file.

    Args:
        gif_directory (str): The full path to the directory containing the GIF files.
        output_directory (str): The full path to the directory where the output videos will be saved.
    """
    # --- 1. Scan directory and parse filenames ---
    print(f"Scanning directory: {gif_directory}")
    all_files = [f for f in os.listdir(gif_directory) if f.endswith('.gif')]

    if not all_files:
        print("No GIF files found in the specified directory.")
        return

    # Group all file information by their trial number
    file_info = {}
    
    for f in all_files:
        parts = f.replace('.gif', '').split('-')
        if len(parts) >= 4:
            try:
                trial_num = int(parts[0])
                task_num = int(parts[1])
                status = parts[-1]
                task_name = "-".join(parts[2:-1])

                if trial_num not in file_info:
                    file_info[trial_num] = []
                file_info[trial_num].append({
                    "task_num": task_num,
                    "task_name": task_name,
                    "status": status,
                    "filename": f
                })
            except (ValueError, IndexError):
                print(f"Could not parse filename, skipping: {f}")
                continue

    # --- 2. Process each trial individually ---
    print("\nChecking trials and creating videos...")
    successful_trials_found = 0

    # Sort by trial number for organized processing
    for trial_num in sorted(file_info.keys()):
        
        trial_files = file_info[trial_num]
        
        # A trial is only valid if it has 5 successful steps (0-4)
        successful_steps = [info for info in trial_files if info['status'] == 'succ']
        successful_steps.sort(key=lambda x: x['task_num'])

        # Check if the trial is complete and successful (tasks 0, 1, 2, 3, 4 all 'succ')
        if len(successful_steps) == 5 and all(s['task_num'] == j for j, s in enumerate(successful_steps)):
            successful_trials_found += 1
            print(f"\nFound complete successful trial: {trial_num}. Creating video...")

            # --- Create a video for THIS trial ---
            clips_for_this_trial = []
            task_names_for_this_trial = []

            for step_info in successful_steps:
                filepath = os.path.join(gif_directory, step_info['filename'])
                print(f"  Adding step {step_info['task_num']}: {step_info['filename']}")
                clips_for_this_trial.append(VideoFileClip(filepath))
                task_names_for_this_trial.append(step_info['task_name'])
            
            # Concatenate the clips for this trial only
            trial_video_clip = concatenate_videoclips(clips_for_this_trial)
            
            # --- Generate a unique name and save the video ---
            base_video_name = f"trial_{trial_num}_" + "_".join(task_names_for_this_trial)
            # Sanitize the filename to remove invalid characters
            sanitized_video_name = re.sub(r'[\\/*?:"<>|]', "", base_video_name) + ".mp4"
            
            os.makedirs(output_directory, exist_ok=True)
            output_path = os.path.join(output_directory, sanitized_video_name)
            
            print(f"  Saving video to: {output_path}")
            trial_video_clip.write_videofile(output_path, codec='libx264', fps=24, logger='bar')
            
    if successful_trials_found == 0:
        print("\nNo complete successful trials were found to create videos from.")
    else:
        print(f"\nProcessing complete. Created {successful_trials_found} video(s).")


# --- HOW TO USE ---
if __name__ == '__main__':
    # 1. CHANGE THIS: Set the path to the directory where your GIFs are stored.
    #    (Use forward slashes / even on Windows for Python strings)
    gif_directory = "/home/v-wangxiaofa/lzl/calvin/results_pt_180K_qwen_pi0-8bit-adam-3-frame_12.5K_astep_10"

    # 2. CHANGE THIS: Set the path where you want to save the final videos.
    output_directory = "/home/v-wangxiaofa/lzl/calvin/calvin_video/"

    # 3. Run the function
    create_individual_videos_for_successful_trials(gif_directory, output_directory)