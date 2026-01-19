# 📝 Blog Feature - Quick Start

## Installation (3 Steps)

### Step 1: Install CKEditor Package
```bash
pip install -r requirements.txt
```

### Step 2: Run Migration
```bash
python manage.py migrate
```

### Step 3: Restart Django
```bash
# Stop current server (Ctrl+C)
.\run_server.bat
```

---

## Create Your First Blog Post

1. **Go to Admin**: `http://127.0.0.1:5000/admin/`
2. **Click "Blog Posts"** (in Store section)
3. **Click "+ Add Blog Post"**
4. **Fill in the form**:
   - Title: Your blog post title
   - Excerpt: Short summary
   - Content: Full post (use rich text editor)
   - Featured Image: Optional cover image
   - Published: Check to make live
5. **Click "Save"**

---

## View Your Blog

**List**: `http://127.0.0.1:5000/blog/`  
**Individual Post**: `http://127.0.0.1:5000/blog/your-post-slug/`

---

## Rich Text Editor Features

✅ Bold, Italic, Underline  
✅ Lists (bullets & numbered)  
✅ **Upload images directly**  
✅ Add links  
✅ Create tables  
✅ Source code view  

---

## Navigation

Blog menu is already added to:
- ✅ Navbar (main menu)
- ✅ Footer (footer menu)

---

That's it! You now have a fully functional blog system! 🎉

See `BLOG_FEATURE.md` for detailed documentation.

