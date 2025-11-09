import os
import json

from contextlib import asynccontextmanager
import click
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from multimodal_api.router.root import router_root
from multimodal_api.router.process_video import router_video_processor
from multimodal_api.router.task_status import router_task_status
from multimodal_api.router.serve_media import router_serve_media
from multimodal_api.router.chat import router_chat
from multimodal_api.router.upload_image import router_upload_image
from multimodal_api.router.upload_video import router_upload_video
from multimodal_api.router.media_files import router_media_files

from multimodal_api.agent.graph import AIAgent
from multimodal_api.agent.mcp_client import get_mcp_client

from multimodal_api.config.config import get_settings

settings = get_settings()

# intial db variable
db = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialize the AI Agent
    app.state.agent = AIAgent()

    # Initialize the MCP Client
    app.state.mcp_client = get_mcp_client()

    # Initialize shared background task state
    app.state.bg_task_states = {}

    # Initialize Backend db

    yield


# Create FastAPI app
app = FastAPI(
    title="Multimodal API",
    description="Multimodal API",
    docs_url="/docs",
    lifespan=lifespan,
)

# Add routers
app.include_router(router_root)
app.include_router(router_video_processor)
app.include_router(router_task_status)
app.include_router(router_chat)
app.include_router(router_serve_media)
app.include_router(router_upload_image)
app.include_router(router_upload_video)
app.include_router(router_media_files)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for media serving
# app.mount("/media", StaticFiles(directory=f"{settings.SHARED_MEDIA_DIR}"), name="media")


@click.command()
@click.option("--port", default=8080, help="FastAPI server port")
@click.option("--host", default="0.0.0.0", help="FastAPI server host")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def run_api(port, host, reload):
    import uvicorn

    uvicorn.run(
        "multimodal_api.api:app", host=host, port=port, reload=reload, loop="asyncio"
    )


if __name__ == "__main__":
    run_api()
