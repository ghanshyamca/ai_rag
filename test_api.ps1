# PowerShell test script for RAG Q&A Bot API

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   RAG Q&A Bot API - PowerShell Test Suite    ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"

# Function to print separator
function Print-Separator {
    Write-Host "`n$('='*70)`n" -ForegroundColor Gray
}

# Function to print response
function Print-Response {
    param($response)
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Yellow
    Write-Host ($response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10)
}

# Test 1: Root endpoint
Print-Separator
Write-Host "Test 1: GET /" -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/" -Method Get -UseBasicParsing
    Print-Response $response
    Write-Host "✅ PASSED" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

# Test 2: Health check
Print-Separator
Write-Host "Test 2: GET /health" -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method Get -UseBasicParsing
    Print-Response $response
    
    $data = $response.Content | ConvertFrom-Json
    if ($data.vector_store_count -eq 0) {
        Write-Host "`n⚠️  WARNING: Vector store is empty!" -ForegroundColor Yellow
        Write-Host "Run 'python main.py' to build the knowledge base first." -ForegroundColor Yellow
        exit
    }
    Write-Host "✅ PASSED" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

# Test 3: Statistics
Print-Separator
Write-Host "Test 3: GET /stats" -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/stats" -Method Get -UseBasicParsing
    Print-Response $response
    Write-Host "✅ PASSED" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
}

# Test 4-7: Ask questions
$questions = @(
    "What is Python used for?",
    "How do I install Python?",
    "What are the main features of Python?",
    "How do I create a virtual environment?"
)

$testNumber = 4
foreach ($question in $questions) {
    Print-Separator
    Write-Host "Test $testNumber : POST /ask" -ForegroundColor Green
    Write-Host "Question: $question" -ForegroundColor Cyan
    
    try {
        $body = @{
            question = $question
            top_k = 5
        } | ConvertTo-Json
        
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-WebRequest -Uri "$baseUrl/ask" -Method Post -Body $body -Headers $headers -UseBasicParsing
        Print-Response $response
        
        $data = $response.Content | ConvertFrom-Json
        if ($data.success) {
            Write-Host "`n✅ Answer generated successfully!" -ForegroundColor Green
            Write-Host "Number of sources: $($data.sources.Count)" -ForegroundColor Cyan
        }
        Write-Host "✅ PASSED" -ForegroundColor Green
    } catch {
        Write-Host "❌ FAILED: $_" -ForegroundColor Red
    }
    
    $testNumber++
    Start-Sleep -Seconds 1
}

Print-Separator
Write-Host "`n🎉 Test suite completed!" -ForegroundColor Green
Write-Host "Check the results above for any failures.`n" -ForegroundColor Yellow
