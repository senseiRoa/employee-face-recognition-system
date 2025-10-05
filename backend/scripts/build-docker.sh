#!/bin/bash

# Face Recognition System - Docker Build Script
# This script builds the complete system including admin panel and backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="face-recognition-system"
REGISTRY_NAME="steelerp.azurecr.io"
BACKEND_IMAGE="${REGISTRY_NAME}/face_recognition_backend"
DEFAULT_TAG="latest"

print_header() {
    echo -e "${BLUE}"
    echo "========================================================"
    echo "   Face Recognition System - Docker Build Script"
    echo "========================================================"
    echo -e "${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --tag TAG          Tag for the Docker image (default: latest)"
    echo "  -r, --registry REGISTRY Registry name (default: steelerp.azurecr.io)"
    echo "  -p, --push             Push to registry after build"
    echo "  -l, --local-only       Build only for local use (no registry tags)"
    echo "  --no-cache             Build without cache"
    echo "  --platform PLATFORM   Target platform (e.g., linux/amd64,linux/arm64)"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Build with default settings"
    echo "  $0 -t v1.0.0 -p                     # Build and push version 1.0.0"
    echo "  $0 -l                                # Build only for local development"
    echo "  $0 --no-cache                       # Force rebuild without cache"
}

check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi

    print_success "Dependencies check passed"
}

verify_project_structure() {
    print_status "Verifying project structure..."
    
    # Check if we're in the project root
    if [ ! -f "admin-panel/package.json" ]; then
        print_error "admin-panel/package.json not found. Please run this script from the project root directory."
        exit 1
    fi

    if [ ! -f "backend/Dockerfile" ]; then
        print_error "backend/Dockerfile not found. Please run this script from the project root directory."
        exit 1
    fi

    print_success "Project structure verified"
}

build_image() {
    local tag=$1
    local no_cache=$2
    local platform=$3
    
    print_status "Building Docker image..."
    
    # Prepare build arguments
    local build_args=""
    if [ "$no_cache" = "true" ]; then
        build_args="$build_args --no-cache"
    fi
    
    if [ -n "$platform" ]; then
        build_args="$build_args --platform $platform"
    fi

    # Generate timestamp for versioning
    local timestamp=$(date +%Y%m%d-%H%M%S)
    
    # Build command
    local build_cmd="docker build -f backend/Dockerfile"
    build_cmd="$build_cmd -t ${IMAGE_NAME}:${tag}"
    build_cmd="$build_cmd -t ${IMAGE_NAME}:${timestamp}"
    
    if [ "$LOCAL_ONLY" != "true" ]; then
        build_cmd="$build_cmd -t ${BACKEND_IMAGE}:${tag}"
        build_cmd="$build_cmd -t ${BACKEND_IMAGE}:${timestamp}"
    fi
    
    build_cmd="$build_cmd $build_args ."
    
    print_status "Executing: $build_cmd"
    eval $build_cmd
    
    if [ $? -eq 0 ]; then
        print_success "Image built successfully!"
        print_status "Tags created:"
        echo "  • ${IMAGE_NAME}:${tag}"
        echo "  • ${IMAGE_NAME}:${timestamp}"
        if [ "$LOCAL_ONLY" != "true" ]; then
            echo "  • ${BACKEND_IMAGE}:${tag}"
            echo "  • ${BACKEND_IMAGE}:${timestamp}"
        fi
    else
        print_error "Build failed!"
        exit 1
    fi
}

push_image() {
    local tag=$1
    
    if [ "$LOCAL_ONLY" = "true" ]; then
        print_warning "Skipping push (local-only mode)"
        return
    fi
    
    print_status "Pushing image to registry..."
    
    # Check if logged in to registry
    if [[ "$REGISTRY_NAME" == *"azurecr.io"* ]]; then
        print_status "Checking Azure Container Registry login..."
        if ! az acr check-name --name $(echo $REGISTRY_NAME | cut -d'.' -f1) &> /dev/null; then
            print_warning "Please ensure you're logged in to Azure: az acr login --name $(echo $REGISTRY_NAME | cut -d'.' -f1)"
        fi
    fi
    
    docker push ${BACKEND_IMAGE}:${tag}
    
    if [ $? -eq 0 ]; then
        print_success "Image pushed successfully!"
        print_status "Image available at: ${BACKEND_IMAGE}:${tag}"
    else
        print_error "Push failed!"
        exit 1
    fi
}

get_image_info() {
    local tag=$1
    
    print_status "Image information:"
    
    # Get image size
    local size=$(docker image inspect ${IMAGE_NAME}:${tag} --format='{{.Size}}' 2>/dev/null || echo "Unknown")
    if [ "$size" != "Unknown" ]; then
        size=$(echo "scale=2; $size / 1024 / 1024" | bc)
        echo "  • Size: ${size} MB"
    fi
    
    # Get creation date
    local created=$(docker image inspect ${IMAGE_NAME}:${tag} --format='{{.Created}}' 2>/dev/null || echo "Unknown")
    echo "  • Created: $created"
    
    # Show how to run
    echo ""
    print_status "To run the container:"
    echo "  docker run -d --name face-recognition-app -p 8081:8081 ${IMAGE_NAME}:${tag}"
    echo ""
    print_status "To access the application:"
    echo "  • API Documentation: http://localhost:8081/docs"
    echo "  • Admin Panel: http://localhost:8081/admin/"
    echo "  • Health Check: http://localhost:8081/health"
}

cleanup_old_images() {
    print_status "Cleaning up old images..."
    
    # Remove dangling images
    docker image prune -f &> /dev/null || true
    
    print_success "Cleanup completed"
}

# Main script logic
print_header

# Parse command line arguments
TAG="$DEFAULT_TAG"
REGISTRY_NAME="steelerp.azurecr.io"
PUSH_IMAGE=false
LOCAL_ONLY=false
NO_CACHE=false
PLATFORM=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY_NAME="$2"
            BACKEND_IMAGE="${REGISTRY_NAME}/face_recognition_backend"
            shift 2
            ;;
        -p|--push)
            PUSH_IMAGE=true
            shift
            ;;
        -l|--local-only)
            LOCAL_ONLY=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Update backend image name if registry changed
BACKEND_IMAGE="${REGISTRY_NAME}/face_recognition_backend"

# Execute build process
check_dependencies
verify_project_structure

print_status "Configuration:"
echo "  • Tag: $TAG"
echo "  • Registry: $REGISTRY_NAME"
echo "  • Push to registry: $PUSH_IMAGE"
echo "  • Local only: $LOCAL_ONLY"
echo "  • No cache: $NO_CACHE"
if [ -n "$PLATFORM" ]; then
    echo "  • Platform: $PLATFORM"
fi
echo ""

build_image "$TAG" "$NO_CACHE" "$PLATFORM"

if [ "$PUSH_IMAGE" = "true" ]; then
    push_image "$TAG"
fi

get_image_info "$TAG"
cleanup_old_images

print_success "Build process completed successfully!"
print_status "Next steps:"
echo "  1. Test the image locally: docker run -p 8081:8081 ${IMAGE_NAME}:${TAG}"
echo "  2. Deploy to your environment"
echo "  3. Configure environment variables for production"

if [ "$LOCAL_ONLY" != "true" ] && [ "$PUSH_IMAGE" != "true" ]; then
    echo ""
    print_status "To push to registry later:"
    echo "  docker push ${BACKEND_IMAGE}:${TAG}"
fi