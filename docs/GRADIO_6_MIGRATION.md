# Gradio 6.0 Migration Guide

## Breaking Changes Fixed

When upgrading from Gradio 4.x to 6.0.1, the following breaking changes were encountered and fixed:

### 1. **gr.Blocks() API Changes**

**Removed Parameters:**
- ❌ `theme` - No longer accepted in constructor
- ❌ `css` - No longer accepted in constructor

**Before (Gradio 4.x):**
```python
with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="cyan"),
    css=css,
    title="My App"
) as demo:
```

**After (Gradio 6.0+):**
```python
with gr.Blocks(title="My App") as demo:
```

---

### 2. **gr.Chatbot() Component Changes**

**Removed Parameters:**
- ❌ `show_copy_button` - No longer supported
- ❌ `avatar_images` - No longer supported

**Before (Gradio 4.x):**
```python
chatbot = gr.Chatbot(
    label="Chat",
    height=600,
    show_copy_button=True,
    avatar_images=(None, "assets/icon.png")
)
```

**After (Gradio 6.0+):**
```python
chatbot = gr.Chatbot(
    label="Chat",
    height=600
)
```

---

### 3. **Chatbot Data Format Change** ⚠️ CRITICAL

**Old Format (Gradio 4.x):**
```python
# History as list of tuples
history = [
    ("user message", "bot response"),
    ("another message", "another response")
]
```

**New Format (Gradio 6.0+):**
```python
# History as list of message dictionaries
history = [
    {"role": "user", "content": "user message"},
    {"role": "assistant", "content": "bot response"},
    {"role": "user", "content": "another message"},
    {"role": "assistant", "content": "another response"}
]
```

**Required Code Changes:**

1. **Update type hints:**
```python
# Before
history: List[Tuple[str, str]]

# After
history: List[Dict[str, str]]
```

2. **Update message yielding:**
```python
# Before
yield history + [(user_msg, bot_response)]

# After
new_history = history + [{"role": "user", "content": user_msg}]
yield new_history + [{"role": "assistant", "content": bot_response}]
```

3. **Update session loading:**
```python
# Before
for user_msg, bot_msg in loaded_messages:
    chat_history.append((user_msg, bot_msg))

# After
for msg in loaded_messages:
    chat_history.append({"role": msg["role"], "content": msg["content"]})
```

---

### 4. **gr.Dropdown() Validation**

**Issue:** Gradio 6.0 validates dropdown values strictly.

**Before:**
```python
gr.Dropdown(
    choices=[(0, "New Session")],
    value=0  # This causes a warning
)
```

**After:**
```python
gr.Dropdown(
    choices=[],  # Start empty
    value=None,  # Or use a valid choice
    allow_custom_value=True  # Or enable custom values
)
```

---

## Files Modified

### app_gradio.py
- Removed `theme` and `css` from `gr.Blocks()`
- Removed `show_copy_button` and `avatar_images` from `gr.Chatbot()`
- Changed history format from `List[Tuple[str, str]]` to `List[Dict[str, str]]`
- Updated `generate_response()` to yield new format
- Updated `submit_message()` handler

### app_gradio_persistent.py
- All changes from `app_gradio.py` plus:
- Updated `load_session()` to return new format
- Updated session loading logic
- Fixed dropdown initialization

---

## Testing Checklist

- [x] App starts without errors
- [x] Can send messages and receive responses
- [x] Streaming works correctly
- [x] Session loading works
- [x] Clear button works
- [x] Stop button works
- [x] Export functionality works

---

## Additional Notes

### Emoji Characters
On Windows console, emoji characters in log messages may cause `UnicodeEncodeError`. This is a console encoding issue, not a Gradio issue. The app functionality is not affected.

**Solution:** Removed emoji characters from log messages or use `PYTHONIOENCODING=utf-8`.

### Theming
Custom theming in Gradio 6.0 requires a different approach. The old `theme` parameter is gone. To add custom styling:

1. Use component-level styling
2. Use the new theming API (if available in your version)
3. Wait for Gradio documentation updates on theming

---

## References

- Gradio 6.0 Release Notes: https://github.com/gradio-app/gradio/releases
- Gradio Migration Guide: https://www.gradio.app/guides/upgrading

---

## Summary

**Total Changes:** 5 major breaking changes
**Files Modified:** 2 main files
**Impact:** High - Required significant refactoring
**Status:** ✅ All issues resolved

The app now works fully with Gradio 6.0.1!

