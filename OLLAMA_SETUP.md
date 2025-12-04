# Ollama Setup Guide

This guide will help you set up Ollama to use local Llama 3 models for translation.

## What is Ollama?

Ollama is a tool that allows you to run large language models locally on your machine. This means:
- **No API costs**: Translation is completely free after initial setup
- **Privacy**: Documents never leave your machine
- **Offline capability**: Works without internet connection
- **Full control**: You own and control the model

## Prerequisites

- macOS, Linux, or Windows (WSL2)
- At least 8GB of RAM (16GB+ recommended for better performance)
- ~4.7GB of disk space for Llama 3 8B model

## Installation Steps

### 1. Install Ollama

**macOS:**
```bash
# Download and install from https://ollama.ai
# Or use Homebrew:
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download the installer from https://ollama.ai/download/windows

### 2. Start Ollama Service

Once installed, start the Ollama service:

```bash
ollama serve
```

This will start the Ollama API server on `http://localhost:11434`.

**Note**: On macOS, Ollama runs as a background service automatically after installation.

### 3. Download Llama 3 Model

Open a new terminal window and pull the Llama 3 model:

```bash
# Download Llama 3 8B (recommended)
ollama pull llama3

# Or download Llama 3.1 8B (newer version)
ollama pull llama3.1

# Or Llama 3.2 3B (smaller, faster, less accurate)
ollama pull llama3.2
```

The download will take a few minutes depending on your internet speed (~4.7GB for llama3).

### 4. Test the Model

Verify the model is working:

```bash
ollama run llama3
```

You should see a prompt where you can chat with the model. Type something like "Hello!" to test it. Type `/bye` to exit.

### 5. Configure the Translator

Update your `.env` file with Ollama configuration:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

If you downloaded a different model (like `llama3.1` or `llama3.2`), update `OLLAMA_MODEL` accordingly.

## Using Ollama with the Translator

1. Make sure Ollama is running (check with `ollama list`)
2. Start your Flask application
3. In the web interface, select "Local Llama 3 (Ollama)" from the Translation Model dropdown
4. Upload and translate your document as usual

## Performance Expectations

**Speed:**
- On a modern Mac with M1/M2/M3 chip: ~20-50 tokens/second (fast)
- On a CPU without GPU acceleration: ~5-15 tokens/second (slower)
- Translation will be slower than cloud APIs but still practical for most documents

**Quality:**
- Llama 3 provides good quality translations comparable to GPT-3.5
- For best quality, consider using Llama 3 70B if you have sufficient RAM (64GB+)

## Available Models

You can use different Llama models by changing the `OLLAMA_MODEL` environment variable:

| Model | Size | RAM Required | Quality | Speed |
|-------|------|--------------|---------|-------|
| llama3.2 | 3B | 8GB | Good | Fast |
| llama3 | 8B | 8GB | Very Good | Medium |
| llama3.1 | 8B | 8GB | Very Good | Medium |
| llama3:70b | 70B | 64GB+ | Excellent | Slow |

To download a different model:
```bash
ollama pull llama3.1
# or
ollama pull llama3:70b
```

## Troubleshooting

### Ollama connection refused
- Make sure Ollama service is running: `ollama serve`
- Check if it's accessible: `curl http://localhost:11434/api/tags`

### Model not found
- List installed models: `ollama list`
- Pull the model if not installed: `ollama pull llama3`

### Out of memory errors
- Try a smaller model like `llama3.2`
- Close other memory-intensive applications
- Consider using cloud APIs for very large documents

### Slow performance
- Make sure you're using GPU acceleration if available
- Consider using a smaller model (llama3.2)
- For Mac: Ensure you have the Apple Silicon version of Ollama

## Advanced Configuration

### Custom Base URL
If you're running Ollama on a different machine or port:
```bash
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

### Running Ollama as a Service (Linux)
To have Ollama start automatically on boot:
```bash
sudo systemctl enable ollama
sudo systemctl start ollama
```

## Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Ollama Model Library](https://ollama.ai/library)
- [Llama 3 Model Card](https://ollama.ai/library/llama3)

## Cost Comparison

**Cloud APIs (per 1M tokens):**
- OpenAI GPT-4o Mini: ~$0.15 - $0.60
- Anthropic Claude Sonnet: ~$3.00

**Ollama (one-time costs):**
- Free (open source)
- Only cost is electricity and hardware you already own

For heavy usage, Ollama can save significant costs over time.
