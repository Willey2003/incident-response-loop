#!/bin/bash
# AegisForge Image Build and Push Script
# Builds all Docker images and pushes to registry

set -euo pipefail

REGISTRY="${REGISTRY:-docker.io}"
ORG="${ORG:-willey2003}"
VERSION="${VERSION:-latest}"
BUILD_ALL="${BUILD_ALL:-true}"

IMAGES=(
    "telemetry-sensor"
    "threat-contextualizer"
    "reconciler-engine"
    "api-gateway"
    "detection-engine"
    "response-orchestrator"
    "ai-copilot"
    "emulation-controller"
    "analyst-console"
    "target-api"
    "auth-simulator"
    "workload-simulator"
    "dns-simulator"
    "traffic-simulator"
)

build_image() {
    local image=$1
    local context=""
    
    case $image in
        "telemetry-sensor")
            context="./cmd/telemetry-sensor"
            ;;
        "threat-contextualizer")
            context="./cmd/threat-contextualizer"
            ;;
        "reconciler-engine")
            context="./cmd/reconciler-engine"
            ;;
        "api-gateway")
            context="./services/api-gateway"
            ;;
        "detection-engine")
            context="./services/detection-engine"
            ;;
        "response-orchestrator")
            context="./services/response-orchestrator"
            ;;
        "ai-copilot")
            context="./services/ai-copilot"
            ;;
        "emulation-controller")
            context="./services/emulation-controller"
            ;;
        "analyst-console")
            context="./web/analyst-console"
            ;;
        "target-api")
            context="./simulators/target-api"
            ;;
        "auth-simulator")
            context="./simulators/auth-simulator"
            ;;
        "workload-simulator")
            context="./simulators/workload-simulator"
            ;;
        "dns-simulator")
            context="./simulators/dns-simulator"
            ;;
        "traffic-simulator")
            context="./simulators/traffic-simulator"
            ;;
        *)
            echo "Unknown image: $image"
            return 1
            ;;
    esac
    
    if [[ ! -d "$context" ]]; then
        echo "Context directory not found: $context"
        return 1
    fi
    
    echo "Building $image from $context..."
    docker build -t "${REGISTRY}/${ORG}/aegisforge-${image}:${VERSION}" \
        -t "${REGISTRY}/${ORG}/aegisforge-${image}:latest" \
        "${context}"
}

push_image() {
    local image=$1
    
    echo "Pushing ${REGISTRY}/${ORG}/aegisforge-${image}:${VERSION}..."
    docker push "${REGISTRY}/${ORG}/aegisforge-${image}:${VERSION}"
    docker push "${REGISTRY}/${ORG}/aegisforge-${image}:latest"
}

main() {
    echo "Building and pushing AegisForge images..."
    echo "Registry: ${REGISTRY}"
    echo "Organization: ${ORG}"
    echo "Version: ${VERSION}"
    echo ""
    
    # Login to registry
    echo "Logging into ${REGISTRY}..."
    docker login "${REGISTRY}"
    
    for image in "${IMAGES[@]}"; do
        if build_image "$image"; then
            push_image "$image"
        else
            echo "Failed to build $image, skipping push"
        fi
    done
    
    echo ""
    echo "All images built and pushed successfully!"
    echo "Images available at:"
    for image in "${IMAGES[@]}"; do
        echo "  ${REGISTRY}/${ORG}/aegisforge-${image}:${VERSION}"
    done
}

main "$@"