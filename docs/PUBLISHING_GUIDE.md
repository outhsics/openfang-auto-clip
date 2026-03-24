# 发布指南 / Publishing Guide

[English](#english) | 简体中文

---

## 简体中文

### 自动发布流程

OpenFang Auto Clip 使用 GitHub Actions 自动化发布流程。

#### 准备工作

1. **设置 Secrets**
   - `PYPI_API_TOKEN`: PyPI API token
   - `DOCKER_USERNAME`: Docker Hub 用户名
   - `DOCKER_PASSWORD`: Docker Hub 密码

2. **配置 GitHub**
   ```bash
   # 设置 GitHub token
   gh secret set PYPI_API_TOKEN
   gh secret set DOCKER_USERNAME
   gh secret set DOCKER_PASSWORD
   ```

#### 发布步骤

**方法 1: 使用 Git Tag (推荐)**

```bash
# 1. 更新版本
python scripts/release.py bump patch

# 2. 更新 CHANGELOG
python scripts/release.py changelog

# 3. 提交更改
git add .
git commit -m "Release v1.0.0"
git push

# 4. 创建并推送 tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

GitHub Actions 将自动：
- 创建 GitHub Release
- 发布到 PyPI
- 构建 and 推送 Docker 镜像

**方法 2: 使用 Release 脚本**

```bash
# 完整发布流程
python scripts/release.py release
```

#### 验证发布

1. **检查 GitHub Release**
   ```bash
   gh release view v1.0.0
   ```

2. **检查 PyPI**
   ```bash
   pip install openfang-auto-clip==v1.0.0
   ```

3. **检查 Docker**
   ```bash
   docker pull outhsics/openfang-auto-clip:v1.0.0
   ```

### 手动发布

如果自动发布失败，可以手动发布：

#### PyPI

```bash
# 构建包
python -m build

# 发布到 TestPyPI (测试)
twine upload --repository testpypi dist/*

# 发布到 PyPI (生产)
twine upload dist/*
```

#### Docker

```bash
# 构建镜像
docker build -t openfang-auto-cli:latest .

# 标记镜像
docker tag openfang-auto-cli:latest outhsics/openfang-auto-clip:v1.0.0

# 推送镜像
docker push outhsics/openfang-auto-clip:v1.0.0
```

### 发布检查清单

- [ ] 所有测试通过
- [ ] CHANGELOG.md 已更新
- [ ] 版本号已更新
- [ ] README.md 中的功能列表是最新的
- [ ] 文档已更新
- [ ] 没有未提交的更改
- [ ] Git tag 已创建和推送

---

## English

### Automated Release Process

OpenFang Auto Clip uses GitHub Actions for automated releases.

#### Prerequisites

1. **Configure Secrets**
   - `PYPI_API_TOKEN`: PyPI API token
   - `DOCKER_USERNAME`: Docker Hub username
   - `DOCKER_PASSWORD`: Docker Hub password

2. **Setup GitHub**
   ```bash
   # Set secrets
   gh secret set PYPI_API_TOKEN
   gh secret set DOCKER_USERNAME
   gh secret set DOCKER_PASSWORD
   ```

#### Release Steps

**Method 1: Using Git Tags (Recommended)**

```bash
# 1. Bump version
python scripts/release.py bump patch

# 2. Update CHANGELOG
python scripts/release.py changelog

# 3. Commit changes
git add .
git commit -m "Release v1.0.0"
git push

# 4. Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

GitHub Actions will automatically:
- Create GitHub Release
- Publish to PyPI
- Build and push Docker images

**Method 2: Using Release Script**

```bash
# Full release workflow
python scripts/release.py release
```

#### Verify Release

1. **Check GitHub Release**
   ```bash
   gh release view v1.0.0
   ```

2. **Check PyPI**
   ```bash
   pip install openfang-auto-clip==v1.0.0
   ```

3. **Check Docker**
   ```bash
   docker pull outhsics/openfang-auto-clip:v1.0.0
   ```

### Manual Publishing

If automated publishing fails, you can publish manually:

#### PyPI

```bash
# Build package
python -m build

# Publish to TestPyPI (testing)
twine upload --repository testpypi dist/*

# Publish to PyPI (production)
twine upload dist/*
```

#### Docker

```bash
# Build image
docker build -t openfang-auto-cli:latest .

# Tag image
docker tag openfang-auto-cli:latest outhsics/openfang-auto-clip:v1.0.0

# Push image
docker push outhsics/openfang-auto-clip:v1.0.0
```

### Release Checklist

- [ ] All tests pass
- [ ] CHANGELOG.md updated
- [ ] Version number updated
- [ ] Feature list in README is current
- [ ] Documentation updated
- [ ] No uncommitted changes
- [ ] Git tag created and pushed
