# Handling Large Content | 处理大内�?

## Problem | 问题

When working with very large Markdown content (>120KB), you might encounter this error:
当处理非常大的Markdown内容�?120KB）时，您可能会遇到此错误�?

```
Input length 164542 exceeds the maximum length 131072
```

## Why This Happens | 为什么会发生这种情况

- **MCP Protocol Limit**: The Model Context Protocol has a built-in limit of ~128KB per request
- **Safety Buffer**: Our system uses 120KB as a safer limit to prevent errors
- **Character Count**: The limit is based on character count, not file size

**MCP协议限制**：模型上下文协议每个请求有约128KB的内置限�?
**安全缓冲**：我们的系统使用120KB作为更安全的限制来防止错�?
**字符计数**：限制基于字符数，而不是文件大�?

## Solutions | 解决方案

### 1. Split Your Content | 分割内容

Break your large Markdown into smaller, logical sections:
将大型Markdown分解为较小的逻辑部分�?

```markdown
# Main Topic - Part 1
## Section A
- Point 1
- Point 2

# Main Topic - Part 2  
## Section B
- Point 3
- Point 4
```

### 2. Reduce Content Density | 减少内容密度

- Remove unnecessary details | 删除不必要的细节
- Use shorter descriptions | 使用更简短的描述
- Focus on key points only | 只关注关键点

### 3. Use Multiple Mind Maps | 使用多个思维导图

Instead of one huge mind map, create several focused ones:
与其创建一个巨大的思维导图，不如创建几个聚焦的�?

- **Overview Map**: High-level structure | 概览图：高级结构
- **Detail Maps**: Specific sections | 详细图：具体部分
- **Process Maps**: Step-by-step flows | 流程图：逐步流程

## Best Practices | 最佳实�?

### Content Organization | 内容组织

```markdown
# Project Overview (Main Map)
## Phase 1
## Phase 2
## Phase 3

# Phase 1 Details (Separate Map)
## Requirements
### Functional
### Non-functional
## Design
### Architecture
### UI/UX
```

### Size Guidelines | 大小指南

- **Optimal Size**: 10-50KB per mind map | 每个思维导图的最佳大小：10-50KB
- **Maximum Safe**: 120KB | 最大安全值：120KB
- **Character Estimate**: ~1000 characters = 1KB | 字符估算：约1000字符 = 1KB

## Checking Content Size | 检查内容大�?

### Method 1: Character Count | 方法1：字符计�?
Most text editors show character count in the status bar.
大多数文本编辑器在状态栏显示字符数�?

### Method 2: File Size | 方法2：文件大�?
```bash
# Windows PowerShell
Get-Item "your-file.md" | Select-Object Length

# Linux/Mac
wc -c your-file.md
```

### Method 3: Online Tools | 方法3：在线工�?
Use online character counters to check your content size.
使用在线字符计数器检查您的内容大小�?

## Error Prevention | 错误预防

The system will now provide helpful error messages:
系统现在将提供有用的错误消息�?

```
Markdown content is too large (max 120KB, current: 164,542 characters). 
Consider splitting into 2 smaller parts or reducing content size.
```

## Example: Splitting Strategy | 示例：分割策�?

**Original Large Content** (160KB):
```markdown
# Complete Company Handbook
## HR Policies (40KB of content)
## Technical Standards (60KB of content) 
## Procedures (60KB of content)
```

**Split into Multiple Maps**:
1. **HR Policies Map** (40KB) �?
2. **Technical Standards Map** (60KB) �? 
3. **Procedures Map** (60KB) �?
4. **Overview Map** (5KB) - Links to all others �?

This approach creates more manageable and focused mind maps!
这种方法创建了更易管理和聚焦的思维导图�?

