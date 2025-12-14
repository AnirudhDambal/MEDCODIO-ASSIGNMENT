# How to Push to Remote Repository

## ✅ Repository Status

Your local repository is initialized and ready to push!

**Current Status**:
- ✅ Git repository initialized
- ✅ Initial commit created
- ✅ .gitignore configured
- ⏳ Ready to add remote and push

## 🚀 Steps to Push

### Step 1: Create Remote Repository

**Option A: GitHub (Recommended)**

1. Go to https://github.com/new
2. Repository name: `MEDCODIO-Assignment` (or your preferred name)
3. Description: "MEDCODIO Assignment - Clinical NLP and Backend System Design"
4. Choose visibility: Public or Private
5. **DO NOT** check:
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
6. Click "Create repository"
7. Copy the repository URL (HTTPS or SSH)

**Option B: GitLab**

1. Go to https://gitlab.com/projects/new
2. Create new project
3. Choose "Create blank project"
4. Copy the repository URL

### Step 2: Add Remote and Push

**Windows PowerShell**:

```powershell
cd "C:\Users\aniru\OneDrive\Desktop\MEDCODIO ASSIGNMENT"

# Add remote (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/MEDCODIO-Assignment.git

# Rename branch to main (if needed)
git branch -M main

# Push to remote
git push -u origin main
```

**Or if using SSH**:

```powershell
git remote add origin git@github.com:YOUR_USERNAME/MEDCODIO-Assignment.git
git branch -M main
git push -u origin main
```

### Step 3: Verify Push

```powershell
# Check remote
git remote -v

# View commit history
git log --oneline

# Check status
git status
```

## 🔐 Authentication

If prompted for credentials:

**GitHub**:
- Use a Personal Access Token (not password)
- Create token: https://github.com/settings/tokens
- Select scope: `repo` (full control)

**GitLab**:
- Use Personal Access Token
- Create token: https://gitlab.com/-/user_settings/personal_access_tokens
- Select scope: `write_repository`

## 📋 Quick Reference

```bash
# Add remote
git remote add origin <repository-url>

# Push
git push -u origin main

# Future pushes (after first time)
git push

# Pull changes
git pull

# Check remotes
git remote -v

# Remove remote (if needed)
git remote remove origin
```

## ⚠️ Important Notes

1. **API Keys**: Make sure sensitive information is in `.gitignore`
2. **Large Files**: Vector database `.pkl` files are excluded (can be regenerated)
3. **Commits**: Review your commit history before pushing
4. **Branch**: Using `main` branch (modern Git default)

## 🆘 Troubleshooting

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin <new-url>
```

### Error: "Authentication failed"
- Use Personal Access Token instead of password
- Check token permissions

### Error: "Large files"
- Ensure `.gitignore` includes `*.pkl`
- Large files should be excluded

### Want to exclude already committed files?
```bash
# Remove from git but keep locally
git rm --cached path/to/file

# Update .gitignore
# Commit the change
git commit -m "Remove large files from tracking"
```

