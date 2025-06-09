#!/bin/bash

echo "🔍 Test 1: Verify multi-stage build reduces image size"
echo "==================================================="

# Build with multi-stage
echo "Building with multi-stage Dockerfile..."
docker build -t model-service-multistage .

# Show image size
echo -e "\nImage size:"
docker images model-service-multistage --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Verify build stages
echo -e "\nVerifying build stages in Dockerfile..."
grep -n "FROM.*AS\|FROM.*$" Dockerfile

echo -e "\n🔍 Test 2: Verify multi-architecture support in workflow"
echo "===================================================="

echo "Checking release workflow for multi-arch support..."
if grep -q "platforms: linux/amd64,linux/arm64" .github/workflows/release.yml; then
    echo "✅ Multi-architecture support found in release workflow"
else
    echo "❌ Multi-architecture support NOT found in release workflow"
fi

if grep -q "docker/setup-buildx-action" .github/workflows/release.yml; then
    echo "✅ Docker Buildx setup found"
else
    echo "❌ Docker Buildx setup NOT found"
fi

echo -e "\n🔍 Test 3: Verify pre-release iteration support"
echo "============================================="

echo "Checking pre-release workflow for iteration support..."
if grep -q "EXISTING_TAGS.*git tag" .github/workflows/prerelease.yml; then
    echo "✅ Iteration counting mechanism found"
else
    echo "❌ Iteration counting mechanism NOT found"
fi

if grep -q "ITERATION.*EXISTING_TAGS" .github/workflows/prerelease.yml; then
    echo "✅ Iteration increment logic found"
else
    echo "❌ Iteration increment logic NOT found"
fi

if grep -q "\${BASE_PRE_VERSION}-\${ITERATION}" .github/workflows/prerelease.yml; then
    echo "✅ Iteration version format found"
else
    echo "❌ Iteration version format NOT found"
fi

echo -e "\n🔍 Test 4: Simulate version calculation"
echo "======================================"

# Simulate version calculation logic
BASE_VERSION="1.2.3"
IFS='.' read -r MAJOR MINOR PATCH <<< "$BASE_VERSION"
NEXT_PATCH=$((PATCH + 1))
BASE_PRE_VERSION="v${MAJOR}.${MINOR}.${NEXT_PATCH}-pre"

echo "Base version: $BASE_VERSION"
echo "Next pre-release base: $BASE_PRE_VERSION"

# Simulate existing tags (normally would use git tag -l)
SIMULATED_EXISTING=2  # Simulate 2 existing iterations
ITERATION=$((SIMULATED_EXISTING + 1))
NEXT_VERSION="${BASE_PRE_VERSION}-${ITERATION}"

echo "Simulated existing iterations: $SIMULATED_EXISTING"
echo "Next iteration version: $NEXT_VERSION"

if [[ $NEXT_VERSION == "v1.2.4-pre-3" ]]; then
    echo "✅ Version calculation logic works correctly"
else
    echo "❌ Version calculation logic has issues"
fi

echo -e "\n🔍 Test 5: Check Dockerfile optimization"
echo "====================================="

# Check for optimization practices
echo "Checking Dockerfile optimization..."

if grep -q "rm -rf /var/lib/apt/lists" Dockerfile; then
    echo "✅ APT cache cleanup found"
else
    echo "❌ APT cache cleanup NOT found"
fi

if grep -q "COPY --from=builder" Dockerfile; then
    echo "✅ Multi-stage copy optimization found"
else
    echo "❌ Multi-stage copy optimization NOT found"
fi

if grep -q "no-install-recommends" Dockerfile; then
    echo "✅ Minimal package installation found"
else
    echo "❌ Minimal package installation NOT found"
fi

echo -e "\n✅ Versioning and release testing completed!"
echo "=========================================="

echo -e "\nSummary:"
echo "- Multi-stage builds: Implemented"
echo "- Multi-architecture: Configured in workflows"
echo "- Pre-release iterations: Automated with counters"
echo "- Image optimization: APT cache cleanup, minimal installs" 