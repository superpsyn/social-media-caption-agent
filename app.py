import streamlit as st
import re
import asyncio
import json
from social_media_script import get_transcript, content_writer_agent, Runner, ItemHelpers

# Function to extract video ID from YouTube link
def extract_video_id(youtube_url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, youtube_url)
    return match.group(1) if match else None

# Async wrapper to be called safely inside Streamlit
async def generate_post(video_id):
    transcript = get_transcript(video_id)
    msg = f"Generate an Instagram post based on this video transcript: {transcript}"
    input_items = [{"content": msg, "role": "user"}]
    result = await Runner.run(content_writer_agent, input_items)
    return ItemHelpers.text_message_outputs(result.new_items)

# Streamlit UI
st.title("📢 Social Media Post Generator")
st.write("Paste a YouTube video link to auto-generate a social media post based on its transcript.")

youtube_url = st.text_input("🎥 YouTube Video Link")

if st.button("Generate Post"):
    if not youtube_url:
        st.error("Please enter a YouTube video link.")
    else:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.error("Invalid YouTube link. Please enter a valid link.")
        else:
            st.info(f"Video ID: `{video_id}`")

            with st.spinner("Generating post from transcript..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    raw_output = loop.run_until_complete(generate_post(video_id))
                    loop.close()

                    # Parse response assuming it's a JSON string with platform and content
                    response = json.loads(raw_output) if isinstance(raw_output, str) else raw_output
                    post_data = response["response"][0] if isinstance(response, dict) else response[0]

                    # Display formatted post
                    st.success("✅ Social Media Post Generated!")
                    st.subheader(f"📝 Platform: {post_data['platform']}")
                    st.markdown(post_data["content"])

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
