from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable, NoTranscriptFound
from openai import OpenAI
from agents import Agent, Runner, WebSearchTool, function_tool, ItemHelpers
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
import os
import asyncio

# Load OpenAI API key
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

# Fetch transcript from YouTube video
def get_transcript(video_id: str, languages: list = None) -> str:
    if languages is None:
        languages = ['en']
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        return " ".join(snippet['text'] for snippet in transcript)
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except VideoUnavailable:
        return "The video is unavailable."
    except NoTranscriptFound:
        return "No transcript found for this video."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# Decorate the tool function so agent can recognize it
@function_tool
def generate_content(video_transcript: str, social_media_platform: str) -> str:
    print(f"Generating social media content for {social_media_platform}...")

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Here is a new video transcript:\n{video_transcript}\n\n"
                           f"Generate a social media post for {social_media_platform} based on the transcript."
            }
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()


@dataclass
class Post:
    platform: str
    content: str

# Define agent
content_writer_agent = Agent(
    name="Content Writer Agent",
    instructions="""You are a talented content writer who writes engaging, humorous, informative and highly readable social media posts.
You will be given a video transcript and a social media platform.
You will generate a social media post based on the transcript and the platform.
You may search the web for up-to-date information and enrich the post if needed.""",
    model="gpt-4o-mini",
    tools=[generate_content, WebSearchTool()],
    output_type=List[Post]
)

# Async runner
async def main():
    video_id = "OZ5OZZZ2cvk"
    transcript = get_transcript(video_id)

    msg = f"Generate a LinkedIn post based on this video transcript: {transcript}"

    input_items = [{"content": msg, "role": "user"}]

    result = await Runner.run(content_writer_agent, input_items)
    output = ItemHelpers.text_message_outputs(result.new_items)

    print("Generated Post:\n", output)

if __name__ == "__main__":
    asyncio.run(main())
