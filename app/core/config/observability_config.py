"""
Observability configuration and initialization.

Sets up OpenTelemetry and Phoenix for LLM observability.
"""

import os
from app.core.config import settings
from app.core.utils import get_logger

logger = get_logger(__name__)


def initialize_observability():
    """
    Initialize observability infrastructure.
    
    Sets up:
    - OpenTelemetry tracer
    - Phoenix integration
    - Traceloop SDK for LLM instrumentation
    """
    if not settings.enable_observability:
        logger.info("Observability is disabled")
        return
    
    try:
        logger.info("Initializing observability infrastructure...")
        
        # Import dependencies only if observability is enabled
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.sdk.resources import Resource, SERVICE_NAME
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            import phoenix as px
            from traceloop.sdk import Traceloop
        except ImportError as e:
            logger.error(f"Failed to import observability dependencies: {str(e)}")
            logger.warning("Continuing without observability...")
            return
        
        # Initialize Phoenix
        logger.info(f"Starting Phoenix on {settings.phoenix_host}:{settings.phoenix_port}")
        try:
            px.launch_app(host=settings.phoenix_host, port=settings.phoenix_port)
        except Exception as e:
            logger.error(f"Failed to launch Phoenix: {str(e)}")
            logger.warning("Continuing without Phoenix UI...")
            # Continue anyway - we can still use OpenTelemetry without Phoenix
        
        # Set up OpenTelemetry resource
        resource = Resource(attributes={
            SERVICE_NAME: settings.app_name,
            "service.version": settings.app_version,
            "deployment.environment": settings.environment,
        })
        
        # Create tracer provider
        tracer_provider = TracerProvider(resource=resource)
        
        # Configure Phoenix as the OTLP endpoint
        phoenix_endpoint = f"{settings.phoenix_collector_endpoint}/v1/traces"
        otlp_exporter = OTLPSpanExporter(endpoint=phoenix_endpoint)
        
        # Add span processor
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)
        
        # Set as global tracer provider
        trace.set_tracer_provider(tracer_provider)
        
        # Initialize Traceloop SDK for automatic LLM instrumentation
        try:
            Traceloop.init(
                app_name=settings.app_name,
                disable_batch=False,
                exporter_endpoint=phoenix_endpoint,
            )
            logger.info("✅ Traceloop SDK initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Traceloop: {str(e)}")
            logger.warning("Continuing without automatic LLM instrumentation...")
        
        logger.info("✅ Observability initialized successfully")
        logger.info(f"📊 Phoenix UI available at: http://{settings.phoenix_host}:{settings.phoenix_port}")
        
    except Exception as e:
        logger.error(f"Failed to initialize observability: {str(e)}", exc_info=True)
        logger.warning("Continuing without observability...")


def shutdown_observability():
    """
    Gracefully shutdown observability infrastructure.
    """
    if not settings.enable_observability:
        return
    
    try:
        logger.info("Shutting down observability...")
        
        try:
            from opentelemetry import trace
            
            # Flush any pending spans
            tracer_provider = trace.get_tracer_provider()
            if hasattr(tracer_provider, 'shutdown'):
                tracer_provider.shutdown()
        except Exception as e:
            logger.error(f"Error flushing traces: {str(e)}")
        
        logger.info("✅ Observability shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during observability shutdown: {str(e)}")
