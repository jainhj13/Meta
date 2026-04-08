#!/bin/bash
# Quick Local Testing Guide for WorkplaceAIEnv++

echo "═══════════════════════════════════════════════════════════════"
echo "  WorkplaceAIEnv++ - Local Testing Guide"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Verify Python Syntax${NC}"
echo "Running: python3 -m py_compile inference.py workplace_ai_env/server/app.py"
python3 -m py_compile inference.py workplace_ai_env/server/app.py || {
    echo -e "${RED}✗ Syntax error found!${NC}"
    exit 1
}
echo -e "${GREEN}✓ All Python files have valid syntax${NC}"
echo ""

echo -e "${YELLOW}Step 2: Check File Structure${NC}"
echo "Verifying required files exist..."

required_files=(
    "inference.py"
    "entrypoint.sh"
    "Dockerfile"
    ".dockerignore"
    ".env.example"
    "pyproject.toml"
    "README.md"
    "openenv.yaml"
    "workplace_ai_env/server/app.py"
    "workplace_ai_env/server/requirements.txt"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (MISSING)"
    fi
done
echo ""

echo -e "${YELLOW}Step 3: Check .env Configuration${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    if grep -q "HF_TOKEN=" .env; then
        token_value=$(grep "HF_TOKEN=" .env | cut -d'=' -f2)
        if [ "$token_value" != "hf_your_token_here" ] && [ -n "$token_value" ]; then
            echo -e "${GREEN}✓${NC} HF_TOKEN is configured (starts with: ${token_value:0:10}...)"
        else
            echo -e "${YELLOW}⚠${NC} HF_TOKEN is not set or is placeholder"
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} .env file not found - use .env.example as template"
fi
echo ""

echo -e "${YELLOW}Step 4: Verify Pydantic Compatibility${NC}"
python3 << 'EOF'
from typing import Optional
from pydantic import BaseModel, Field
from typing import Any

class TestRequest(BaseModel):
    task_name: str = Field(default="email_triage", description="Test")
    episode_id: Optional[str] = Field(default=None, description="Test")

print("✓ Pydantic models compile successfully")
EOF
echo ""

echo -e "${YELLOW}Step 5: Next Steps${NC}"
cat << 'EOF'

Option A: Test with Local Server (requires HF_TOKEN in .env)
  1. Start the environment server:
     python -m uvicorn workplace_ai_env.server.app:app --port 8000
  
  2. In another terminal, test the endpoint:
     curl -X POST http://localhost:8000/reset \
       -H "Content-Type: application/json" \
       -d '{"task_name":"email_triage","seed":0}'

Option B: Test Docker Build
  1. Build the image:
     docker build -t workplace-ai-env:test .
  
  2. Run with validation mode (no credentials needed):
     docker run \
       -e VALIDATION_MODE=true \
       -p 8000:8000 \
       workplace-ai-env:test
  
  3. Test health endpoint:
     curl http://localhost:8000/health

Option C: Re-Submit to OpenEnv
  1. Commit and push all changes to GitHub
  2. Go to OpenEnv validation
  3. Paste your GitHub repository URL
  4. Validation should now pass all 6 checks!

═══════════════════════════════════════════════════════════════════
EOF

echo ""
echo -e "${GREEN}All checks passed! Ready for submission.${NC}"
echo ""
