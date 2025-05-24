from social_media_script import get_transcript

def main():
    video_id = "OZ5OZZZ2cvk"
    try: 
        transcript = get_transcript(video_id)
        print("Successfully retrieved transcript")
        print(transcript[:500])
    except Exception as e:
        print(f"Error retrieving transcript: {e}")

if __name__ == "__main__":
    main()