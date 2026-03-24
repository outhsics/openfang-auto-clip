#!/usr/bin/env python3
"""
OpenFang Auto Clip Web Manager v2

Enhanced web interface with AIGC and Agent Skills integration.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.web_runtime import TaskStore, start_background_task
from src.aigc import ImageGenerator, VideoGenerator, get_provider
from src.agent_skills import SkillExecutor, Agent, create_video_processing_workflow

app = Flask(__name__)
CORS(app)

# Configuration
PROJECT_DIR = PROJECT_ROOT
OUTPUT_DIR = Path.home() / ".openfang" / "clips"
CONFIG_FILE = Path.home() / ".openfang" / "auto_clip_config.json"

# Initialize components
TASK_STORE = TaskStore()
skill_executor = SkillExecutor(workspace=OUTPUT_DIR)


def load_config() -> dict:
    """Load configuration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    """Save configuration"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


# ============================================================================
# API Routes - System
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('manager_v2.html')


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/status')
def get_status():
    """Get system status"""
    config = load_config()

    # Count output files
    clips_count = 0
    aigc_images = 0
    aigc_videos = 0

    if OUTPUT_DIR.exists():
        clips_count = len(list(OUTPUT_DIR.glob("**/*.mp4")))
        aigc_dir = OUTPUT_DIR.parent / "aigc"
        if aigc_dir.exists():
            images_dir = aigc_dir / "images"
            videos_dir = aigc_dir / "videos"
            aigc_images = len(list(images_dir.glob("**/*.png"))) if images_dir.exists() else 0
            aigc_videos = len(list(videos_dir.glob("**/*.mp4"))) if videos_dir.exists() else 0

    return jsonify({
        'project_dir': str(PROJECT_DIR),
        'output_dir': str(OUTPUT_DIR),
        'python_version': sys.version.split()[0],
        'tasks': TASK_STORE.all(),
        'stats': {
            'clips_generated': clips_count,
            'aigc_images': aigc_images,
            'aigc_videos': aigc_videos
        },
        'config': config
    })


# ============================================================================
# API Routes - Video Processing
# ============================================================================

@app.route('/api/video/download', methods=['POST'])
def video_download():
    """Download video from URL"""
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        from src.video_sources import get_video_source

        source = get_video_source(url)
        output_path = source.download(output_dir=str(OUTPUT_DIR / "downloads"))

        return jsonify({
            'success': True,
            'video_path': str(output_path),
            'source': source.__class__.__name__
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/transform', methods=['POST'])
def video_transform():
    """Transform video with copyright protection"""
    data = request.json
    input_path = data.get('input_path')
    preset = data.get('preset', 'default')

    if not input_path:
        return jsonify({'error': 'input_path is required'}), 400

    try:
        from src.transform_effects import apply_preset

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / "transformed" / f"transformed_{timestamp}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        success = apply_preset(
            input_path=input_path,
            output_path=str(output_path),
            preset_name=preset
        )

        if success:
            return jsonify({
                'success': True,
                'output_path': str(output_path),
                'preset': preset
            })
        else:
            return jsonify({'error': 'Transform failed'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/process', methods=['POST'])
def video_process():
    """Process video with full pipeline"""
    data = request.json
    url = data.get('url')
    transform_level = data.get('transform_level', 1)
    duration = data.get('duration', 60)

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    task_id = start_background_task(
        "video_process",
        [sys.executable, "auto_clip.py", url,
         "--transform", str(transform_level),
         "--duration", str(duration)],
        TASK_STORE,
        metadata={"url": url, "transform_level": transform_level},
        cwd=PROJECT_DIR
    )

    return jsonify({
        'task_id': task_id,
        'message': 'Video processing task started'
    })


# ============================================================================
# API Routes - AIGC
# ============================================================================

@app.route('/api/aigc/providers')
def list_aigc_providers():
    """List available AIGC providers"""
    providers = [
        {'id': 'stable_diffusion', 'name': 'Stable Diffusion', 'type': 'local', 'status': 'available'},
        {'id': 'openai_dalle', 'name': 'OpenAI DALL-E', 'type': 'api', 'status': 'requires_key'},
        {'id': 'replicate', 'name': 'Replicate', 'type': 'api', 'status': 'requires_key'},
        {'id': 'comfyui', 'name': 'ComfyUI', 'type': 'local', 'status': 'available'},
    ]

    return jsonify({'providers': providers})


@app.route('/api/aigc/styles')
def list_aigc_styles():
    """List available AIGC styles"""
    image_styles = [
        {'id': 'realistic', 'name': 'Realistic', 'category': 'image'},
        {'id': 'cinematic', 'name': 'Cinematic', 'category': 'image'},
        {'id': 'anime', 'name': 'Anime', 'category': 'image'},
        {'id': 'cyberpunk', 'name': 'Cyberpunk', 'category': 'image'},
        {'id': 'vintage', 'name': 'Vintage', 'category': 'image'},
    ]

    video_styles = [
        {'id': 'cinematic', 'name': 'Cinematic', 'category': 'video'},
        {'id': 'loop', 'name': 'Looping', 'category': 'video'},
        {'id': 'timelapse', 'name': 'Timelapse', 'category': 'video'},
    ]

    return jsonify({
        'image_styles': image_styles,
        'video_styles': video_styles
    })


@app.route('/api/aigc/image/generate', methods=['POST'])
def aigc_generate_image():
    """Generate AI image"""
    data = request.json
    prompt = data.get('prompt')
    provider = data.get('provider', 'stable_diffusion')
    style = data.get('style')
    width = data.get('width', 1024)
    height = data.get('height', 1024)
    variations = data.get('variations', 1)

    if not prompt:
        return jsonify({'error': 'prompt is required'}), 400

    try:
        ai_provider = get_provider(provider)
        generator = ImageGenerator(provider=ai_provider)

        # Convert style
        from src.aigc import ImageStyle
        image_style = None
        if style:
            try:
                image_style = ImageStyle(style)
            except ValueError:
                pass

        if variations > 1:
            results = generator.generate_variations(
                base_prompt=prompt,
                num_variations=variations,
                width=width,
                height=height,
                style=image_style
            )

            successful = [r for r in results if r.get("success")]
            return jsonify({
                'success': len(successful) > 0,
                'generated': len(successful),
                'total': variations,
                'images': [r.get("save_path") for r in successful]
            })
        else:
            result = generator.generate(
                prompt=prompt,
                style=image_style,
                width=width,
                height=height
            )

            return jsonify({
                'success': result.get("success", False),
                'image_path': result.get("save_path"),
                'error': result.get("error")
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/aigc/video/generate', methods=['POST'])
def aigc_generate_video():
    """Generate AI video"""
    data = request.json
    prompt = data.get('prompt')
    provider = data.get('provider', 'stable_diffusion')
    duration = data.get('duration', 4.0)
    width = data.get('width', 1024)
    height = data.get('height', 1024)

    if not prompt:
        return jsonify({'error': 'prompt is required'}), 400

    try:
        ai_provider = get_provider(provider)
        generator = VideoGenerator(provider=ai_provider)

        result = generator.generate(
            prompt=prompt,
            duration=duration,
            width=width,
            height=height
        )

        return jsonify({
            'success': result.get("success", False),
            'video_path': result.get("save_path"),
            'error': result.get("error")
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API Routes - Agent Skills
# ============================================================================

@app.route('/api/skills')
def list_skills():
    """List available skills"""
    from src.agent_skills import SkillRegistry

    schemas = SkillRegistry.get_all_schemas()

    skills = []
    for name, schema in schemas.items():
        skills.append({
            'name': name,
            'description': schema.get('description', ''),
            'parameters': schema.get('parameters', {}),
            'version': schema.get('version', '1.0.0')
        })

    return jsonify({'skills': skills})


@app.route('/api/skills/execute', methods=['POST'])
def execute_skill():
    """Execute a skill"""
    data = request.json
    skill_name = data.get('skill')
    params = data.get('params', {})

    if not skill_name:
        return jsonify({'error': 'skill is required'}), 400

    try:
        result = skill_executor.execute(skill_name, params)

        return jsonify({
            'success': result.success,
            'status': result.status.value,
            'data': result.data,
            'error': result.error,
            'execution_time': result.execution_time
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/workflows')
def list_workflows():
    """List available workflows"""
    from src.agent_skills import (
        create_video_processing_workflow,
        create_aigc_content_workflow,
        create_full_pipeline_workflow
    )

    workflows = [
        {
            'id': 'video_processing',
            'name': 'Video Processing',
            'description': 'Download, transform, and extract clips'
        },
        {
            'id': 'aigc_content',
            'name': 'AIGC Content',
            'description': 'Generate AI images and videos'
        },
        {
            'id': 'full_pipeline',
            'name': 'Full Pipeline',
            'description': 'Complete video creation pipeline'
        }
    ]

    return jsonify({'workflows': workflows})


@app.route('/api/workflows/execute', methods=['POST'])
def execute_workflow():
    """Execute a workflow"""
    data = request.json
    workflow_name = data.get('workflow')
    variables = data.get('variables', {})

    if not workflow_name:
        return jsonify({'error': 'workflow is required'}), 400

    try:
        from src.agent_skills import (
            create_video_processing_workflow,
            create_aigc_content_workflow,
            create_full_pipeline_workflow
        )

        # Register workflows
        from src.agent_skills import WorkflowExecutor
        executor = WorkflowExecutor(workspace=OUTPUT_DIR)

        if workflow_name == 'video_processing':
            executor.register_workflow(create_video_processing_workflow())
        elif workflow_name == 'aigc_content':
            executor.register_workflow(create_aigc_content_workflow())
        elif workflow_name == 'full_pipeline':
            executor.register_workflow(create_full_pipeline_workflow())
        else:
            return jsonify({'error': f'Unknown workflow: {workflow_name}'}), 400

        results = executor.execute_workflow(workflow_name, variables)

        return jsonify({
            'success': True,
            'workflow': workflow_name,
            'results': [r.to_dict() for r in results]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API Routes - Tasks
# ============================================================================

@app.route('/api/tasks')
def list_tasks():
    """List all tasks"""
    tasks = TASK_STORE.all()
    return jsonify({'tasks': tasks})


@app.route('/api/tasks/<task_id>')
def get_task(task_id: str):
    """Get task details"""
    task = TASK_STORE.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task)


@app.route('/api/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id: str):
    """Cancel a task"""
    # Implementation depends on task store
    return jsonify({'message': f'Task {task_id} cancel requested'})


# ============================================================================
# API Routes - Configuration
# ============================================================================

@app.route('/api/config')
def get_config():
    """Get configuration"""
    config = load_config()
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    data = request.json
    config = load_config()
    config.update(data)
    save_config(config)
    return jsonify({'message': 'Configuration updated'})


# ============================================================================
# Static Files
# ============================================================================

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    static_dir = PROJECT_DIR / "templates" / "static"
    return send_from_directory(static_dir, filename)


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# Main
# ============================================================================

def run_server(host='127.0.0.1', port=5000, debug=True):
    """Run the web server"""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   OpenFang Auto Clip - Web Manager v2.0                  ║
║                                                          ║
║   Access at: http://{host}:{port}                  ║
║                                                          ║
║   Features:                                              ║
║   • Video Processing                                     ║
║   • AIGC Integration                                     ║
║   • Agent Skills System                                  ║
║   • Task Management                                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='OpenFang Auto Clip Web Manager')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    run_server(host=args.host, port=args.port, debug=args.debug)
