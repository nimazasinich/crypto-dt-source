# CryptoBERT Quick Reference Card

## 🚀 Quick Start (3 Steps)

```bash
# 1. Setup environment
./setup_cryptobert.sh

# 2. Test integration
python3 test_cryptobert.py

# 3. Use in code
python3 -c "import ai_models; ai_models.initialize_models(); print(ai_models.analyze_crypto_sentiment('Bitcoin bullish trend'))"
```

---

## 📋 Model Info

| Item | Value |
|------|-------|
| **Model** | ElKulako/CryptoBERT |
| **ID** | `hf_model_elkulako_cryptobert` |
| **Token** | `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` |
| **Status** | CONDITIONALLY_AVAILABLE |

---

## 💻 Code Snippets

### Initialize Models
```python
import ai_models
result = ai_models.initialize_models()
print(f"CryptoBERT: {result['models']['crypto_sentiment']}")
```

### Analyze Sentiment
```python
sentiment = ai_models.analyze_crypto_sentiment("Bitcoin moon incoming")
print(f"{sentiment['label']}: {sentiment['score']:.2%}")
```

### Get Model Info
```python
info = ai_models.get_model_info()
print(f"Loaded: {info['loaded_models']['crypto_sentiment']}")
```

---

## 🔧 Commands

### Setup
```bash
export HF_TOKEN="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"
./setup_cryptobert.sh
```

### Test
```bash
python3 test_cryptobert.py
```

### Verify
```bash
python3 -c "import config; print(config.HF_USE_AUTH_TOKEN)"
```

---

## 📁 Files Created

```
setup_cryptobert.sh              - Setup script
test_cryptobert.py               - Test suite
docs/CRYPTOBERT_INTEGRATION.md   - Full docs
CRYPTOBERT_SETUP_COMPLETE.md     - Setup guide
INTEGRATION_SUMMARY.md           - Summary
CRYPTOBERT_QUICK_REFERENCE.md    - This file
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Model not loading | `./setup_cryptobert.sh` |
| Auth failure | `echo $HF_TOKEN` |
| Slow inference | Check GPU: `torch.cuda.is_available()` |
| Import error | `pip install transformers torch` |

---

## 📚 Documentation

- **Full Guide**: `docs/CRYPTOBERT_INTEGRATION.md`
- **Summary**: `INTEGRATION_SUMMARY.md`
- **Setup**: `CRYPTOBERT_SETUP_COMPLETE.md`

---

## ✅ Status

```
✓ Configuration: Complete
✓ Authentication: Configured
✓ Integration: Active
✓ Testing: Ready
✓ Documentation: Complete
```

**Next**: Run `python3 test_cryptobert.py` 🎯
