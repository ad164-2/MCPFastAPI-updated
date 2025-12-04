from enum import Enum
import httpx
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

# Global Configuration
# We use settings for configuration, but keep the HTTP client global for reuse
HTTP_CLIENT = httpx.Client(verify=False)

class ModelCapability(Enum):
    BASIC = "basic"           # For simple queries, summaries
    MODERATE = "moderate"
    REASONING = "reasoning"   # For complex logic, math (DeepSeek R1)
    VISION = "vision"         # For image analysis
    HIGH_PERF = "high_perf"   # For code gen, complex nuance
    EMBEDDING = "embedding"   # For RAG/Vector Stores
    AUDIO = "audio"           # For Speech-to-text

def get_model_name(capability: ModelCapability):
    """Maps capability to the specific model string from settings"""
    mapping = {
        ModelCapability.BASIC: settings.MODEL_CHAT_BASIC,
        ModelCapability.MODERATE: settings.MODEL_CHAT_MOD,
        ModelCapability.HIGH_PERF: settings.MODEL_CHAT_OPEN,
        ModelCapability.REASONING: settings.MODEL_REASONING,
        ModelCapability.VISION: settings.MODEL_VISION,
        ModelCapability.EMBEDDING: settings.MODEL_EMBEDDING,
        ModelCapability.AUDIO: settings.MODEL_AUDIO,
    }
    return mapping.get(capability)

def get_chat_llm(capability: ModelCapability = ModelCapability.BASIC, temperature: float = 0.7):
    """
    Returns a Chat Model instance (OpenAI or Google) based on configuration.
    """
    from app.core.utils import trace_llm_operation
    
    model_name = get_model_name(capability)
    
    # Validation: Ensure we don't pass Embedding/Audio models to the Chat client
    if capability in [ModelCapability.EMBEDDING, ModelCapability.AUDIO]:
        raise ValueError(f"Capability {capability.name} cannot be used with get_chat_llm")

    # DeepSeek R1 (Reasoning) usually benefits from lower temperature
    if capability == ModelCapability.REASONING:
        temperature = 0.1
    
    # Trace model initialization
    with trace_llm_operation(
        "llm.model.initialize",
        attributes={
            "llm.model": model_name or "default",
            "llm.capability": capability.value,
            "llm.temperature": temperature,
            "llm.provider": "ChatOpenAI"
        }
    ):

            return ChatGoogleGenerativeAI(
                model=model_name or "gemini-2.5-flash",
                google_api_key="AIzaSyCsoSAR3jkfvp-SaS3Ok5UDmh2AiCrfusg",
                temperature=temperature,
                convert_system_message_to_human=True
            )
            # Default to OpenAI-compatible (works for OpenAI, DeepSeek, etc.)
            # return ChatOpenAI(
            #     base_url=settings.API_ENDPOINT,
            #     model=model_name or settings.default_model,
            #     api_key=settings.API_KEY,
            #     http_client=HTTP_CLIENT,
            #     temperature=temperature
            # )

def get_embeddings():
    """
    Returns the OpenAIEmbeddings client specifically for Vector operations.
    """
    model_name = get_model_name(ModelCapability.EMBEDDING)
    print(f"Initializing Embeddings: {model_name}")
    
    return OpenAIEmbeddings(
        base_url=settings.API_ENDPOINT,
        model=model_name or settings.embedding_model,
        api_key=settings.API_KEY,
        http_client=HTTP_CLIENT
    )

def get_audio_client():
    """
    LangChain ChatOpenAI does not support Whisper natively for transcription.
    We return the raw OpenAI client wrapper for this.
    """
    print(f"Initializing Audio Client")
    return OpenAI(
        base_url=settings.API_ENDPOINT,
        api_key=settings.API_KEY,
        http_client=HTTP_CLIENT
    )
