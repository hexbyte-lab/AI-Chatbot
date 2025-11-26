# Bug Fix: Delete Session Not Deleting Messages

## 🐛 Issue Description

**Severity:** 🔴 **HIGH** - Session deletion not working properly

**Problem:** When clicking "Delete Session", only the session record was deleted but all messages remained in the database. This caused:
- Database bloat (orphaned messages)
- Incorrect message counts
- Confusion about what was deleted

---

## 🔍 Root Cause

SQLite has **foreign key constraints DISABLED by default**. Even though the schema defined:

```sql
CREATE TABLE messages (
    ...
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
)
```

The `ON DELETE CASCADE` wasn't working because foreign keys were never enabled!

---

## ✅ The Fix

**File:** `src/storage/database.py`

**Before:**
```python
def _init_database(self):
    """Initialize database schema."""
    self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
    self.connection.row_factory = sqlite3.Row
    
    cursor = self.connection.cursor()  # ❌ Foreign keys not enabled
```

**After:**
```python
def _init_database(self):
    """Initialize database schema."""
    self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
    self.connection.row_factory = sqlite3.Row
    
    # Enable foreign key constraints (required for CASCADE DELETE to work)
    self.connection.execute("PRAGMA foreign_keys = ON")  # ✅ Fixed!
    
    cursor = self.connection.cursor()
```

**One line fix:** Enable foreign keys immediately after connection!

---

## 📊 How It Works Now

### Before Fix:
```sql
-- Delete session
DELETE FROM sessions WHERE id = 1;  
-- ❌ Messages remain orphaned in database!
-- SELECT COUNT(*) FROM messages WHERE session_id = 1;  -- Still returns results
```

### After Fix:
```sql
-- Delete session
DELETE FROM sessions WHERE id = 1;  
-- ✅ CASCADE DELETE automatically removes all messages!
-- SELECT COUNT(*) FROM messages WHERE session_id = 1;  -- Returns 0
```

---

## 🧪 Testing

**To verify the fix:**

1. **Create a session with messages:**
   ```bash
   python app_gradio_persistent.py
   # Send some messages in the chat
   ```

2. **Check database before deletion:**
   ```sql
   sqlite3 data/chatbot.db
   SELECT COUNT(*) FROM messages WHERE session_id = 1;  -- Should show messages
   ```

3. **Delete the session via UI:**
   - Select the session from dropdown
   - Click "🗑️ Delete Session"

4. **Check database after deletion:**
   ```sql
   SELECT COUNT(*) FROM sessions WHERE id = 1;   -- Should be 0
   SELECT COUNT(*) FROM messages WHERE session_id = 1;  -- Should be 0 ✅
   ```

---

## 📈 Impact

### Before Fix:
- ❌ Sessions deleted, but messages remained
- ❌ Database filled with orphaned messages
- ❌ Misleading statistics
- ❌ Wasted disk space

### After Fix:
- ✅ Session AND messages deleted together
- ✅ Clean database
- ✅ Accurate statistics
- ✅ Proper cascade behavior

---

## 🔑 Key Takeaway

**SQLite requires explicit foreign key enablement:**

```python
# ALWAYS do this after opening SQLite connection
connection.execute("PRAGMA foreign_keys = ON")
```

Without this, all foreign key constraints (including CASCADE DELETE) are silently ignored!

---

## 📝 Related Code

The delete session method in `session_manager.py` was already correct:

```python
def delete_session(self, session_id: int) -> bool:
    """Delete a session and all its messages."""
    self.db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    return True
```

It didn't need changes because the CASCADE DELETE now works properly.

---

## ✅ Status

**Fixed!** ✅

- [x] Foreign keys enabled in database connection
- [x] CASCADE DELETE now works
- [x] Sessions and messages deleted together
- [x] No orphaned records
- [x] Clean database behavior

---

**Date:** November 25, 2025  
**Fix:** One line - Enable foreign keys  
**Impact:** Critical - Proper data deletion

