@echo off
REM Face Recognition System - Docker Build Script for Windows
REM This script builds the complete system including admin panel and backend

setlocal enabledelayedexpansion

REM Colors for output
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Configuration
set "IMAGE_NAME=face-recognition-system"
set "REGISTRY_NAME=steelerp.azurecr.io"
set "BACKEND_IMAGE=%REGISTRY_NAME%/face_recognition_backend"
set "DEFAULT_TAG=latest"
set "TAG=%DEFAULT_TAG%"
set "PUSH_IMAGE=false"
set "LOCAL_ONLY=false"
set "NO_CACHE=false"
set "PLATFORM="

:print_header
echo %BLUE%
echo ========================================================
echo    Face Recognition System - Docker Build Script
echo ========================================================
echo %NC%
goto :eof

:print_status
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

:print_usage
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   -t, --tag TAG          Tag for the Docker image (default: latest)
echo   -r, --registry REGISTRY Registry name (default: steelerp.azurecr.io)
echo   -p, --push             Push to registry after build
echo   -l, --local-only       Build only for local use (no registry tags)
echo   --no-cache             Build without cache
echo   --platform PLATFORM   Target platform (e.g., linux/amd64,linux/arm64)
echo   -h, --help             Show this help message
echo.
echo Examples:
echo   %~nx0                                    # Build with default settings
echo   %~nx0 -t v1.0.0 -p                     # Build and push version 1.0.0
echo   %~nx0 -l                                # Build only for local development
echo   %~nx0 --no-cache                       # Force rebuild without cache
goto :eof

:check_dependencies
call :print_status "Checking dependencies..."

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Docker is not installed or not in PATH"
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Docker daemon is not running"
    exit /b 1
)

call :print_success "Dependencies check passed"
goto :eof

:verify_project_structure
call :print_status "Verifying project structure..."

if not exist "admin-panel\package.json" (
    call :print_error "admin-panel\package.json not found. Please run this script from the project root directory."
    exit /b 1
)

if not exist "backend\Dockerfile" (
    call :print_error "backend\Dockerfile not found. Please run this script from the project root directory."
    exit /b 1
)

call :print_success "Project structure verified"
goto :eof

:build_image
set "build_tag=%~1"
set "no_cache_flag=%~2"
set "platform_flag=%~3"

call :print_status "Building Docker image..."

REM Prepare build arguments
set "build_args="
if "%no_cache_flag%"=="true" (
    set "build_args=!build_args! --no-cache"
)

if not "%platform_flag%"=="" (
    set "build_args=!build_args! --platform %platform_flag%"
)

REM Generate timestamp for versioning
for /f "tokens=2 delims==" %%I in ('wmic OS Get localdatetime /value') do set "dt=%%I"
set "timestamp=%dt:~0,8%-%dt:~8,6%"

REM Build command
set "build_cmd=docker build -f backend\Dockerfile"
set "build_cmd=!build_cmd! -t %IMAGE_NAME%:!build_tag!"
set "build_cmd=!build_cmd! -t %IMAGE_NAME%:!timestamp!"

if not "%LOCAL_ONLY%"=="true" (
    set "build_cmd=!build_cmd! -t %BACKEND_IMAGE%:!build_tag!"
    set "build_cmd=!build_cmd! -t %BACKEND_IMAGE%:!timestamp!"
)

set "build_cmd=!build_cmd! !build_args! ."

call :print_status "Executing: !build_cmd!"
%build_cmd%

if %errorlevel% equ 0 (
    call :print_success "Image built successfully!"
    call :print_status "Tags created:"
    echo   • %IMAGE_NAME%:!build_tag!
    echo   • %IMAGE_NAME%:!timestamp!
    if not "%LOCAL_ONLY%"=="true" (
        echo   • %BACKEND_IMAGE%:!build_tag!
        echo   • %BACKEND_IMAGE%:!timestamp!
    )
) else (
    call :print_error "Build failed!"
    exit /b 1
)
goto :eof

:push_image
set "push_tag=%~1"

if "%LOCAL_ONLY%"=="true" (
    call :print_warning "Skipping push (local-only mode)"
    goto :eof
)

call :print_status "Pushing image to registry..."

REM Check if registry is Azure Container Registry
echo %REGISTRY_NAME% | findstr "azurecr.io" >nul
if %errorlevel% equ 0 (
    call :print_status "Detected Azure Container Registry"
    call :print_warning "Please ensure you're logged in to Azure: az acr login --name steelerp"
)

