#!/bin/bash
# AI Tutor Orchestrator - Demo Commands
# Run these commands in order to demonstrate the system locally

echo "=== AI TUTOR ORCHESTRATOR DEMO SETUP ==="
echo ""

# Step 1: Start the services
echo "Step 1: Starting Docker services..."
echo "Command: docker-compose up -d"
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "=== DEMO SCENARIOS ==="
echo ""

# Scenario 1: Flashcard Generator
echo "Scenario 1: Flashcard Generator"
echo "User says: 'I'm struggling with calculus derivatives and need some practice problems'"
echo ""
echo "Curl command:"
echo "curl -X POST http://localhost:8000/orchestrate \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"message\": \"I'm struggling with calculus derivatives and need some practice problems\"}'"

echo ""
echo "Running command..."
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"message": "I'\''m struggling with calculus derivatives and need some practice problems"}' \
  | python -m json.tool

echo ""
echo "Expected: Routes to flashcard_generator with difficulty=easy, num_cards=5"
echo ""
echo "Press Enter to continue to next scenario..."
read -r

# Scenario 2: Note Maker  
echo "Scenario 2: Note Maker"
echo "User says: 'Make notes on the water cycle in an outline format — include analogies'"
echo ""
echo "Curl command:"
echo "curl -X POST http://localhost:8000/orchestrate \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"message\": \"Make notes on the water cycle in an outline format — include analogies\"}'"

echo ""
echo "Running command..."
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"message": "Make notes on the water cycle in an outline format — include analogies"}' \
  | python -m json.tool

echo ""
echo "Expected: Routes to note_maker with note_style=outline, includes examples"
echo ""
echo "Press Enter to continue to next scenario..."
read -r

# Scenario 3: Concept Explainer
echo "Scenario 3: Concept Explainer"
echo "User says: 'Explain photosynthesis at an intermediate level. Give 2 practice questions.'"
echo ""
echo "Curl command:"
echo "curl -X POST http://localhost:8000/orchestrate \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"message\": \"Explain photosynthesis at an intermediate level. Give 2 practice questions.\"}'"

echo ""
echo "Running command..."
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain photosynthesis at an intermediate level. Give 2 practice questions."}' \
  | python -m json.tool

echo ""
echo "Expected: Routes to concept_explainer with prior_knowledge=intermediate, include_quiz=true"
echo ""

# Health check
echo "=== HEALTH CHECK ==="
echo "Checking system health..."
curl -X GET http://localhost:8000/health | python -m json.tool

echo ""
echo "=== ADDITIONAL DEMO COMMANDS ==="
echo ""

# Show available tools
echo "Get available tools:"
echo "curl -X GET http://localhost:8000/tools"
curl -X GET http://localhost:8000/tools | python -m json.tool

echo ""

# Show tool schemas
echo "Get tool schemas:"
echo "curl -X GET http://localhost:8000/tools/schemas"
curl -X GET http://localhost:8000/tools/schemas | python -m json.tool

echo ""

# Test parameter extraction directly
echo "Test parameter extraction (flashcards):"
echo "curl -X POST http://localhost:8000/extract \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"message\": \"Quiz me on physics\", \"tool\": \"flashcard_generator\"}'"

curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"message": "Quiz me on physics", "tool": "flashcard_generator"}' \
  | python -m json.tool

echo ""

# Demo cleanup
echo "=== CLEANUP (Optional) ==="
echo "To stop services:"
echo "docker-compose down"
echo ""
echo "Demo complete! 🎉"

# PowerShell version for Windows
echo ""
echo "=== POWERSHELL COMMANDS (Windows) ==="
echo ""
echo "# Start services"
echo "docker-compose up -d"
echo ""
echo "# Scenario 1 (PowerShell)"
echo "Invoke-RestMethod -Uri 'http://localhost:8000/orchestrate' -Method POST -ContentType 'application/json' -Body '{\"message\": \"I am struggling with calculus derivatives and need some practice problems\"}'"
echo ""
echo "# Scenario 2 (PowerShell)" 
echo "Invoke-RestMethod -Uri 'http://localhost:8000/orchestrate' -Method POST -ContentType 'application/json' -Body '{\"message\": \"Make notes on the water cycle in an outline format — include analogies\"}'"
echo ""
echo "# Scenario 3 (PowerShell)"
echo "Invoke-RestMethod -Uri 'http://localhost:8000/orchestrate' -Method POST -ContentType 'application/json' -Body '{\"message\": \"Explain photosynthesis at an intermediate level. Give 2 practice questions.\"}'"