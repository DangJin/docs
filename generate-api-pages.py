#!/usr/bin/env python3
"""
根据 OpenAPI 文件自动生成所有 API 端点的文档页面
"""
import json
import os
import re
from pathlib import Path

def sanitize_filename(text):
    """将文本转换为有效的文件名"""
    # 移除特殊字符，替换为连字符
    text = re.sub(r'[^\w\s-]', '', text)
    # 将空格和多个连字符替换为单个连字符
    text = re.sub(r'[-\s]+', '-', text)
    # 移除开头的连字符
    text = text.strip('-')
    return text.lower()

def generate_api_pages(openapi_path, output_dir):
    """从 OpenAPI 文件生成所有端点的 MDX 页面"""
    with open(openapi_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    paths = spec.get('paths', {})
    base_dir = Path.cwd()
    output_path = base_dir / output_dir
    output_path.mkdir(parents=True, exist_ok=True)
    
    generated_files = []
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                continue
            
            # 获取端点的标题和描述
            summary = details.get('summary', '')
            description = details.get('description', '')
            
            # 生成文件名
            # 从路径中提取主要部分，例如 /v1/image-generation -> image-generation
            path_parts = path.strip('/').split('/')
            # 移除版本号（如 v1）
            if path_parts and path_parts[0].startswith('v'):
                path_parts = path_parts[1:]
            
            # 使用路径的最后部分作为文件名基础
            if path_parts:
                base_name = path_parts[-1]
            else:
                base_name = sanitize_filename(summary) if summary else f"{method.lower()}-{path.replace('/', '-')}"
            
            # 如果路径包含多个部分，组合它们
            if len(path_parts) > 1:
                # 例如: query/image-generation
                base_name = '-'.join(path_parts)
            
            filename = sanitize_filename(base_name)
            if not filename:
                filename = f"{method.lower()}-endpoint"
            
            filepath = output_path / f"{filename}.mdx"
            
            # 生成页面内容
            title = summary if summary else f"{method.upper()} {path}"
            
            content = f"""---
title: '{title}'
openapi: '{method.upper()} {path}'
---

"""
            
            if description:
                content += f"{description}\n\n"
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            rel_path = filepath.relative_to(base_dir)
            generated_files.append({
                'file': str(rel_path),
                'title': title,
                'method': method.upper(),
                'path': path
            })
            
            print(f"✓ 已生成: {rel_path} - {title}")
    
    return generated_files

if __name__ == '__main__':
    openapi_file = 'api-reference/openapi.json'
    output_directory = 'api-reference'
    
    print(f"正在从 {openapi_file} 生成 API 文档页面...\n")
    
    files = generate_api_pages(openapi_file, output_directory)
    
    print(f"\n✅ 共生成 {len(files)} 个 API 文档页面")
    print("\n生成的页面列表:")
    for f in files:
        print(f"  - {f['file']} ({f['method']} {f['path']})")
    
    print("\n💡 提示: 请将这些页面添加到 docs.json 的导航配置中")