docker push %BACKEND_IMAGE%:!push_tag!

if %errorlevel% equ 0 (
    call :print_success "Image pushed successfully!"
    call :print_status "Image available at: %BACKEND_IMAGE%:!push_tag!"
) else (
    call :print_error "Push failed!"
    exit /b 1
)
goto :eof

:get_image_info
set "info_tag=%~1"

call :print_status "Image information:"

REM Get image size
for /f "delims=" %%i in ('docker image inspect %IMAGE_NAME%:!info_tag! --format="{{.Size}}" 2^>nul') do set "size=%%i"
if defined size (
    set /a "size_mb=!size! / 1024 / 1024"
    echo   • Size: !size_mb! MB
)

REM Get creation date
for /f "delims=" %%i in ('docker image inspect %IMAGE_NAME%:!info_tag! --format="{{.Created}}" 2^>nul') do set "created=%%i"
if defined created (
    echo   • Created: !created!
)

echo.
call :print_status "To run the container:"
echo   docker run -d --name face-recognition-app -p 8081:8081 %IMAGE_NAME%:!info_tag!
echo.
call :print_status "To access the application:"
echo   • API Documentation: http://localhost:8081/docs
echo   • Admin Panel: http://localhost:8081/admin/
echo   • Health Check: http://localhost:8081/health
goto :eof

:cleanup_old_images
call :print_status "Cleaning up old images..."
docker image prune -f >nul 2>&1
call :print_success "Cleanup completed"
goto :eof

:parse_args
if "%~1"=="" goto :done_parsing
if "%~1"=="-t" (
    set "TAG=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--tag" (
    set "TAG=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-r" (
    set "REGISTRY_NAME=%~2"
    set "BACKEND_IMAGE=!REGISTRY_NAME!/face_recognition_backend"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--registry" (
    set "REGISTRY_NAME=%~2"
    set "BACKEND_IMAGE=!REGISTRY_NAME!/face_recognition_backend"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-p" (
    set "PUSH_IMAGE=true"
    shift
    goto :parse_args
)
if "%~1"=="--push" (
    set "PUSH_IMAGE=true"
    shift
    goto :parse_args
)
if "%~1"=="-l" (
    set "LOCAL_ONLY=true"
    shift
    goto :parse_args
)
if "%~1"=="--local-only" (
    set "LOCAL_ONLY=true"
    shift
    goto :parse_args
)
if "%~1"=="--no-cache" (
    set "NO_CACHE=true"
    shift
    goto :parse_args
)
if "%~1"=="--platform" (
    set "PLATFORM=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-h" (
    call :print_usage
    exit /b 0
)
if "%~1"=="--help" (
    call :print_usage
    exit /b 0
)
call :print_error "Unknown option: %~1"
call :print_usage
exit /b 1

:done_parsing
goto :eof

REM Main script logic
call :print_header

REM Parse command line arguments
call :parse_args %*

REM Update backend image name if registry changed
set "BACKEND_IMAGE=%REGISTRY_NAME%/face_recognition_backend"

REM Execute build process
call :check_dependencies
call :verify_project_structure

call :print_status "Configuration:"
echo   • Tag: %TAG%
echo   • Registry: %REGISTRY_NAME%
echo   • Push to registry: %PUSH_IMAGE%
echo   • Local only: %LOCAL_ONLY%
echo   • No cache: %NO_CACHE%
if not "%PLATFORM%"=="" (
    echo   • Platform: %PLATFORM%
)
echo.

call :build_image "%TAG%" "%NO_CACHE%" "%PLATFORM%"

if "%PUSH_IMAGE%"=="true" (
    call :push_image "%TAG%"
)

call :get_image_info "%TAG%"
call :cleanup_old_images

call :print_success "Build process completed successfully!"
call :print_status "Next steps:"
echo   1. Test the image locally: docker run -p 8081:8081 %IMAGE_NAME%:%TAG%
echo   2. Deploy to your environment
echo   3. Configure environment variables for production

if not "%LOCAL_ONLY%"=="true" if not "%PUSH_IMAGE%"=="true" (
    echo.
    call :print_status "To push to registry later:"
    echo   docker push %BACKEND_IMAGE%:%TAG%
)

pause