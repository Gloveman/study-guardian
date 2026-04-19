import nbformat
import re
from typing import List, Dict, Any

def extract_image_links(text: str) -> List[str]:
    """
    마크다운 문자열 내에서 마크다운 형식 및 HTML 형식의 이미지 링크를 모두 추출합니다.
    """
    # 1. 마크다운 형식: ![alt](url)
    md_images = re.findall(r'!\[.*?\]\((.*?)\)', text)
    # 2. HTML 태그 형식: <img src="url" ...>
    html_images = re.findall(r'<img [^>]*src="([^"]+)"', text)
    
    return list(set(md_images + html_images)) # 중복 제거

def parse_ipynb(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    단일 주피터 노트북(.ipynb)의 바이너리 데이터를 파싱하여 
    핵심 콘텐츠(마크다운, 코드)와 이미지 링크를 추출합니다.
    """
    try:
        # 바이너리 데이터를 UTF-8 문자열로 디코딩하여 노트북 객체로 변환
        nb_str = file_content.decode("utf-8")
        nb = nbformat.reads(nb_str, as_version=4)
        
        parsed_cells = []
        
        for i, cell in enumerate(nb.cells):
            # 셀 본문 (공백 제거)
            source = cell.source.strip()
            if not source:
                continue
                
            cell_info = {
                "cell_index": i,
                "type": cell.cell_type,
                "source": source,
                "images": []
            }
            
            # 마크다운 셀인 경우 이미지 링크 추출
            if cell.cell_type == "markdown":
                cell_info["images"] = extract_image_links(source)
            
            # 코드 셀인 경우 (실행 결과인 outputs는 의도적으로 제외하여 토큰 절약 및 노이즈 제거)
            # 순수 소스 코드만 parsed_cells에 추가
            parsed_cells.append(cell_info)
            
        return {
            "filename": filename,
            "status": "success",
            "total_cells": len(parsed_cells),
            "cells": parsed_cells
        }
        
    except Exception as e:
        return {
            "filename": filename,
            "status": "error",
            "message": str(e)
        }

def parse_multiple_notebooks(files: List[Any]) -> List[Dict[str, Any]]:
    """
    Chainlit 등에서 전달받은 파일 객체 리스트를 통합적으로 파싱합니다.
    """
    combined_results = []
    for file in files:
        # Chainlit 파일 객체는 .content(bytes)와 .name(str) 속성을 가짐
        result = parse_ipynb(file.content, file.name)
        combined_results.append(result)
    return combined_results

# ==========================================
# 로컬 테스트를 위한 실행 블록
# ==========================================
if __name__ == "__main__":
    import os
    
    print("🛡️ StudyGuardian Parser Test Mode")
    print("-" * 40)

    # 실제 테스트를 위해 로컬에 있는 .ipynb 파일을 가상 객체로 시뮬레이션
    class MockFile:
        def __init__(self, path):
            self.name = os.path.basename(path)
            with open(path, "rb") as f:
                self.content = f.read()

    # 현재 폴더에서 .ipynb 파일 찾기
    test_files = [f for f in os.listdir(".") if f.endswith(".ipynb")]
    print(f"🔎 발견된 파일: {test_files}")
    mock_files = [MockFile(f) for f in test_files]
    results = parse_multiple_notebooks(mock_files)
    
    for res in results:
        print(f"\n📦 파일: {res['filename']} (상태: {res['status']})")
        if res['status'] == 'success':
            print(f"   추출된 셀 개수: {res['total_cells']}")

            # 이미지 링크가 있는 셀만 확인
            img_cells = [c for c in res['cells'] if c['images']]
            if img_cells:
                print(f"   발견된 이미지 링크: {img_cells[0]['images']}")
    
    print("-" * 40)
    print("✅ 테스트 종료")