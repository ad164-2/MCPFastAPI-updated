from enum import Enum
import os
import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from openai import OpenAI  # Standard client for Audio/Whisper
from langchain_google_genai import ChatGoogleGenerativeAI

# Load variables
load_dotenv()

# Global Configuration
BASE_URL = os.getenv("API_ENDPOINT")
API_KEY = os.getenv("API_KEY")
HTTP_CLIENT = httpx.Client(verify=False)

class ModelCapability(Enum):
    BASIC = "basic"           # For simple queries, summaries
    MODERATE="moderate"
    REASONING = "reasoning"   # For complex logic, math (DeepSeek R1)
    VISION = "vision"         # For image analysis
    HIGH_PERF = "high_perf"   # For code gen, complex nuance
    EMBEDDING = "embedding"   # For RAG/Vector Stores
    AUDIO = "audio"           # For Speech-to-text

def get_model_name(capability: ModelCapability):
    """Maps capability to the specific model string from .env"""
    mapping = {
        ModelCapability.BASIC: os.getenv("MODEL_CHAT_BASIC"),
        ModelCapability.MODERATE:os.getenv("MODEL_CHAT_MOD"),
        ModelCapability.HIGH_PERF: os.getenv("MODEL_CHAT_OPEN"), # or DeepSeek-V3
        ModelCapability.REASONING: os.getenv("MODEL_REASONING"),
        ModelCapability.VISION: os.getenv("MODEL_VISION"),
        ModelCapability.EMBEDDING: os.getenv("MODEL_EMBEDDING"),
        ModelCapability.AUDIO: os.getenv("MODEL_AUDIO"),
    }
    return mapping.get(capability)

def get_chat_llm(capability: ModelCapability = ModelCapability.BASIC, temperature: float = 0.7):
    """
    Returns a ChatOpenAI instance for Text, Vision, or Reasoning models.
    """
    model_name = get_model_name(capability)
    
    # Validation: Ensure we don't pass Embedding/Audio models to the Chat client
    if capability in [ModelCapability.EMBEDDING, ModelCapability.AUDIO]:
        raise ValueError(f"Capability {capability.name} cannot be used with get_chat_llm")

    # DeepSeek R1 (Reasoning) usually benefits from lower temperature
    if capability == ModelCapability.REASONING:
        temperature = 0.1

    print(f"Initializing Chat Model: {model_name}")
    
    # return ChatOpenAI(
    #     base_url=BASE_URL,
    #     model=model_name,
    #     api_key=API_KEY,
    #     http_client=HTTP_CLIENT,
    #     temperature=temperature
    # )

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key='',
        temperature=0.7,
        convert_system_message_to_human=True  # Required for Gemini models
    )

def get_embeddings():
    """
    Returns the OpenAIEmbeddings client specifically for Vector operations.
    """
    model_name = get_model_name(ModelCapability.EMBEDDING)
    print(f"Initializing Embeddings: {model_name}")
    
    return OpenAIEmbeddings(
        base_url=BASE_URL,
        model=model_name,
        api_key=API_KEY,
        http_client=HTTP_CLIENT
    )

def get_audio_client():
    """
    LangChain ChatOpenAI does not support Whisper natively for transcription.
    We return the raw OpenAI client wrapper for this.
    """
    print(f"Initializing Audio Client")
    return OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        http_client=HTTP_CLIENT

    )
